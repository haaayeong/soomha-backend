from flask import Blueprint,request,jsonify
from werkzeug.security import generate_password_hash
from apps.crud.models import db, User, Level
from apps.crud.enums import UserRole
from apps.crud.forms import UserForm

bp = Blueprint("crud", __name__, static_folder="static")

@bp.route('/signup', methods=["POST"])
def signup():
  data = request.get_json()

  form = UserForm(data)

  # 폼이 유효한지 확인
  if not form.validate():
    errors = []
    for field, messages in form.errors.items():
      for message in messages:
        errors.append(f"{field}: {message}")
    return jsonify({"error": errors}), 400
    
  # 비밀번호 확인
  if data['password'] != data['confirmPassword']:
    return jsonify({"error": "비밀번호가 일치하지 않습니다."}), 400
  
  # 아이디 중복 확인
  if User.is_duplicate_username(data['username']):
    return jsonify({"error" : "중복된 아이디입니다."}), 400

  # 닉네임 중복 확인
  if User.is_duplicate_username(data['nickname']):
    return jsonify({"error": "중복된 닉네임입니다."}), 400
  
  # 이메일 중복 확인
  if User.is_duplicate_email(data['email']):
    return jsonify({'error': "중복된 이메일입니다."}), 400
  
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