import re

PHONE_NUMBER_REGEX = re.compile(r'(((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10})')


def is_phone_number(phone_number: str) -> bool:
    return PHONE_NUMBER_REGEX.fullmatch(phone_number) is not None and len(re.findall('\d', phone_number)) >= 10


def contain_phone_number(text: str) -> bool:
    return len(PHONE_NUMBER_REGEX.findall(text)) > 0 and any ([is_phone_number(phone_number[0]) for phone_number in PHONE_NUMBER_REGEX.findall(text)])
