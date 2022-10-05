def optional_dict(**kwargs) -> dict:
    return {key: value for key, value in kwargs.items() if value or value == 0}
