import json
import functools
from flask import Flask, request
from flask_cors import CORS
from database import Database
from process_jwt import Encryption


app = Flask(__name__)
CORS(app)

db_instance = Database()
encr = Encryption()


def security(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        security_header: str = request.headers["security"]
        decoded_header = encr.decode(security_header, validate=True)

        if decoded_header:
            return func(*args, **kwargs)

        return {"error": "invalid header"}

    return wrapper


@app.route('/api/v1/get_data', methods=['POST'])
@security
def get_data():
    raw_data = request.get_json()
    query = raw_data["query"] if "query" in raw_data else {}
    table = raw_data["request"]

    data = db_instance.get_one(table, query)

    if data:
        return json.dumps({"data": data, "status": "200"})

    return {"status": "404"}


@app.route('/api/v1/update_data', methods=['POST'])
@security
def update_data():
    raw_data = request.get_json()
    query = raw_data["query"] if "query" in raw_data else {}
    data = raw_data["data"] if "data" in raw_data else {}
    table = raw_data["request"]

    record_id = db_instance.update_db(table, query, data)

    return json.dumps({"id": record_id, "status": "200"})


@app.route('/api/v1/delete_data', methods=['POST'])
@security
def delete_data():
    raw_data = request.get_json()
    query = raw_data["query"] if "query" in raw_data else {}

    if query == {}:
        return {'status': '400'}

    table = raw_data['request']
    db_instance.clear_all(table, query)
    return {'status': '200'}


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8084)
