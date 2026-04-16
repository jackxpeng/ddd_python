from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from adapters import orm
from adapters.repository import SqlAlchemyRepository
from domain import model
from services import services
import config

orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))

app = Flask(__name__)

@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    session = get_session()
    repo = SqlAlchemyRepository(session)
    
    try:
        batch_ref = services.allocate(
            request.json.get("orderid"),
            request.json.get("sku"),
            request.json.get("qty"),
            repo,
            session
        )
        return jsonify({"batchref": batch_ref}), 201
    except (model.OutOfStock, services.InvalidSku) as e:
        return jsonify({"message": str(e)}), 400

    finally:
        session.close()

if __name__ == "__main__":
    app.run(debug=True)
