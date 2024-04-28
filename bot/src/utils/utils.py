import re

__JSON_TYPE = bool | str | dict | list | None | int | float
NUMBER_PATTERN = re.compile(r'[-+]?\d+')


def json_get(key: str, obj: __JSON_TYPE, allow_list: bool = False) -> __JSON_TYPE:
    """
        Find object from JSON-value by key seperated with dots (Example: root.sub1.message)
    """

    if not key:
        if allow_list:
            return None if isinstance(obj, dict) else obj
        return None if isinstance(obj, (list, dict)) else obj

    sub_key = key.split('.')[0]
    child_key = key[len(sub_key) + 1:]

    if isinstance(obj, list):
        if sub_key.lower() in ['false', 'true', 'f', 't']:
            return None if len(obj) != 2 else json_get(child_key, obj[sub_key[0].lower() == 't'], allow_list=allow_list)
        if not NUMBER_PATTERN.fullmatch(sub_key):
            return None
        key_index = int(sub_key)
        if abs(key_index) >= len(obj):
            return None
        return json_get(child_key, obj[key_index], allow_list=allow_list)

    if isinstance(obj, dict):
        if sub_key not in obj:
            return None
        return json_get(child_key, obj[sub_key], allow_list=allow_list)

    return None
