def int_void_convertion(value: str) -> int | None:
    if value == '':
        return None
    elif value.isdigit():
        return int(value)
    else:
        raise RuntimeError("Failed parsing .env")


def void_convertion(value: str) -> str | None:
    if value == '':
        return None
    else:
        return value
