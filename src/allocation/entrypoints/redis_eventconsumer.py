import json
import logging
import redis

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from allocation import config
from allocation.domain import commands
from allocation.adapters import orm
from allocation.service_layer import messagebus, unit_of_work

logger = logging.getLogger(__name__)

r = redis.Redis(**config.get_redis_host_and_port())

orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))

def main():
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe("change_batch_quantity")

    logger.info("Listening for Redis messages...")
    for m in pubsub.listen():
        handle_change_batch_quantity(m)

# hexagonal ports & adapters:
# outside json is converted to Command - domain language
# and handed to service layer (message bus)
# core app doesn't care where the command comes from, redis or flask
def handle_change_batch_quantity(m):
    logger.debug("handling %s", m)
    data = json.loads(m["data"])
    cmd = commands.ChangeBatchQuantity(ref=data["ref"], 
                                       qty=data["qty"])
    messagebus.handle(cmd, uow=unit_of_work.SqlAlchemyUnitOfWork(get_session))   

if __name__ == "__main__":
    main()
    