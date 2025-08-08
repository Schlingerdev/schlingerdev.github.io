from flask import Blueprint, request, jsonify
from src.models.account import ManusAccount, db
from src.services.manus_service import ManusService
from src.routes.auth import require_auth
from datetime import datetime
import threading

account_bp = Blueprint('account', __name__)

@account_bp.route('/accounts', methods=['GET'])
@require_auth
def get_accounts():
    """Get all accounts with their status"""
    try:
        accounts = ManusAccount.query.all()
        return jsonify({
            'success': True,
            'accounts': [account.to_dict() for account in accounts]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@account_bp.route('/accounts', methods=['POST'])
@require_auth
def add_account():
    """Add a new account"""
    try:
        data = request.get_json()
        
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({
                'success': False,
                'error': 'Email and password are required'
            }), 400
        
        email = data['email']
        password = data['password']
        
        # Check if account already exists
        existing_account = ManusAccount.query.filter_by(email=email).first()
        if existing_account:
            return jsonify({
                'success': False,
                'error': 'Account with this email already exists'
            }), 400
        
        # Create new account
        account = ManusAccount(email=email)
        account.set_password(password)
        account.status = 'inactive'
        
        db.session.add(account)
        db.session.commit()
        
        # Try to login immediately to verify credentials
        def verify_login():
            from src.main import app
            with app.app_context():
                manus_service = ManusService()
                success, session_data, error_msg = manus_service.login(email, password)
                
                if success:
                    account.status = 'active'
                    account.last_login = datetime.utcnow()
                    account.set_session_data(session_data)
                else:
                    account.status = 'error'
                
                db.session.commit()
        
        # Run login verification in background
        thread = threading.Thread(target=verify_login)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'account': account.to_dict(),
            'message': 'Account added successfully. Login verification in progress.'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@account_bp.route('/accounts/<int:account_id>', methods=['DELETE'])
@require_auth
def delete_account(account_id):
    """Delete an account"""
    try:
        account = ManusAccount.query.get(account_id)
        if not account:
            return jsonify({
                'success': False,
                'error': 'Account not found'
            }), 404
        
        db.session.delete(account)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Account deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@account_bp.route('/accounts/sync', methods=['POST'])
@require_auth
def sync_accounts():
    """Manually sync all accounts"""
    try:
        accounts = ManusAccount.query.all()
        
        def sync_account(account):
            from src.main import app
            with app.app_context():
                manus_service = ManusService()
                password = account.get_password()
                
                if not password:
                    account.status = 'error'
                    db.session.commit()
                    return
                
                success, session_data, error_msg = manus_service.refresh_session(
                    account.email, 
                    password, 
                    account.get_session_data()
                )
                
                if success:
                    account.status = 'active'
                    account.last_login = datetime.utcnow()
                    account.set_session_data(session_data)
                else:
                    account.status = 'error'
                
                account.updated_at = datetime.utcnow()
                db.session.commit()
        
        # Sync all accounts in background threads
        threads = []
        for account in accounts:
            thread = threading.Thread(target=sync_account, args=(account,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        return jsonify({
            'success': True,
            'message': f'Synchronization started for {len(accounts)} accounts'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@account_bp.route('/accounts/<int:account_id>/sync', methods=['POST'])
@require_auth
def sync_single_account(account_id):
    """Sync a single account"""
    try:
        account = ManusAccount.query.get(account_id)
        if not account:
            return jsonify({
                'success': False,
                'error': 'Account not found'
            }), 404
        
        def sync_account():
            from src.main import app
            with app.app_context():
                manus_service = ManusService()
                password = account.get_password()
                
                if not password:
                    account.status = 'error'
                    db.session.commit()
                    return
                
                success, session_data, error_msg = manus_service.refresh_session(
                    account.email, 
                    password, 
                    account.get_session_data()
                )
                
                if success:
                    account.status = 'active'
                    account.last_login = datetime.utcnow()
                    account.set_session_data(session_data)
                else:
                    account.status = 'error'
                
                account.updated_at = datetime.utcnow()
                db.session.commit()
        
        # Run sync in background
        thread = threading.Thread(target=sync_account)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Account synchronization started'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

