import typing as tp
import re
from .patterns import *


__JSON_TYPES = bool | str | dict | list | None | int | float


def correct_brackets(string: str) -> bool:
    cnt = 0
    for c in string:
        if c == '{':
            cnt += 1
        if c == '}':
            cnt -= 1
            if cnt < 0:
                return False
    return cnt == 0


def validate_string(string: str) -> bool:
    string = string.replace('{{', '').replace('}}', '')
    brackets = re.sub('[^{}]', '', string)
    if not correct_brackets(brackets):
        return False

    start_index = None
    cnt = 0
    for i, c in enumerate(string):
        if c == '{':
            if cnt == 0:
                start_index = i + 1
            cnt += 1
        if c == '}':
            cnt -= 1
            if cnt == 0:
                match = string[start_index:i]
                parts = match.split('|')
                if len(parts) == 1:
                    if KEY_PATTERN.fullmatch(match) is None:
                        return False
                    continue
                key, word = parts[0], parts[-1]
                if KEY_PATTERN.fullmatch(key) is None or WORD_PATTERN.fullmatch(word) is None:
                    return False
                seperator = '|'.join(parts[1:-1])
                if not validate_string(seperator):
                    return False

    return True


def __validate_json(obj: __JSON_TYPES) -> list[str]:
    if isinstance(obj, dict):
        return sum([__validate_json(child) for child in obj.values()], start=[])
    if isinstance(obj, list):
        return sum([__validate_json(child) for child in obj], start=[])
    if isinstance(obj, str):
        return [] if validate_string(obj) else [obj]
    return []


def __validate_dict(d: dict[str, list[str]]) -> list[str]:
    if not isinstance(d, dict):
        return ['dictionary type is not json dict']
    errors = []
    for k, v in d.items():
        if not isinstance(k, str):
            errors.append(f'{k} is not string')
        elif not WORD_PATTERN.fullmatch(k):
            errors.append(f'{k} is not matched word pattern')
        if not isinstance(v, list):
            errors.append(f'{k}:{v} is not list')
        else:
            if ENG_PATTERN.fullmatch(k):
                if len(v) != 2:
                    errors.append(f'{k} size is not 2 (eng word)')
                else:
                    for i, item in enumerate(v):
                        if not isinstance(item, str) or not ENG_PATTERN.fullmatch(k):
                            errors.append(f'{k}:{i} is not valid string')
            elif RU_PATTERN.fullmatch(k):
                if len(v) != 3:
                    errors.append(f'{k} size is not 3 (ru word)')
                else:
                    for i, item in enumerate(v):
                        if not isinstance(item, str) or not RU_PATTERN.fullmatch(k):
                            errors.append(f'{k}:{i} is not valid string')
    return errors
