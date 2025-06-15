from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wallet_address = db.Column(db.String(42), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=True)
    kyc_status = db.Column(db.String(20), default='pending')
    jurisdiction = db.Column(db.String(10), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'wallet_address': self.wallet_address,
            'email': self.email,
            'kyc_status': self.kyc_status,
            'jurisdiction': self.jurisdiction,
            'created_at': self.created_at.isoformat()
        }

class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    asset_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    estimated_value = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    verification_status = db.Column(db.String(20), default='pending')
    token_id = db.Column(db.String(100), nullable=True)
    requirements = db.Column(db.Text, nullable=True)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('assets', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'asset_type': self.asset_type,
            'description': self.description,
            'estimated_value': self.estimated_value,
            'location': self.location,
            'verification_status': self.verification_status,
            'token_id': self.token_id,
            'requirements': json.loads(self.requirements) if self.requirements else {},
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)  # tokenize, transfer, etc.
    transaction_hash = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), default='pending')
    details = db.Column(db.Text, nullable=True)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    asset = db.relationship('Asset', backref=db.backref('transactions', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'transaction_type': self.transaction_type,
            'transaction_hash': self.transaction_hash,
            'status': self.status,
            'details': json.loads(self.details) if self.details else {},
            'created_at': self.created_at.isoformat()
        }