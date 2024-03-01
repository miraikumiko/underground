from src.crud import (
    crud_create,
    crud_read,
    crud_update,
    crud_delete
)
from src.user.models import User, UserSettings
from src.user.schemas import (
    UserCreate,
    UserRead,
    UserUpdate,
    UserDelete,
    UserSettingsCreate,
    UserSettingsRead,
    UserSettingsUpdate,
    UserSettingsDelete
)
from src.auth.password import get_password_hash


async def crud_create_user(Schema: UserCreate) -> int:
    Schema.hashed_password = get_password_hash(Schema.password)
    id = await crud_create(User, Schema)

    return id


async def crud_read_users() -> list[UserRead]:
    users = await crud_read(User)

    return users


async def crud_read_user(Schema: UserRead) -> UserRead:
    user = await crud_read(Schema)

    return user


async def crud_update_user(Schema: UserUpdate) -> None:
    Schema.hashed_password = get_password_hash(Schema.password)

    await crud_update(User, Schema)


async def crud_delete_user(Schema: UserDelete) -> None:
    await crud_delete(User, Schema)


async def crud_create_user_settings(Schema: UserSettingsCreate) -> int:
    id = await crud_create(UserSettings, Schema)

    return id


async def crud_read_user_settings(Schema: UserSettingsRead) -> UserSettingsRead:
    user_settings = await crud_create(UserSettings, Schema)

    return user_settings


async def crud_update_user_settings(Schema: UserSettingsUpdate) -> None:
    await crud_create(UserSettings, Schema)


async def crud_delete_user_settings(Schema: UserSettingsDelete) -> None:
    await crud_create(UserSettings, Schema)
