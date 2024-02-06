async def get_avaible_cores_number() -> int | Exception:
    try:
        return 2
    except Exception as e:
        raise e


async def get_ipv4() -> str | Exception:
    try:
        import random
        r = random.randint(1, 999)
        return f"{r}.{r}.{r}.{r}"
    except Exception as e:
        raise e


async def get_ipv6() -> str | Exception:
    try:
        import random
        r = random.randint(1000, 9999)
        return f"{r}::{r}:{r}:{r}:{r}"
    except Exception as e:
        raise e
