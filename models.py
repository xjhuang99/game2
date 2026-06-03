# 文件名: models.py
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from extensions import db  # 注意：是从 extensions 导入 db

# --- 数据库模型 ---

class SessionLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_code = db.Column(db.String(10), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    admin_id = db.Column(db.String(50))

class ChatRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_code = db.Column(db.String(10))
    match_id = db.Column(db.String(50))
    sender = db.Column(db.String(50))
    message = db.Column(db.Text)
    scope = db.Column(db.String(10))
    timestamp = db.Column(db.DateTime, default=datetime.now)

class GameResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_code = db.Column(db.String(10))
    match_id = db.Column(db.String(50))
    round_num = db.Column(db.Integer)
    team_a = db.Column(db.String(50))
    team_b = db.Column(db.String(50))
    move_a = db.Column(db.String(10))
    move_b = db.Column(db.String(10))
    score_a = db.Column(db.Float)
    score_b = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.now)

class AdminAccount(db.Model, UserMixin):
    """Registered admin; must verify email before login."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    verify_token = db.Column(db.String(64), unique=True, nullable=True, index=True)
    verify_token_expires = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


# Legacy / env bootstrap admin (not stored in DB)
class AdminUser(UserMixin):
    def __init__(self, id):
        self.id = id