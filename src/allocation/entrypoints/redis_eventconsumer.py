import json
import logging
import redis

from allocation import config, bootstrap
from allocation.domain import commands

logger = logging.getLogger(__name__)

r = redis.Redis(**config.get_redis_host_and_port())

bus = bootstrap.bootstrap()

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
    bus.handle(cmd)   

if __name__ == "__main__":
    main()
    