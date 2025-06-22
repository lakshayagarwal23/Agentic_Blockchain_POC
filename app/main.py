import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import json
import logging
from datetime import datetime

from app.models.database import db, User, Asset, Transaction

from app.agents.nlp_agent import NLPAgent

from app.agents.verification_agent import VerificationAgent
from app.agents.tokenization_agent import TokenizationAgent

from flask import Flask


app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rwa_tokenization.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



# Initialize extensions
db.init_app(app)
CORS(app)

# Initialize agents
nlp_agent = NLPAgent()
verification_agent = VerificationAgent()
tokenization_agent = TokenizationAgent()

# Configure logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create tables
with app.app_context():
    db.create_all()

# Simple root route
@app.route('/')
def home():
    return render_template('index.html')

# ✅ Basic Health Check for system_test.sh compatibility
@app.route('/health')
def health_check_basic():
    return jsonify(status="ok"), 200

# Detailed Health Check
@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

# Asset Intake Route
@app.route('/api/intake', methods=['POST'])
def asset_intake():
    try:
        data = request.get_json()

        if not data or 'user_input' not in data or 'wallet_address' not in data:
            return jsonify({'error': 'Missing required fields: user_input, wallet_address'}), 400

        user_input = data['user_input']
        wallet_address = data['wallet_address']
        logger.info(f"Processing intake for wallet: {wallet_address}")

        parsed_data = nlp_agent.parse_user_input(user_input)

        user = User.query.filter_by(wallet_address=wallet_address).first()
        if not user:
            user = User(
                wallet_address=wallet_address,
                email=data.get('email'),
                jurisdiction=parsed_data.get('location', '').split(',')[-1].strip()[:2]
            )
            db.session.add(user)
            db.session.commit()

        asset = Asset(
            user_id=user.id,
            asset_type=parsed_data.get('asset_type', 'unknown'),
            description=parsed_data.get('description', user_input),
            estimated_value=parsed_data.get('estimated_value', 0),
            location=parsed_data.get('location', 'Unknown'),
            requirements=json.dumps({
                'confidence_score': parsed_data.get('confidence_score', 0),
                'sentiment': parsed_data.get('sentiment', {}),
                'entities': parsed_data.get('entities', [])
            })
        )
        db.session.add(asset)
        db.session.commit()

        follow_up_questions = nlp_agent.generate_follow_up_questions(parsed_data)

        return jsonify({
            'success': True,
            'asset': asset.to_dict(),
            'parsed_data': parsed_data,
            'follow_up_questions': follow_up_questions,
            'next_steps': [
                'Review asset information',
                'Proceed with verification',
                'Submit for tokenization'
            ]
        })

    except Exception as e:
        logger.error(f"Asset intake failed: {str(e)}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/verify/<int:asset_id>', methods=['POST'])
def verify_asset(asset_id):
    try:
        asset = Asset.query.get_or_404(asset_id)
        logger.info(f"Verifying asset: {asset_id}")

        asset_data = asset.to_dict()
        verification_result = verification_agent.verify_asset(asset_data)

        asset.verification_status = verification_result['status']
        asset.updated_at = datetime.utcnow()
        db.session.commit()

        transaction = Transaction(
            asset_id=asset.id,
            transaction_type='verification',
            status=verification_result['status'],
            details=json.dumps(verification_result)
        )
        db.session.add(transaction)
        db.session.commit()

        return jsonify({
            'success': True,
            'verification_result': verification_result,
            'asset': asset.to_dict()
        })

    except Exception as e:
        logger.error(f"Verification failed: {str(e)}")
        return jsonify({'error': 'Verification failed', 'details': str(e)}), 500

@app.route('/api/tokenize/<int:asset_id>', methods=['POST'])
def tokenize_asset(asset_id):
    try:
        asset = Asset.query.get_or_404(asset_id)

        if asset.verification_status != 'verified':
            return jsonify({'error': 'Asset must be verified before tokenization'}), 400

        asset_data = asset.to_dict()

        last_verification = Transaction.query.filter_by(
            asset_id=asset_id,
            transaction_type='verification'
        ).order_by(Transaction.created_at.desc()).first()

        verification_result = json.loads(last_verification.details) if last_verification else {'status': 'verified'}
        tokenization_result = tokenization_agent.tokenize_asset(asset_data, verification_result)

        if tokenization_result.get('success'):
            asset.token_id = tokenization_result['token_id']
            asset.updated_at = datetime.utcnow()
            db.session.commit()

            transaction = Transaction(
                asset_id=asset.id,
                transaction_type='tokenization',
                transaction_hash=tokenization_result['transaction_hash'],
                status='completed',
                details=json.dumps(tokenization_result)
            )
            db.session.add(transaction)
            db.session.commit()

            return jsonify({
                'success': True,
                'tokenization_result': tokenization_result,
                'asset': asset.to_dict()
            })
        else:
            return jsonify(tokenization_result), 400

    except Exception as e:
        logger.error(f"Tokenization failed: {str(e)}")
        return jsonify({'error': 'Tokenization failed', 'details': str(e)}), 500

@app.route('/api/asset/<int:asset_id>')
def get_asset(asset_id):
    try:
        asset = Asset.query.get_or_404(asset_id)
        transactions = Transaction.query.filter_by(asset_id=asset_id).order_by(Transaction.created_at.desc()).all()
        return jsonify({
            'asset': asset.to_dict(),
            'transactions': [tx.to_dict() for tx in transactions]
        })

    except Exception as e:
        logger.error(f"Get asset failed: {str(e)}")
        return jsonify({'error': 'Asset not found', 'details': str(e)}), 404

@app.route('/api/assets/<wallet_address>')
def get_user_assets(wallet_address):
    try:
        user = User.query.filter_by(wallet_address=wallet_address).first()
        if not user:
            return jsonify({'assets': []})

        assets = Asset.query.filter_by(user_id=user.id).order_by(Asset.created_at.desc()).all()

        return jsonify({
            'user': user.to_dict(),
            'assets': [asset.to_dict() for asset in assets]
        })

    except Exception as e:
        logger.error(f"Get user assets failed: {str(e)}")
        return jsonify({'error': 'Failed to retrieve assets', 'details': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    try:
        total_assets = Asset.query.count()
        total_users = User.query.count()
        verified_assets = Asset.query.filter_by(verification_status='verified').count()
        tokenized_assets = Asset.query.filter(Asset.token_id.isnot(None)).count()

        return jsonify({
            'total_assets': total_assets,
            'total_users': total_users,
            'verified_assets': verified_assets,
            'tokenized_assets': tokenized_assets,
            'verification_rate': (verified_assets / total_assets * 100) if total_assets > 0 else 0,
            'tokenization_rate': (tokenized_assets / verified_assets * 100) if verified_assets > 0 else 0
        })

    except Exception as e:
        logger.error(f"Stats failed: {str(e)}")
        return jsonify({'error': 'Failed to retrieve stats', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
