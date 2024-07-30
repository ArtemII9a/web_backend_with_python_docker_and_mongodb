from dependencies import *
from jwt_process import Encryption

app = Flask(__name__)
CORS(app)

encr = Encryption()

services = json.loads(getenv("BACKEND_SERVICES_MAPPING"))
get_url = f"http://{services['data-provider']}:5001/api/v1/get_data"
update_url = f"http://{services['data-provider']}:5001/api/v1/update_data"


def security(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        security_header: str = request.headers["security"]
        decoded_header = encr.decode(security_header, validate=True)

        if decoded_header:
            return func(*args, **kwargs)
        return {"error": "invalid header"}
    return wrapper


def attach_header(request_url, request_body):
    response = requests.post(url=request_url, json=request_body, headers={"security": encr.app_token})
    return response


def create_session(query):
    session_exp = str(datetime.now() + timedelta(days=30))
    session_id = attach_header(update_url, {"request": "sessions", "query": {},
                                            "data": {"session_exp": session_exp}}).json()["record_id"]

    attach_header(update_url, {"request": "users", "query": query, "data": {"session_id": session_id}})

    user_data = attach_header(get_url, {"request": "users", "query": query}).json()["data"][0]
    return user_data


def update_session(session_id):
    session_exp = str(datetime.now() + timedelta(days=30))
    attach_header(update_url, {"request": "sessions", "query": {"id": session_id}, "data": session_exp})

    user_data = attach_header(get_url, {"request": "users", "query": {"session_id": session_id}}).json()["data"][0]
    return user_data


@app.route('/api/v1/session/start', methods=['POST'])
def session_start():
    payload = request.get_json()

    if payload:
        if payload["tg_auth"]:
            tg_query = {"tg_id": payload["tg_id"]}
            user = attach_header(get_url, {"request": "users", "query": tg_query}).json()

            if user["status"] == "200":
                user_data = create_session(tg_query)
                return json.dumps({"data": user_data, "status": "200"})

            return {"status": "401", "error": "could not find user"}
        
        else:
            user_login = payload["login"]
            user_password = payload["password"]

            if user_login and user_password:
                log_pass_query = {"login": user_login, "password": user_password}
                user_query = {"request": "users", "query": log_pass_query}

                user = attach_header(get_url, user_query).json()

                if user["status"] == "200":
                    user_data = create_session(log_pass_query)
                    return json.dumps({"data": user_data, "status": "200"})

                return {"status": "401", "error": "could not find user"}
            
            return {"status": "401", "error": "wrong username or password"}


@app.route('/api/v1/session/validate', methods=['POST'])
def session_validate():
    payload = request.get_json()
    session_id = payload["session_id"]
    session = attach_header(get_url, {"request": "sessions", "query": {"id": session_id}}).json()

    if session["status"] == "200":
        session_exp = datetime.strptime(session["data"][0]["session_exp"], "%Y-%m-%d %H:%M:%S.%f")

        if session_exp > datetime.now():
            user_data = update_session(session_id)
            if user_data:
                return json.dumps({"data": user_data, "status": "200"})
            return {"error": "User with that session id does not exist", "status": "403"}

        return {"error": "Session is outdated", "status": "401"}

    return {"error": "Session is undefined", "status": "401"}


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8089)
