def validate_email(email):
    validators = [
            lambda e:'@' in e, 
            lambda e:'.' in e
            ]
    for validator in validators:
        if not validator(email):
            return True
        return False

def validate_password(password):
    validators = [
            lambda x: any(password in ['!','@','#','$','%','&','*'] for password in x),
            lambda x: any(password.isupper() for password in x),
            lambda x: any(password.islower() for password in x),
            lambda x: any(password.isdigit() for password in x),
            lambda x: len(password) >= 10
            ]
    for validator in validators:
        if not validator(password):
            return True
        return False
