import datetime
from src.utils import err_catch
from src.logger import logger
from src.payment.crud import (
    crud_create_payment,
    crud_read_payment,
    crud_update_payment
)
from src.payment.schemas import PaymentCreate
from src.payment.utils import monero_request, usd_to_xmr
from src.server.crud import (
    crud_read_servers,
    crud_update_server,
    crud_create_active_server,
    crud_read_active_server,
    crud_update_active_server,
    crud_read_server_ips
)
from src.server.vps import vps_server_create
from src.server.rpc import (
    rpc_get_avaible_cores_number,
    rpc_get_ipv4,
    rpc_get_ipv6
)


@err_catch
async def payment_request(data: PaymentCreate, amount_usd: int) -> str:
    response = await monero_request("make_integrated_address")

    address = response["result"]["integrated_address"]
    payment_id = response["result"]["payment_id"]

    amount_xmr = await usd_to_xmr(amount_usd)

    response = await monero_request("make_uri", {
        "address": address,
        "amount": amount_xmr
    })

    payment_uri = response["result"]["uri"]

    crud_create_payment({
        "user_id": data.user_id,
        "server_id": data.server_id,
        "active_server_id": data.active_server_id,
        "payment_id": payment_id,
        "amount": amount_xmr,
        "month": data.month
    })

    return payment_uri


@err_catch
async def payment_checkout(txid: str) -> None:
    response = await monero_request("get_transfer_by_txid", {"txid": txid})

    payment_id = response["result"]["transfer"]["payment_id"]
    amount = response["result"]["transfer"]["amount"]

    payment = await crud_read_payment({"payment_id": payment_id})

    if payment is not None:
        if payment.amount == amount:
            await crud_update_payment({"payment_id": payment_id, "active": False})

            if payment.active_server_id is None or payment.active_server_id == 0:
                # Creating active server
                ipv4 = await rpc_get_ipv4()
                ipv6 = await rpc_get_ipv6()
                end_at = datetime.now() + datetime.timedelta(days=30 * payment.month)

                active_server_id = await crud_create_active_server({
                    "user_id": payment.user_id,
                    "server_id": payment.server_id,
                    "ipv4": ipv4,
                    "ipv6": ipv6,
                    "end_at": end_at
                })

                xml = await vps_server_create(active_server_id, payment.server_id)

                await crud_update_active_server({"id": active_server_id, "xml": xml})

                # Checking resource availability
                server_addresses = await crud_read_server_ips()
                node_cores = []

                for ip in server_addresses.ip:
                    avaible_cores = await rpc_get_avaible_cores_number(ip)
                    node_cores += avaible_cores - 1

                servers = await crud_read_servers()

                for server in servers:
                    if max(node_cores) < server.cores:
                        await crud_update_server(server.id, {"avaible": False})

                logger.info(f"Server has been bought by user with id {payment.user_id}")
            else:
                active_server = await crud_read_active_server({"id": payment.active_server_id})
                end_at = active_server.end_at + datetime.timedelta(days=30 * payment.month)
                await crud_update_active_server({"id": active_server.id, "end_at": end_at})

                logger.info(f"Server has been payed by user with id {payment.user_id}")
