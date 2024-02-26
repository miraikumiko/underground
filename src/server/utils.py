from os import makedirs
from fastapi import UploadFile


async def upload_iso(user_id: int, iso: UploadFile) -> None | Exception:
    try:
        iso_path = f"/var/lib/libvirt/iso/{user_id}"

        makedirs(iso_path, exist_ok=True)

        with open(f"{iso_path}/{iso.filename}", "wb") as file:
            file.write(await iso.read())
    except Exception as e:
        raise e
