from bcrypt import hashpw, checkpw, gensalt


class Password:
    @classmethod
    def encode(cls, data, encoding="utf-8"):
        return data.encode(encoding)

    @classmethod
    def decode(cls, data, encoding="utf-8"):
        return data.decode(encoding)

    @classmethod
    def create_password_hash(cls, password):
        hashed_password = hashpw(cls.encode(password), gensalt())
        return cls.decode(hashed_password)

    @classmethod
    def verify_password(cls, plain_password, hashed_password):
        return checkpw(cls.encode(plain_password), cls.encode(hashed_password))




