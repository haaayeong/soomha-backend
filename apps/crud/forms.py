from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, IntegerField, SelectField
from wtforms.validators import Length, DataRequired, Email, EqualTo, Regexp

class UserForm(FlaskForm):
    username = StringField(
        validators=[
            DataRequired(message="아이디를 입력하세요."),
            Length(min=4, max=20, message="아이디는 4자 이상 20자 이하로 입력하세요."),
            Regexp(
                regex=r"^(?=.*[a-z])(?=.*\d)[a-z\d]+$",
                message="아이디는 소문자와 숫자를 포함해야 합니다."
            )
        ]
    )

    email = StringField(
        validators=[
            DataRequired(message="이메일을 입력하세요."),
            Email(message="올바른 이메일 형식을 입력하세요.")
        ]
    )

    password = PasswordField(
        validators=[
            DataRequired(message="비밀번호를 입력하세요."),
            Length(min=4, max=20, message="비밀번호는 4자 이상 20자 이하로 입력하세요."),
            Regexp(
                regex=r"^(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*./,])[a-z\d!@#$%^&*./,]+$",
                message="비밀번호는 소문자, 숫자, 특수문자를 포함해야 합니다."
            )
        ]
    )

    confirmPassword = PasswordField(
        validators=[
            DataRequired(message="비밀번호 확인을 입력하세요."),
            EqualTo("password", message="비밀번호가 일치하지 않습니다.")
        ]
    )

    nickname = StringField(
        validators=[
            DataRequired(message='닉네임을 입력하세요.')
        ]
    )

    emailCode = IntegerField(
        validators=[
            DataRequired(message="인증번호를 입력하세요.")
        ]
    )

    role = SelectField(
        choices=[
            ('child', '어린이'), 
            ('parent', '학부모'), 
            ('teacher', '선생님')
        ],

        validators=[
            DataRequired(message="가입 유형을 선택하세요.")
        ]
    )