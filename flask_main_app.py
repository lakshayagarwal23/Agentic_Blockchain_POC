from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import json
import logging
from datetime import datetime
from database_models import db, User, Asset, Transaction
from agents.nlp_agent import NLPAgent
from agents.verification_agent import VerificationAgent
from agents.tokenization_agent import TokenizationAgent

# Initialize Flask app
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

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/intake', methods=['POST'])
def asset_intake():
    """Asset intake endpoint"""
    try:
        data = request.get_json()
        
        if not data or 'user_input' not in data or 'wallet_address' not in data:
            return jsonify({
                'error': 'Missing required fields: user_input, wallet_address'
            }), 400
        
        user_input = data['user_input']
        wallet_address = data['wallet_address']
        
        logger.info(f"Processing intake for wallet: {wallet_address}")
        
        # Parse user input using NLP
        parsed_data = nlp_agent.parse_user_input(user_input)
        
        # Create or get user
        user = User.query.filter_by(wallet_address=wallet_address).first()
        if not user:
            user = User(
                wallet_address=wallet_address,
                email=data.get('email'),
                jurisdiction=parsed_data.get('location', '').split(',')[-1].strip()[:2]
            )
            db.session.add(user)
            db.session.commit()
        
        # Create asset record
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
        
        # Generate follow-up questions
        follow_up_questions = nlp_agent.generate_follow_up_questions(parsed_data)
        
        response = {
            'success': True,
            'asset': asset.to_dict(),
            'parsed_data': parsed_data,
            'follow_up_questions': follow_up_questions,
            'next_steps': [
                'Review asset information',
                'Proceed with verification',
                'Submit for tokenization'
            ]
        }
        
        logger.info(f"Asset created successfully: {asset.id}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in asset intake: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

@app.route('/api/verify/<int:asset_id>', methods=['POST'])
def verify_asset(asset_id):
    """Asset verification endpoint"""
    try:
        asset = Asset.query.get_or_404(asset_id)
        logger.info(f"Starting verification for asset: {asset_id}")
        
        # Prepare asset data for verification
        asset_data = {
            'id': asset.id,
            'asset_type': asset.asset_type,
            'description': asset.description,
            'estimated_value': asset.estimated_value,
            'location': asset.location,
            'user_id': asset.user_id
        }
        
        # Perform verification
        verification_result = verification_agent.verify_asset(asset_data)
        
        # Update asset status
        asset.verification_status = verification_result['status']
        asset.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Create transaction record
        transaction = Transaction(
            asset_id=asset.id,
            transaction_type='verification',
            status=verification_result['status'],
            details=json.dumps(verification_result)
        )
        db.session.add(transaction)
        db.session.commit()
        
        logger.info(f"Verification completed for asset {asset_id}: {verification_result['status']}")
        
        return jsonify({
            'success': True,
            'verification_result': verification_result,
            'asset': asset.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error in asset verification: {str(e)}")
        return jsonify({
            'error': 'Verification failed',
            'details': str(e)
        }), 500

@app.route('/api/tokenize/<int:asset_id>', methods=['POST'])
def tokenize_asset(asset_id):
    """Asset tokenization endpoint"""
    try:
        asset = Asset.query.get_or_404(asset_id)
        
        if asset.verification_status != 'verified':
            return jsonify({
                'error': 'Asset must be verified before tokenization'
            }), 400
        
        logger.info(f"Starting tokenization for asset: {asset_id}")
        
        # Prepare asset data
        asset_data = asset.to_dict()
        
        # Get verification result
        last_verification = Transaction.query.filter_by(
            asset_id=asset_id,
            transaction_type='verification'
        ).order_by(Transaction.created_at.desc()).first()
        
        verification_result = {'status': 'verified'}
        if last_verification:
            verification_result = json.loads(last_verification.details)
        
        # Perform tokenization
        tokenization_result = tokenization_agent.tokenize_asset(asset_data, verification_result)
        
        if tokenization_result['success']:
            # Update asset with token information
            asset.token_id = tokenization_result['token_id']
            asset.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Create transaction record
            transaction = Transaction(
                asset_id=asset.id,
                transaction_type='tokenization',
                transaction_hash=tokenization_result['transaction_hash'],
                status='completed',
                details=json.dumps(tokenization_result)
            )
            db.session.add(transaction)
            db.session.commit()
            
            logger.info(f"Tokenization completed for asset {asset_id}")
            
            return jsonify({
                'success': True,
                'tokenization_result': tokenization_result,
                'asset': asset.to_dict()
            })
        else:
            return jsonify(tokenization_result), 400
            
    except Exception as e:
        logger.error(f"Error in asset tokenization: {str(e)}")
        return jsonify({
            'error': 'Tokenization failed',
            'details': str(e)
        }), 500

@app.route('/api/asset/<int:asset_id>')
def get_asset(asset_id):
    """Get asset details"""
    try:
        asset = Asset.query.get_or_404(asset_id)
        transactions = Transaction.query.filter_by(asset_id=asset_id).order_by(Transaction.created_at.desc()).all()
        
        return jsonify({
            'asset': asset.to_dict(),
            'transactions': [tx.to_dict() for tx in transactions]
        })
        
    except Exception as e:
        logger.error(f"Error retrieving asset: {str(e)}")
        return jsonify({
            'error': 'Asset not found',
            'details': str(e)
        }), 404

@app.route('/api/assets/<wallet_address>')
def get_user_assets(wallet_address):
    """Get all assets for a user"""
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
        logger.error(f"Error retrieving user assets: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve assets',
            'details': str(e)
        }), 500

@app.route('/api/stats')
def get_stats():
    """Get system statistics"""
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
        logger.error(f"Error retrieving stats: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve statistics',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    # Ensure logs directory exists
    os.makedirs('logs', exist_ok=True)
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)