from flask import Blueprint

from apps.crud.models import User
from apps.app import db

bp = Blueprint("crud", __name__, static_folder="static")