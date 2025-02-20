import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from dotenv import load_dotenv
import os

def send_verification_email(email):
    load_dotenv()

    # 환경 변수에서 이메일 정보 가져오기
    smtp_server = os.getenv('MAIL_SERVER')  # 기본값 설정
    smtp_port = int(os.getenv('MAIL_PORT'))  # 보통 SSL은 465, TLS는 587
    sender_email = os.getenv('MAIL_USERNAME')
    sender_password = os.getenv('MAIL_PASSWORD')

    if not all([smtp_server, smtp_port, sender_email, sender_password]):
        print("SMTP 설정이 올바르지 않습니다.")
        return None, "SMTP 설정 오류"

    # 6자리 인증번호 생성
    verification_code = random.randint(100000, 999999)

    # 이메일 내용 설정 (UTF-8 인코딩)
    subject = Header("[숨하] 이메일 인증번호", "utf-8").encode()
    body = f"안녕하세요. 숨하입니다.\n인증 번호를 입력하여 이메일 인증을 완료해주세요.\n\n인증 번호: {verification_code}"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'euc-kr'))

    # SMTP 서버와 연결하여 이메일 보내기
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.ehlo()
        server.starttls()
        server.ehlo()

        # SMTP 로그인
        server.login(sender_email, sender_password)

        # 이메일 전송
        server.sendmail(sender_email, email, msg.as_string())
        server.quit()

        return verification_code, None  # 인증번호 반환 (임시 저장)
    except smtplib.SMTPRecipientsRefused:
        return None, "존재하지 않는 이메일 주소입니다."
    except smtplib.SMTPResponseException as e:
        print("SMTP 오류 발생:", e)
        return None, "이메일 전송 실패"
    except Exception as e:
        print("기타 이메일 전송 오류:", e)
        return None, f"이메일 전송 실패: {str(e)}"