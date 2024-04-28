import re

KEY_PATTERN = re.compile(r'[A-Za-z0-9_]+')
WORD_PATTERN = re.compile(r'[а-яА-ЯёЁ: ]+|[a-zA-Z ]+')
RU_PATTERN = re.compile(r'[а-яА-ЯёЁ: ]+')
ENG_PATTERN = re.compile(r'[a-zA-Z ]+')
