from src.crud import crud_create, crud_reads, crud_read, crud_update, crud_delete
from src.user.models import User
from src.user.schemas import UserCreate, UserRead, UserUpdate


async def crud_create_user(schema: UserCreate) -> int:
    user_id = await crud_create(User, schema)

    return user_id


async def crud_read_users() -> list[UserRead]:
    users = await crud_reads(User)

    return users


async def crud_read_user(user_id: int) -> UserRead:
    user = await crud_read(User, attr1=User.id, attr2=user_id)

    return user


async def crud_update_user(schema: UserUpdate, user_id: int) -> None:
    await crud_update(User, schema, attr1=User.id, attr2=user_id)


async def crud_delete_user(user_id: int) -> None:
    await crud_delete(User, attr1=User.id, attr2=user_id)
