from enum import Enum

class UserRole(Enum):
  CHILD = "child"
  PARENT = "parent"
  TEACHER = "teacher"
  ADMIN = "admin"