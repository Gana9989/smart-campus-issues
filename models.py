"""Database models."""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db


class User(UserMixin, db.Model):
    """User model for students and admins."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default="student")  # student | admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    issues = db.relationship("Issue", backref="user", lazy="dynamic")

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
        }


class Issue(db.Model):
    """Issue model for campus reports."""
    __tablename__ = "issues"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    image_path = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(30), default="Pending")  # Pending | In Progress | Resolved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "image_path": self.image_path,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "user_id": self.user_id,
            "user_name": self.user.name if self.user else None,
        }
