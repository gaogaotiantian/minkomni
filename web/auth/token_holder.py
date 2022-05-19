import secrets


class TokenHolder:
    def __init__(self):
        self.token = self.generate_token()

    def generate_token(self):
        self.token = secrets.token_urlsafe(32)
        return self.token

    def check_token(self, token):
        return token == self.token
