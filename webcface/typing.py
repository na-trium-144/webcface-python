def convertible_to_float(obj) -> bool:
    return hasattr(obj, "__float__")


def is_float_sequence(obj) -> bool:
    try:
        return all(convertible_to_float(x) for x in obj)
    except:
        return False
