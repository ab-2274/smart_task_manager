from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app.auth import auth
from app.auth.forms import RegistrationForm, LoginForm
from app.models import db, User, Category

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('tasks.dashboard'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.flush() # Get user.id before commit to seed default categories
            
            # Seed default categories for new user
            default_categories = [
                Category(name='Work', color='#4f46e5', icon='fa-briefcase', user_id=user.id),
                Category(name='Personal', color='#10b981', icon='fa-user', user_id=user.id),
                Category(name='Study', color='#f59e0b', icon='fa-book', user_id=user.id),
                Category(name='Health', color='#ec4899', icon='fa-heart-pulse', user_id=user.id)
            ]
            for cat in default_categories:
                db.session.add(cat)
                
            db.session.commit()
            flash('Your account has been created successfully! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            
    return render_template('auth/register.html', title='Register', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('tasks.dashboard'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('tasks.dashboard'))
        else:
            flash('Login unsuccessful. Please check your email and password.', 'danger')
            
    return render_template('auth/login.html', title='Login', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


from app.auth.forms import UpdateProfileForm

@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Verification failed: Current password is incorrect.', 'danger')
        else:
            current_user.username = form.username.data
            current_user.email = form.email.data
            
            if form.new_password.data:
                if len(form.new_password.data) < 8:
                    flash('New password must be at least 8 characters long.', 'danger')
                    return render_template('auth/profile.html', title='Profile Settings', form=form)
                current_user.set_password(form.new_password.data)
                
            try:
                db.session.commit()
                flash('Your profile settings have been updated!', 'success')
                return redirect(url_for('auth.profile'))
            except Exception as e:
                db.session.rollback()
                flash('An error occurred. Please try again.', 'danger')
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        
    return render_template('auth/profile.html', title='Profile Settings', form=form)

