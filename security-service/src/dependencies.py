from flask import Flask, request, make_response
import requests
from flask_cors import CORS
from datetime import datetime, timedelta
from attrs import define
import functools
import jwt
import json
from os import getenv
from uuid import uuid4

