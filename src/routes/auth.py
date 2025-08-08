from flask import Blueprint, request, jsonify, session
import hashlib

auth_bp = Blueprint('auth', __name__)

# Das gehashte Passwort (SHA-256 Hash von "1q2ww2q1Ichgamer12")
HASHED_PASSWORD = hashlib.sha256("1q2ww2q1Ichgamer12".encode()).hexdigest()

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login endpoint"""
    try:
        data = request.get_json()
        
        if not data or 'password' not in data:
            return jsonify({
                'success': False,
                'error': 'Passwort ist erforderlich'
            }), 400
        
        password = data['password']
        
        # Hash des eingegebenen Passworts berechnen
        input_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Passwort überprüfen
        if input_hash == HASHED_PASSWORD:
            session['authenticated'] = True
            return jsonify({
                'success': True,
                'message': 'Login erfolgreich'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Falsches Passwort'
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout endpoint"""
    try:
        session.pop('authenticated', None)
        return jsonify({
            'success': True,
            'message': 'Logout erfolgreich'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/status', methods=['GET'])
def auth_status():
    """Check authentication status"""
    try:
        is_authenticated = session.get('authenticated', False)
        return jsonify({
            'success': True,
            'authenticated': is_authenticated
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def require_auth(f):
    """Decorator to require authentication for routes"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated', False):
            return jsonify({
                'success': False,
                'error': 'Authentifizierung erforderlich'
            }), 401
        return f(*args, **kwargs)
    return decorated_function

