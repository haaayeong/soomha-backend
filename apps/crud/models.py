from apps.app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from apps.crud.enums import UserRole

class Level(db.Model):
  __tablename__ = 'level'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  name = db.Column(db.String(50), nullable=False, unique=True)
  required_stamps = db.Column(db.Integer, nullable=False, unique=True)

class User(db.Model):
  __tablename__ = 'users'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  username = db.Column(db.String(50), unique=True, index=True, nullable=False )
  password_hash = db.Column(db.String(255), nullable=False)
  profile_image = db.Column(db.String(255), nullable=False, default='/static/images/default_profile.png')
  nickname = db.Column(db.String(150), nullable=False, unique=True)
  email = db.Column(db.String(100), unique=True, index=True, nullable=False)
  role = db.Column(db.Enum(UserRole), nullable=False)

  kindergarten = db.Column(db.String(100))
  stamp = db.Column(db.Integer, nullable=True, default=0)

  level_id = db.Column(db.Integer, db.ForeignKey('level.id'))
  level = db.relationship('Level', backref=db.backref('users', lazy=True))

  area = db.Column(db.String(100), nullable=False)
  created_at = db.Column(db.DateTime, default=datetime.now)
  updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

  @property
  def password(self):
    raise AttributeError('비밀번호는 접근이 불가능 합니다.')
  
  @password.setter
  def password(self, password):
    self.password_hash = generate_password_hash(password)

  def verify_password(self, password):
    return check_password_hash(self.password_hash, password)
  
  def is_duplicate_username(self):
    return User.query.filter_by(username = self.username).first() is not None
  
  def is_duplicate_nickname(self):
    return User.query.filter_by(nickname = self.nickname).first() is not None
  
  def is_duplicate_email(self):
    return User.query.filter_by(email = self.email).first() is not None
  
