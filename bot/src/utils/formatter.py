import html
import re
from pathlib import Path

import json

from .validators import __validate_json, __validate_dict, validate_string
from .patterns import RU_PATTERN, ENG_PATTERN
from .utils import json_get

OPEN_BRACKET = '<open_curse_bracket>'
CLOSE_BRACKET = '<close_curse_bracket>'

if Path('data/strings.json').exists():
    STRINGS = json.loads(Path('data/strings.json').read_text())
else:
    STRINGS = {}
    print('No strings.json file found')

if Path('data/dictionary.json').exists():
    DICTIONARY = json.loads(Path('data/dictionary.json').read_text())
else:
    DICTIONARY = {}
    print('No dictionary.json file found')

__all__ = ['fformat', 'fill_keys']


def __incline_ru_word(interpretation: list[str], count: int) -> str:
    count = abs(count)
    if 5 <= count <= 19:
        return interpretation[2]
    if count % 10 == 1:
        return interpretation[0]
    if count % 10 in {2, 3, 4}:
        return interpretation[1]
    return interpretation[2]


def __incline_eng_word(interpretation: list[str], count: int) -> str:
    return interpretation[0] if abs(count) == 1 else interpretation[1]


def incline_word(word: str, count: int, *, __dictionary: dict = DICTIONARY) -> str:
    if word not in __dictionary:
        return word
    return (
        __incline_ru_word(__dictionary[word], count) if RU_PATTERN.fullmatch(word)
        else __incline_eng_word(__dictionary[word], count)
    )


def fill_keys(string: str, check_string: bool = True, *, __dictionary: dict = DICTIONARY, **kwargs) -> str:
    if check_string and not validate_string(string):
        return string

    string = string.replace('{{', OPEN_BRACKET)
    string = string[::-1].replace('}}', CLOSE_BRACKET[::-1])[::-1]

    result = ''

    start_index = None
    cnt = 0
    for i, c in enumerate(string):
        if c == '{':
            if cnt == 0:
                start_index = i + 1
            cnt += 1
        if cnt == 0:
            result += c
        if c == '}':
            cnt -= 1
            if cnt == 0:
                match = string[start_index:i]
                parts = match.split('|')
                if len(parts) == 1:
                    result += f'{{{match}}}' if match not in kwargs else str(kwargs[match])
                    continue
                key, word = parts[0], parts[-1]
                seperator = '|'.join(parts[1:-1])
                if key not in kwargs:
                    result += f'{{{key}|'
                    sep = fill_keys(seperator, False, __dictionary=__dictionary, **kwargs)
                    result += sep + ('|' if sep else '')
                    result += f'{word}}}'
                    continue
                value = str(kwargs[key])
                if not re.fullmatch(r'[+-]?\d+', value):
                    continue
                result += value
                result += fill_keys(seperator, False, __dictionary=__dictionary, **kwargs)
                result += incline_word(word, int(value), __dictionary=__dictionary)

    return result.replace(OPEN_BRACKET, '{').replace(CLOSE_BRACKET, '}')


def fformat(string_key: str, *, __strings: dict = STRINGS, __dictionary: dict = DICTIONARY, **kwargs) -> str:
    string = json_get(string_key, __strings)
    if string is None:
        return string_key
    return fill_keys(str(string), check_string=False, __dictionary=__dictionary, **kwargs)


if strings_errors := __validate_json(STRINGS):
    raise ValueError(f'strings.json contains invalid string: "{strings_errors[0]}"')

if dict_errors := __validate_dict(DICTIONARY):
    raise ValueError(f'dictionary.json contains invalid word interpretation: "{dict_errors[0]}"')
