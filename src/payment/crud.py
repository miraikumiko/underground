from src.crud import crud_create, crud_reads, crud_read, crud_update, crud_delete
from src.payment.models import VDS, Promo
from src.payment.schemas import VDSCreate, VDSRead, VDSUpdate, PromoCreate, PromoRead, PromoUpdate


async def crud_create_vds(schema: VDSCreate) -> int:
    vds_id = await crud_create(VDS, schema)

    return vds_id


async def crud_read_vdss() -> list[VDSRead]:
    vdss = await crud_reads(VDS)

    return vdss


async def crud_read_vds(vds_id: int) -> VDSRead:
    vds = await crud_read(VDS, attr1=VDS.id, attr2=vds_id)

    return vds


async def crud_update_vds(schema: VDSUpdate, vds_id: int) -> None:
    await crud_update(VDS, schema, attr1=VDS.id, attr2=vds_id)


async def crud_delete_vds(vds_id: int) -> None:
    await crud_delete(VDS, attr1=VDS.id, attr2=vds_id)


async def crud_create_promo(schema: PromoCreate) -> int:
    promo_id = await crud_create(Promo, schema)

    return promo_id


async def crud_read_promos() -> list[PromoRead]:
    promos = await crud_reads(Promo)

    return promos


async def crud_read_promo(code: str) -> PromoRead:
    promo = await crud_read(Promo, attr1=Promo.code, attr2=code)

    return promo


async def crud_update_promo(schema: PromoUpdate, promo_id: int) -> None:
    await crud_update(Promo, schema, attr1=Promo.id, attr2=promo_id)


async def crud_delete_promo(promo_id: int) -> None:
    await crud_delete(Promo, attr1=Promo.id, attr2=promo_id)
