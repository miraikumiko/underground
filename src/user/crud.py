from src.crud import (
    crud_create,
    crud_reads,
    crud_read,
    crud_update,
    crud_delete
)
from src.user.models import User, UserSettings
from src.user.schemas import (
    UserCreate,
    UserRead,
    UserUpdate,
    UserSettingsCreate,
    UserSettingsRead,
    UserSettingsUpdate,
)
from src.auth.password import password_helper


async def crud_create_user(schema: UserCreate) -> int:
    try:
        schema.hashed_password = password_helper.hash(schema.password)
        user_id = await crud_create(User, schema)

        return user_id
    except Exception:
        raise Exception("User already exist")


async def crud_read_users() -> list[UserRead]:
    users = await crud_reads(User)

    return users


async def crud_read_user(user_id: int) -> UserRead:
    user = await crud_read(User, attr1=User.id, attr2=user_id)

    return user


async def crud_update_user(schema: UserUpdate, user_id: int) -> None:
    schema.hashed_password = password_helper(schema.password)

    await crud_update(User, schema, attr1=User.id, attr2=user_id)


async def crud_delete_user(user_id: int) -> None:
    await crud_delete(User, attr1=User.id, attr2=user_id)


async def crud_create_user_settings(schema: UserSettingsCreate) -> int:
    user_settings_id = await crud_create(UserSettings, schema)

    return user_settings_id


async def crud_read_user_settings(user_id: int) -> UserSettingsRead:
    user_settings = await crud_read(UserSettings, attr1=UserSettings.user_id, attr2=user_id)

    return user_settings


async def crud_update_user_settings(schema: UserSettingsUpdate, user_id: int) -> None:
    await crud_update(UserSettings, schema, attr1=UserSettings.user_id, attr2=user_id)


async def crud_delete_user_settings(user_id: int) -> None:
    await crud_delete(UserSettings, attr1=UserSettings.user_id, attr2=user_id)
