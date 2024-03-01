from os import makedirs
from fastapi import UploadFile
from src.utils import err_catch


@err_catch
async def upload_iso(user_id: int, iso: UploadFile) -> None:
    iso_path = f"/var/lib/libvirt/iso/{user_id}"

    makedirs(iso_path, exist_ok=True)

    with open(f"{iso_path}/{iso.filename}", "wb") as file:
        file.write(await iso.read())
