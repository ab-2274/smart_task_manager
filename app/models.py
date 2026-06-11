from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    tasks = db.relationship('Task', backref='owner', lazy=True, cascade='all, delete-orphan')
    categories = db.relationship('Category', backref='owner', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(7), default='#4f46e5')  # Hex code for styling (e.g. #4f46e5)
    icon = db.Column(db.String(50), default='fa-tag')    # FontAwesome icon class
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # Relationships
    tasks = db.relationship('Task', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'


class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    priority = db.Column(db.String(20), default='Medium')  # Low, Medium, High, Urgent
    status = db.Column(db.String(20), default='Pending')    # Pending, In Progress, Completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
    
    # Relationships
    subtasks = db.relationship('Subtask', backref='task', lazy=True, cascade='all, delete-orphan')
    activity_logs = db.relationship('ActivityLog', backref='task', lazy=True, cascade='all, delete-orphan', order_by='ActivityLog.timestamp.desc()')

    @property
    def completion_percentage(self):
        if not self.subtasks:
            return 100 if self.status == 'Completed' else 0
        completed = sum(1 for sub in self.subtasks if sub.is_completed)
        return int((completed / len(self.subtasks)) * 100)

    @property
    def is_overdue(self):
        if self.status == 'Completed' or not self.due_date:
            return False
        return self.due_date < date.today()

    def __repr__(self):
        return f'<Task {self.title}>'


class Subtask(db.Model):
    __tablename__ = 'subtasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)

    def __repr__(self):
        return f'<Subtask {self.title}>'


class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)

    def __repr__(self):
        return f'<ActivityLog {self.action} on Task {self.task_id}>'
