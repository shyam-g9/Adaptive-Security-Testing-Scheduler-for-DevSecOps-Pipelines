"""
Comprehensive vulnerable application demonstrating various security vulnerabilities
This file contains intentional security flaws for testing security scanners
"""

import os
import subprocess
import pickle
import hashlib
import sqlite3
import random
import yaml
import json
from flask import Flask, request, render_template_string
import jwt
import base64

# Vulnerability 1: Hardcoded credentials and secrets
API_KEY = "sk_live_51ABC123DEF456GHI789JKL012MNO345PQR"
DATABASE_PASSWORD = "super_secret_admin_password_123"
JWT_SECRET = "weak_secret_key_for_jwt"
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# Vulnerability 2: Weak cryptography (MD5)
def hash_password_weak(password):
    """Insecure password hashing using MD5"""
    return hashlib.md5(password.encode()).hexdigest()

# Vulnerability 3: SQL Injection
def get_user_vulnerable(username):
    """SQL injection vulnerability"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # UNSAFE: Direct string interpolation in SQL
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)

    return cursor.fetchone()

# Vulnerability 4: Command Injection
def execute_command_vulnerable(user_input):
    """Command injection vulnerability"""
    # UNSAFE: Direct command execution with user input
    os.system(f"echo {user_input}")

# Vulnerability 5: Path Traversal
def read_file_vulnerable(filename):
    """Path traversal vulnerability"""
    # UNSAFE: No path validation
    with open(filename, 'r') as f:
        return f.read()

# Vulnerability 6: Insecure Deserialization
def load_data_vulnerable(serialized_data):
    """Insecure pickle deserialization"""
    # UNSAFE: Pickle can execute arbitrary code
    return pickle.loads(serialized_data)

# Vulnerability 7: XSS in web application
app = Flask(__name__)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    # UNSAFE: Direct insertion into HTML without escaping
    template = f"<h1>Search results for: {query}</h1><p>No results found.</p>"
    return render_template_string(template)

# Vulnerability 8: Weak JWT handling
def create_token_vulnerable(user_id):
    """Weak JWT token creation"""
    payload = {'user_id': user_id, 'admin': True}
    # UNSAFE: Using weak secret and no expiration
    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    return token

def verify_token_vulnerable(token):
    """Insecure JWT verification"""
    try:
        # UNSAFE: No signature verification in some cases
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'], verify_exp=False)
        return payload
    except:
        return None

# Vulnerability 9: Insecure random number generation
def generate_session_id():
    """Insecure session ID generation"""
    # UNSAFE: Using weak random
    return str(random.randint(100000, 999999))

# Vulnerability 10: Information disclosure
def get_system_info():
    """Information disclosure vulnerability"""
    # UNSAFE: Exposing sensitive system information
    return {
        'os': os.uname(),
        'env': dict(os.environ),
        'cwd': os.getcwd()
    }

# Vulnerability 11: Race condition
temp_files = []

def create_temp_file_vulnerable(content):
    """Race condition in temporary file creation"""
    # UNSAFE: Predictable temporary file names
    filename = f"/tmp/temp_{random.randint(1000, 9999)}.txt"
    temp_files.append(filename)

    with open(filename, 'w') as f:
        f.write(content)

    return filename

# Vulnerability 12: Buffer overflow simulation (Python doesn't have true buffer overflows, but concept)
def process_data_vulnerable(data):
    """Buffer overflow concept - no bounds checking"""
    buffer = bytearray(1024)
    # UNSAFE: No bounds checking
    buffer[:len(data)] = data
    return buffer

# Vulnerability 13: Insecure configuration loading
def load_config_vulnerable(config_file):
    """Insecure YAML loading"""
    with open(config_file, 'r') as f:
        # UNSAFE: Loading YAML without safe_load
        config = yaml.load(f, Loader=yaml.FullLoader)  # Should use yaml.safe_load
    return config

# Vulnerability 14: Authentication bypass
def authenticate_vulnerable(username, password):
    """Weak authentication"""
    # UNSAFE: No proper password verification
    if username == "admin" and password == "password":
        return True
    return False

# Vulnerability 15: Authorization bypass
def check_permission_vulnerable(user, action):
    """Missing authorization check"""
    # UNSAFE: No permission checking
    return True  # Always allows

# Vulnerability 16: Insecure logging
def log_sensitive_data(data):
    """Logging sensitive information"""
    # UNSAFE: Logging passwords and secrets
    print(f"User data: {data}")  # This could include passwords

# Vulnerability 17: Open redirect
def redirect_user_vulnerable(url):
    """Open redirect vulnerability"""
    # UNSAFE: No validation of redirect URL
    from flask import redirect
    return redirect(url)

# Vulnerability 18: CSRF vulnerability
@app.route('/transfer', methods=['POST'])
def transfer_money():
    """CSRF vulnerable endpoint"""
    # UNSAFE: No CSRF protection
    amount = request.form.get('amount')
    to_account = request.form.get('to_account')
    # Process transfer...
    return "Transfer completed"

# Vulnerability 19: Insecure file upload
@app.route('/upload', methods=['POST'])
def upload_file():
    """Insecure file upload"""
    file = request.files['file']
    # UNSAFE: No validation of file type or content
    filename = file.filename
    file.save(os.path.join('/uploads', filename))
    return "File uploaded"

# Vulnerability 20: Timing attack vulnerability
def check_password_vulnerable(stored_hash, input_password):
    """Timing attack vulnerable password check"""
    input_hash = hashlib.sha256(input_password.encode()).hexdigest()
    # UNSAFE: Early return on mismatch reveals timing information
    if len(input_hash) != len(stored_hash):
        return False
    for i in range(len(input_hash)):
        if input_hash[i] != stored_hash[i]:
            return False
    return True

# Vulnerability 21: Insecure random for cryptography
def generate_crypto_key():
    """Insecure cryptographic key generation"""
    # UNSAFE: Using random instead of secrets
    return ''.join(random.choice('0123456789ABCDEF') for _ in range(32))

# Vulnerability 22: Directory traversal in file operations
def serve_file_vulnerable(filepath):
    """Directory traversal in file serving"""
    # UNSAFE: No path validation
    return open(filepath, 'rb').read()

# Vulnerability 23: Insecure subprocess usage
def run_subprocess_vulnerable(command):
    """Insecure subprocess execution"""
    # UNSAFE: Using shell=True with user input
    result = subprocess.run(command, shell=True, capture_output=True)
    return result.stdout.decode()

# Vulnerability 24: Weak encryption
def encrypt_data_vulnerable(data, key):
    """Weak encryption implementation"""
    # UNSAFE: ECB mode, no IV, weak key derivation
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    cipher = Cipher(algorithms.AES(key.encode().ljust(32, b'\0')[:32]), modes.ECB())
    encryptor = cipher.encryptor()
    return encryptor.update(data.encode()) + encryptor.finalize()

# Vulnerability 25: Insecure cookie handling
@app.route('/set_cookie')
def set_cookie_vulnerable():
    """Insecure cookie setting"""
    response = app.make_response("Cookie set")
    # UNSAFE: No secure flags, no httpOnly
    response.set_cookie('session', 'session_value')
    return response

# Vulnerability 26: Mass assignment vulnerability
class User:
    def __init__(self, **kwargs):
        # UNSAFE: Mass assignment without whitelist
        for key, value in kwargs.items():
            setattr(self, key, value)

def create_user_vulnerable(user_data):
    """Mass assignment vulnerability"""
    # UNSAFE: Allows setting any attribute
    return User(**user_data)

# Vulnerability 27: Insecure direct object reference
users_db = {'1': {'name': 'Alice', 'secret': 'Alice\'s secret'},
            '2': {'name': 'Bob', 'secret': 'Bob\'s secret'}}

@app.route('/user/<user_id>')
def get_user_profile(user_id):
    """Insecure direct object reference"""
    # UNSAFE: No authorization check
    user = users_db.get(user_id)
    if user:
        return json.dumps(user)
    return "User not found", 404

# Vulnerability 28: Host header injection
@app.route('/host')
def get_host():
    """Host header injection vulnerability"""
    host = request.headers.get('Host')
    # UNSAFE: Using host header directly
    return f"Host: {host}"

# Vulnerability 29: Insecure CORS
from flask_cors import CORS
# UNSAFE: Allowing all origins
CORS(app, origins="*")

# Vulnerability 30: Information disclosure in error messages
@app.route('/divide')
def divide():
    """Information disclosure in errors"""
    a = int(request.args.get('a', '10'))
    b = int(request.args.get('b', '0'))
    # UNSAFE: Division by zero will leak stack trace
    return str(a / b)

if __name__ == '__main__':
    print("Vulnerable application started - DO NOT USE IN PRODUCTION")
    print("This application contains intentional security vulnerabilities")
    print("Use only for testing security scanners")
    app.run(debug=True, host='0.0.0.0', port=5000)