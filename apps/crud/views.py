from flask import Blueprint,request,jsonify
from werkzeug.security import generate_password_hash
from apps.crud.models import db, User

bp = Blueprint("crud", __name__, static_folder="static")