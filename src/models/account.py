from src.models.user import db
from datetime import datetime
import base64
import os
import json

# Simple encoding for deployment compatibility
def encode_data(data):
    """Encode data using base64"""
    return base64.b64encode(data.encode()).decode()

def decode_data(encoded_data):
    """Decode base64 encoded data"""
    try:
        return base64.b64decode(encoded_data.encode()).decode()
    except:
        return None

class ManusAccount(db.Model):
    __tablename__ = 'manus_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    encrypted_password = db.Column(db.Text, nullable=False)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='inactive')  # 'active', 'error', 'inactive'
    session_data = db.Column(db.Text)  # JSON string for cookies/tokens
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        """Encode and store password"""
        self.encrypted_password = encode_data(password)
    
    def get_password(self):
        """Decode and return password"""
        return decode_data(self.encrypted_password)
    
    def set_session_data(self, session_dict):
        """Store session data as encoded JSON"""
        if session_dict:
            json_data = json.dumps(session_dict)
            self.session_data = encode_data(json_data)
        else:
            self.session_data = None
    
    def get_session_data(self):
        """Retrieve and decode session data"""
        if not self.session_data:
            return {}
        try:
            decoded_data = decode_data(self.session_data)
            return json.loads(decoded_data) if decoded_data else {}
        except:
            return {}
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<ManusAccount {self.email}>'

