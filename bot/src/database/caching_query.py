from dogpile.cache.api import NO_VALUE

from sqlalchemy import event
from sqlalchemy.orm import loading, ORMExecuteState, Mapper
from sqlalchemy.orm import Query
from sqlalchemy.orm.interfaces import UserDefinedOption


class ORMCache:
    def __init__(self, regions):
        self.cache_regions = regions
        self._statement_cache = {}
        self._cached_queries = {}

    def listen_on_session(self, session_factory):
        event.listen(session_factory, "do_orm_execute", self._do_orm_execute)

    def listen_on_model(self, model):
        event.listen(model, "after_insert", self._after_insert)
        event.listen(model, "after_update", self._after_update)

    def _after_insert(self, mapper: Mapper, connection, target):
        for table in mapper.tables:
            self._invalidate_table_cache(table.name)

    def _after_update(self, mapper: Mapper, connection, target):
        for table in mapper.tables:
            self._invalidate_table_cache(table.name)

    def _invalidate_table_cache(self, table_name: str):
        print(f"updating cache for {table_name}")
        if table_name not in self._cached_queries:
            self._cached_queries[table_name] = []
        for region, cache_key in self._cached_queries[table_name]:
            dogpile_region = self.cache_regions[region]
            print(f"deleting cache for {region} with key {cache_key}")
            dogpile_region.delete(cache_key)

    def _do_orm_execute(self, orm_context: ORMExecuteState):
        for option in orm_context.user_defined_options:
            if isinstance(option, RelationshipCache):
                option = option._process_orm_context(orm_context)
                if option is None:
                    continue

            if isinstance(option, FromCache):
                dogpile_region = self.cache_regions[option.region]

                our_cache_key = option._generate_cache_key(
                    orm_context.statement, orm_context.parameters or {}, self
                )

                if option.ignore_expiration:
                    cached_value = dogpile_region.get(
                        our_cache_key,
                        expiration_time=option.expiration_time,
                        ignore_expiration=option.ignore_expiration,
                    )
                else:

                    def createfunc():
                        return orm_context.invoke_statement().freeze()

                    cached_value = dogpile_region.get_or_create(
                        our_cache_key,
                        createfunc,
                        expiration_time=option.expiration_time,
                    )

                for mapper in orm_context.all_mappers:
                    for table in mapper.tables:
                        if table.name not in self._cached_queries:
                            self._cached_queries[table.name] = []
                        self._cached_queries[table.name].append((option.region, our_cache_key))

                if cached_value is NO_VALUE:
                    # keyerror?   this is bigger than a keyerror...
                    raise KeyError()

                orm_result = loading.merge_frozen_result(
                    orm_context.session,
                    orm_context.statement,
                    cached_value,
                    load=False,
                )
                return orm_result()

        else:
            return None

    def invalidate(self, statement, parameters, opt):
        """Invalidate the cache value represented by a statement."""

        if isinstance(statement, Query):
            statement = statement.__clause_element__()

        dogpile_region = self.cache_regions[opt.region]

        cache_key = opt._generate_cache_key(statement, parameters, self)

        dogpile_region.delete(cache_key)


class FromCache(UserDefinedOption):
    """Specifies that a Query should load results from a cache."""

    propagate_to_loaders = False

    def __init__(
            self,
            region="default",
            cache_key=None,
            expiration_time=None,
            ignore_expiration=False,
    ):
        """Construct a new FromCache.

        :param region: the cache region.  Should be a
         region configured in the dictionary of dogpile
         regions.

        :param cache_key: optional.  A string cache key
         that will serve as the key to the query.   Use this
         if your query has a huge amount of parameters (such
         as when using in_()) which correspond more simply to
         some other identifier.

        """
        self.region = region
        self.cache_key = cache_key
        self.expiration_time = expiration_time
        self.ignore_expiration = ignore_expiration

    def _generate_cache_key(self, statement, parameters, orm_cache):
        key = self.cache_key or statement._generate_cache_key().to_offline_string(
            orm_cache._statement_cache, statement, parameters
        )
        # print("here's our key...%s" % key)
        return key


class RelationshipCache(FromCache):
    propagate_to_loaders = True

    def __init__(
            self,
            attribute,
            region="default",
            cache_key=None,
            expiration_time=None,
            ignore_expiration=False,
    ):
        """Construct a new RelationshipCache.

        :param attribute: A Class.attribute which
         indicates a particular class relationship() whose
         lazy loader should be pulled from the cache.

        :param region: name of the cache region.

        :param cache_key: optional.  A string cache key
         that will serve as the key to the query, bypassing
         the usual means of forming a key from the Query itself.

        """
        self.region = region
        self.cache_key = cache_key
        self.expiration_time = expiration_time
        self.ignore_expiration = ignore_expiration
        self._relationship_options = {
            (attribute.property.parent.class_, attribute.property.key): self
        }

    def _process_orm_context(self, orm_context):
        current_path = orm_context.loader_strategy_path

        if current_path:
            mapper, prop = current_path[-2:]
            key = prop.key

            for cls in mapper.class_.__mro__:
                if (cls, key) in self._relationship_options:
                    relationship_option = self._relationship_options[
                        (cls, key)
                    ]
                    return relationship_option

    def and_(self, option):
        """Chain another RelationshipCache option to this one.

        While many RelationshipCache objects can be specified on a single
        Query separately, chaining them together allows for a more efficient
        lookup during load.

        """
        self._relationship_options.update(option._relationship_options)
        return self
