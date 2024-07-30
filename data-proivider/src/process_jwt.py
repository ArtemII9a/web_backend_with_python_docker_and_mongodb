import jwt
import json
from os import getenv
from attrs import define


@define(frozen=True)
class Encryption:
    backend_key: str = getenv("BACKEND_NETWORK_KEY")
    service: str = getenv("APP_SERVICE_NAME")
    services: dict = json.loads(getenv("BACKEND_SERVICES_MAPPING"))
    key: str = getenv("APP_TRUSTED_KEY")
    keys: list = getenv("BACKEND_TRUSTED_KEYS").split(";")
    app_token: str = jwt.encode({"service_name": service, "key": key}, backend_key, algorithm="HS256")

    def _validate(self, token):
        if token["service_name"] in self.services.keys() and token["key"] in self.keys:
            return True
        return False

    def decode(self, token_to_decode, validate: bool = False):
        token = jwt.decode(token_to_decode, self.backend_key, algorithms="HS256")
        if validate:
            if not self._validate(token):
                return False
        return token

    def encode(self, payload: dict = None):
        if payload:
            return jwt.encode(f"{payload}", self.backend_key, algorithm="HS256")
        return self.app_token


