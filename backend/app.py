from flask import Flask, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from datetime import datetime, timedelta
import jwt
from functools import wraps
import secrets

# Initialize Flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Enable CORS for frontend communication
CORS(app, supports_credentials=True)

# Configuration
DATABASE_PATH = os.getenv('DATABASE_PATH', 'users.db')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', 'your-google-client-id')
JWT_SECRET = os.getenv('JWT_SECRET', secrets.token_hex(32))

# SQLite database setup
def init_db():
    """Initialize the SQLite database with users table"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT,
            name TEXT NOT NULL,
            google_id TEXT,
            picture TEXT,
            auth_provider TEXT DEFAULT 'email',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_verified BOOLEAN DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully")

# Initialize database on startup
init_db()

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn

# JWT token decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token.split(' ')[1]
            
            data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            
            conn = get_db_connection()
            current_user = conn.execute('SELECT * FROM users WHERE email = ?', (data['email'],)).fetchone()
            conn.close()
            
            if not current_user:
                return jsonify({'message': 'Token is invalid!'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
            
        return f(dict(current_user), *args, **kwargs)
    
    return decorated

# Helper function to generate JWT token
def generate_token(user_email):
    payload = {
        'email': user_email,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

# Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Flask backend is running'})

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate input
        required_fields = ['email', 'password', 'name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        name = data['name'].strip()
        
        conn = get_db_connection()
        
        # Check if user already exists
        existing_user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        if existing_user:
            conn.close()
            return jsonify({'error': 'User with this email already exists'}), 409
        
        # Hash password
        hashed_password = generate_password_hash(password)
        
        # Insert user into database
        cursor = conn.execute('''
            INSERT INTO users (email, password, name, auth_provider, is_verified)
            VALUES (?, ?, ?, ?, ?)
        ''', (email, hashed_password, name, 'email', 0))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        if user_id:
            # Generate token
            token = generate_token(email)
            
            return jsonify({
                'message': 'User registered successfully',
                'token': token,
                'user': {
                    'id': user_id,
                    'email': email,
                    'name': name,
                    'auth_provider': 'email'
                }
            }), 201
        else:
            return jsonify({'error': 'Failed to create user'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        
        if not user:
            conn.close()
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check password
        if not check_password_hash(user['password'], password):
            conn.close()
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate token
        token = generate_token(email)
        
        # Update last login
        conn.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE email = ?', (email,))
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'name': user['name'],
                'auth_provider': user['auth_provider']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/google-auth', methods=['POST'])
def google_auth():
    try:
        data = request.get_json()
        google_token = data.get('token')
        
        if not google_token:
            return jsonify({'error': 'Google token is required'}), 400
        
        # For demo purposes - In production, verify the Google token properly
        # This is a simplified version - you'd normally verify with Google
        
        # Mock Google user data (replace with actual Google token verification)
        # For demo: assuming token contains user info (this is NOT secure for production)
        try:
            import json
            import base64
            # This is just for demo - DO NOT use in production
            # You should verify the token with Google's API
            
            # For now, we'll create a simple demo user
            email = "demo@google.com"  # Replace with actual Google verification
            name = "Demo User"
            google_id = "demo123"
            picture = ""
            
        except Exception as e:
            return jsonify({'error': 'Invalid Google token'}), 401
        
        conn = get_db_connection()
        
        # Check if user exists
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        
        if user:
            # Update existing user with Google info
            conn.execute('''
                UPDATE users SET google_id = ?, picture = ?, last_login = CURRENT_TIMESTAMP, 
                auth_provider = ? WHERE email = ?
            ''', (google_id, picture, 'google', email))
            user_id = user['id']
        else:
            # Create new user
            cursor = conn.execute('''
                INSERT INTO users (email, name, google_id, picture, auth_provider, is_verified)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (email, name, google_id, picture, 'google', 1))
            user_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        # Generate JWT token
        token = generate_token(email)
        
        return jsonify({
            'message': 'Google authentication successful',
            'token': token,
            'user': {
                'id': user_id,
                'email': email,
                'name': name,
                'picture': picture,
                'auth_provider': 'google'
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    try:
        return jsonify({
            'user': {
                'id': current_user['id'],
                'email': current_user['email'],
                'name': current_user['name'],
                'picture': current_user.get('picture', ''),
                'auth_provider': current_user.get('auth_provider', 'email'),
                'created_at': current_user['created_at'],
                'is_verified': bool(current_user.get('is_verified', False))
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    try:
        data = request.get_json()
        
        # Fields that can be updated
        name = data.get('name')
        
        if not name:
            return jsonify({'error': 'Name is required'}), 400
        
        conn = get_db_connection()
        result = conn.execute('''
            UPDATE users SET name = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (name, current_user['id']))
        
        conn.commit()
        
        if result.rowcount > 0:
            conn.close()
            return jsonify({'message': 'Profile updated successfully'}), 200
        else:
            conn.close()
            return jsonify({'error': 'No changes made'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
@token_required
def logout(current_user):
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/api/change-password', methods=['POST'])
@token_required
def change_password(current_user):
    try:
        data = request.get_json()
        
        if current_user.get('auth_provider') == 'google':
            return jsonify({'error': 'Cannot change password for Google accounts'}), 400
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current and new passwords are required'}), 400
        
        # Verify current password
        if not check_password_hash(current_user['password'], current_password):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Hash new password
        new_hashed_password = generate_password_hash(new_password)
        
        # Update password
        conn = get_db_connection()
        conn.execute('''
            UPDATE users SET password = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (new_hashed_password, current_user['id']))
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("Starting Flask application with SQLite...")
    print("Database file:", DATABASE_PATH)
    print("Available endpoints:")
    print("POST /api/register - User registration")
    print("POST /api/login - User login")
    print("POST /api/google-auth - Google OAuth login")
    print("GET /api/profile - Get user profile")
    print("PUT /api/profile - Update user profile")
    print("POST /api/logout - User logout")
    print("POST /api/change-password - Change password")
    
    app.run(debug=True, host='0.0.0.0', port=5000)