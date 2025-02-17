from flask import Blueprint, request, jsonify
from apps.crud.models import db, User
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta

bp = Blueprint("auth", __name__, static_folder="static")

# 로그인 API
@bp.route('/login', methods=["POST"])
def login():
  data = request.get_json()
  username = data.get("username")
  password = data.get("password")

  if not username or not password:
    return jsonify({"error": "아이디와 비밀번호를 입력하세요."}), 400
  
  user = User.query.filter_by(username=username).first()

  if not user or not check_password_hash(user.password, password):
    return jsonify({"error": "아이디 또는 비밀번호가 올바르지 않습니다."})
  
  # JWT 토큰 생성 (유효기간 3시간)
  access_token = create_access_token(identity=user.id, expires_delta=timedelta(hours=3))

  return jsonify({"message": "로그인 성공", "token": access_token}), 200