
"""
Example application with intentional security vulnerabilities
Use this file to test the security scanner
"""

import hashlib
import sqlite3

# Vulnerability 1: Hardcoded credentials
API_KEY = "sk_live_1234567890abcdef"
DATABASE_PASSWORD = "admin123"

# Vulnerability 2: Weak hash function (MD5)
def hash_password(password):
    """Insecure password hashing using MD5"""
    return hashlib.md5(password.encode()).hexdigest()

# Vulnerability 3: SQL Injection
def get_user(username):
    """SQL injection vulnerability"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Unsafe query - vulnerable to SQL injection
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    
    return cursor.fetchone()

# Vulnerability 4: Eval usage
def calculate(expression):
    """Dangerous use of eval"""
    return eval(expression)

# Vulnerability 5: Insecure randomness
import random

def generate_token():
    """Insecure random token generation"""
    return random.randint(1000, 9999)

# Vulnerability 6: Open redirect
def redirect_user(url):
    """Open redirect vulnerability"""
    import webbrowser
    webbrowser.open(url)

if __name__ == '__main__':
    print("Example application with security vulnerabilities")
    print("Use this to test the security scanner")
