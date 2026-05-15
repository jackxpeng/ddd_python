from datetime import datetime
from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from allocation.adapters import orm
from allocation.service_layer.unit_of_work import SqlAlchemyUnitOfWork
from allocation.service_layer import handlers, messagebus
import allocation.config as config
from allocation.domain import events

orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))

app = Flask(__name__)


@app.route("/add_batch", methods=["POST"])
def add_batch():
    eta = request.json["eta"]
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()
    event = events.BatchCreated(
        request.json["ref"], request.json["sku"], request.json["qty"], eta
    )
    uow = SqlAlchemyUnitOfWork(get_session)
    messagebus.handle(event, uow)
    return "OK", 201


@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    event = events.AllocationRequired(
        request.json.get("orderid"), request.json.get("sku"), request.json.get("qty")
    )
    uow = SqlAlchemyUnitOfWork(get_session)
    results = messagebus.handle(event, uow)
    batch_ref = results[0]
    return jsonify({"batchref": batch_ref}), 201


@app.errorhandler(handlers.InvalidSku)
def handle_invalid_sku(e):
    return jsonify({"message": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)
