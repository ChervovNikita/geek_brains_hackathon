import re
import dotenv
import os
from enum import Enum
from datetime import timedelta
from pathlib import Path

from sqlalchemy import URL


class Environment(Enum):
    DEVELOPMENT = "DEV"
    TEST = "TEST"
    PRODUCTION = "PROD"


ENVIRONMENT = Environment(os.environ.get('ENVIRONMENT', Environment.DEVELOPMENT.value))
DEBUG = ENVIRONMENT == Environment.DEVELOPMENT
DEBUG_SQL = ENVIRONMENT == Environment.DEVELOPMENT

dotenv.load_dotenv(dotenv_path='.env')

TOKEN = os.environ.get('TOKEN')

DATABASE_URL = URL.create(
    'postgresql+psycopg2',
    username=os.environ.get('POSTGRES_USER'),
    password=os.environ.get('POSTGRES_PASSWORD'),
    host=os.environ.get('POSTGRES_HOST'),
    port=os.environ.get('POSTGRES_PORT'),
    database=os.environ.get('POSTGRES_DATABASE')
)

REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')

CACHE_TTL = 60

CORRECT_THRESHOLD = 0.85
