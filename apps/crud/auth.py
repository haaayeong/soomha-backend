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

  if not user or not user.verify_password(password):
    return jsonify({"error": "아이디 또는 비밀번호가 올바르지 않습니다."})
  
  # JWT 토큰 생성 (유효기간 3시간)
  access_token = create_access_token(identity=user.id, expires_delta=timedelta(hours=3))

  return jsonify({"message": "로그인 성공", "token": access_token}), 200

# 로그인한 사용자 정보 조회
@bp.route("/user", methods=["GET"])
@jwt_required()
def get_user():
  user_id = get_jwt_identity()
  user = User.query.get(user_id)

  if not user:
    return jsonify({"error": "사용자를 찾을 수 없습니다."}), 404
  
  return jsonify({
    "id": user.id,
    "username": user.username,
    "profile_image": user.profile_image,
    "nickname": user.nickname,
    "email" : user.email,
    "kindergarten" : user.kindergarten,
    "stamp" : user.stamp,
    "level_id" : user.level_id,
    "area" : user.area
  }), 200