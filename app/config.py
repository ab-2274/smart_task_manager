import os

class Config:
    # Secret key for Flask forms and session signing
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-jwt-secret-task-manager-token-key-2026'
    
    # SQLite Database setting
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'tasks.db')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
