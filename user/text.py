def email_text(domain, uidb64, token):
    return f"안녕하세요. 암호화폐 거래소 코인원입니다.고객님, 아래 버튼을 클릭하여 이메일을 인증을 완료해주세요. http://{domain}/account/activate/{uidb64}/{token}"
