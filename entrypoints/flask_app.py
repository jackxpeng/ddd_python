from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from adapters import orm
from service_layer.uow import SqlAlchemyUnitOfWork
from domain import model
from service_layer import services
import config

orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))

app = Flask(__name__)

@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    with SqlAlchemyUnitOfWork(get_session) as uow:
        try:
            batch_ref = services.allocate(
                request.json.get("orderid"),
                request.json.get("sku"),
                request.json.get("qty"),
                uow 
            )
            return jsonify({"batchref": batch_ref}), 201
        except (model.OutOfStock, services.InvalidSku) as e:
            return jsonify({"message": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)
