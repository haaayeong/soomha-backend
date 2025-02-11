from flask import Blueprint,request,jsonify
from werkzeug.security import generate_password_hash
from apps.crud.models import db, User, Level
from apps.crud.enums import UserRole

bp = Blueprint("crud", __name__, static_folder="static")

@bp.route('/signup', methods=["POST"])
def signup():
  data = request.get_json()

  # 회원가입 중 필수값 확인
  required_fields = ['username', 'password', 'confirmPassword', 'nickname', 'email', 'emailCode', 'role', 'area']
  for field in required_fields:
    if field not in data or not data[field]:
      return jsonify({"error" : f"{field}는 필수입니다."}), 400
    
  # 비밀번호 확인
  if data['password'] != data['confirmPassword']:
    return jsonify({"error": "비밀번호가 일치하지 않습니다."}), 400
  
  # 아이디 중복 확인
  existing_user = User.query.filter(username=data['username']).first()
  if existing_user:
    return jsonify({"error" : "중복된 아이디입니다."}), 400

  # 닉네임 중복 확인
  existing_nickname = User.query.filter_by(nickname=data['nickname']).first()
  if existing_nickname:
    return jsonify({"error": "중복된 닉네임입니다."}), 400
  
  # 기본 역할 설정
  if data['role'] not in [role.name for role in UserRole]:
    return jsonify({"error": "유효하지 않은 가입유형입니다."}), 400
  
  # 선생님일 경우 유치원 이름 확인
  if data['role'] == "teacher" and not data.get('kindergarten'):
    return jsonify({"error" : "소속 유치원 이름을 작성해주세요"})
  
  # 레벨 정보 가져오기 (기본 레벨 설정)
  level = Level.query.filter_by(name="어린이").first()

  # User 객체 생성
  new_user = User(
    username=data['username'],
    password_hash=data['password'],
    nickname=data['nickname'],
    email=data['email'],
    role=data['role'],
    kindergarten=data.get('kindergarten'),
    level_id=level.id if level else None,
    area=data['area']
  )

  # DB에 저장
  db.session.add(new_user)
  db.session.commit()

  return jsonify({"message": "사용자 정보가 잘 저장되었습니다."}), 201