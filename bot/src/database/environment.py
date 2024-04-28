from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import declarative_base

from dogpile.cache.region import CacheRegion, make_region

from src import configs

from . import caching_query

default_region: CacheRegion = make_region().configure(
    'dogpile.cache.redis',
    expiration_time=configs.CACHE_TTL - 1,
    arguments={
        'host': configs.REDIS_HOST,
        'port': configs.REDIS_PORT,
        'db': 1,
        'redis_expiration_time': configs.CACHE_TTL
    }
)

regions = {
    'default': default_region
}
root = "./dogpile_data/"

Base = declarative_base()

engine = create_engine(configs.DATABASE_URL, echo=configs.DEBUG_SQL)
SessionMaker = sessionmaker(bind=engine)

cache = caching_query.ORMCache(regions)
cache.listen_on_session(Session)
