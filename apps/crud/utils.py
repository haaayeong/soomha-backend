import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

def send_verification_eamil(to_email):
  load_dotenv()

  # 환경 변수에서 이메일 정보 가져오기
  smtp_server = os.getenv('MAIL_SERVER')
  smtp_port = os.getenv('MAIL_PORT')
  sender_email = os.getenv('MAIL_USERNAME')
  sender_password = os.getenv('MAIL_PASSWORD')

  # 6자리 인증번호 생성
  verification_code = random.randint(100000, 999999)

  # 이메일 내용 설정
  subject = '[숨하] 이메일 인증번호'
  body = f"안녕하세요. 숨하입니다. \n인증 번호를 입력하여 이메일 인증을 완료해주세요. \n인증 번호 : {verification_code}"

  msg = MIMEMultipart()
  msg['From'] = sender_email
  msg['To'] = to_email
  msg['Subject'] = subject
  msg.attach(MIMEText(body, 'plain'))

  # SMTP 서버와 연결하여 이메일 보내기
  try:
      server = smtplib.SMTP(smtp_server, smtp_port)
      server.starttls()  # TLS 연결 보안 활성화
      server.login(sender_email, sender_password)
      server.sendmail(sender_email, to_email, msg.as_string())
      server.quit()

      # 인증번호 반환 (임시 저장)
      return verification_code
  except Exception as e:
      print(f"이메일 전송 실패: {e}")
      return None