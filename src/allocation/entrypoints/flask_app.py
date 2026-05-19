from datetime import datetime
from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from allocation import bootstrap, views
from allocation.domain import commands
from allocation.service_layer import handlers, unit_of_work

bus = bootstrap.bootstrap()

app = Flask(__name__)


@app.route("/add_batch", methods=["POST"])
def add_batch():
    eta = request.json["eta"]
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()
    command = commands.CreateBatch(
        request.json["ref"], request.json["sku"], request.json["qty"], eta
    )
    bus.handle(command)
    return "OK", 201


@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    command = commands.Allocate(
        request.json.get("orderid"), request.json.get("sku"), request.json.get("qty")
    )
    bus.handle(command)
    return "OK", 202

@app.route("/allocations/<order_id>", methods=["GET"])
def allocations_view_endpoint(order_id):
    session = unit_of_work.get_session()
    try:
        result = views.allocations(order_id, session)
    finally:
        session.close()
        
    if not result:
        return "not found", 404
    return jsonify(result), 200

@app.errorhandler(handlers.InvalidSku)
def handle_invalid_sku(e):
    return jsonify({"message": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)
