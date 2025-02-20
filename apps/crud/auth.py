from flask import Blueprint, request, jsonify
from apps.crud.models import db, User
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

  if user is None:
    return jsonify({"error": "아이디가 존재하지 않습니다."}), 404
  
  if not user.verify_password(password):
     return jsonify({"error": "아이디 또는 비밀번호가 올바르지 않습니다."})
  
  # JWT 토큰 생성 (유효기간 3시간)
  access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(hours=3))

  return jsonify({"message": "로그인 성공", "token": access_token}), 200

# 로그인한 사용자 정보 조회
@bp.route("/user", methods=["GET"])
@jwt_required()
def get_user():
  try:
      user_id = get_jwt_identity()

      if not user_id:
          return jsonify({"error": "유효하지 않은 토큰"}), 401

      user = User.query.get(user_id)
      print("user:", user)

      if not user:
          return jsonify({"error": "사용자를 찾을 수 없습니다."}), 404

      return jsonify({
          "id": user.id,
          "username": user.username,
          "profile_image": user.profile_image,
          "nickname": user.nickname,
          "role": user.role.name,
          "email": user.email,
          "stamp": user.stamp,
          "level": user.level.name if user.role.name == "CHILD" else None,
          "area": user.area
      }), 200
  except Exception as e:
      print("🚨 오류 발생:", str(e))  # 콘솔에서 오류 확인 가능
      return jsonify({"error": str(e)}), 500
  
@bp.route('/update-user', methods=["PUT"])
@jwt_required()
def update_user():
   try:
      user_id = get_jwt_identity()
      user = User.query.get(user_id)

      if not user:
         return jsonify({"error": "사용자를 찾을 수 없습니다."}), 404
      
      data = request.get_json()
      user.nickname = data.get('nickname', user.nickname)
      user.email = data.get('email', user.email)
      user.kindergarten = data.get('kindergarten', user.kindergarten)
      user.area = data.get('area', user.area)

      db.session.commit()

      return jsonify({
          "id": user.id,
          "username": user.username,
          "profile_image": user.profile_image,
          "nickname": user.nickname,
          "role": user.role.name,
          "email": user.email,
          "stamp": user.stamp,
          "level": user.level.name,
          "area": user.area
      }), 200
   except Exception as e:
      return jsonify({"error": str(e)}), 500
   
@bp.route('/delete-account', methods=["DELETE"])
@jwt_required()
def delete_account():
   try:
      user_id = get_jwt_identity()
      user = User.query.get(user_id)

      if not user:
         return jsonify({"error": "사용자를 찾을 수 없습니다."}), 404
      
      db.session.delete(user)
      db.session.commit()

      return jsonify({"message": "탈퇴 성공"}), 200
   except Exception as e:
      return jsonify({"error": str(e)}), 500