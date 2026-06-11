from datetime import datetime, date, timedelta
from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import current_user, login_required
from app.tasks import tasks
from app.tasks.forms import TaskForm, CategoryForm, SubtaskForm
from app.models import db, Task, Category, Subtask, ActivityLog

def log_activity(task_id, action_text):
    log = ActivityLog(task_id=task_id, action=action_text)
    db.session.add(log)

@tasks.route('/')
@tasks.route('/dashboard')
@login_required
def dashboard():
    # Base query for user's tasks
    query = Task.query.filter_by(user_id=current_user.id)
    
    # Filter by search term
    search_query = request.args.get('q', '')
    if search_query:
        query = query.filter(
            (Task.title.ilike(f'%{search_query}%')) | 
            (Task.description.ilike(f'%{search_query}%'))
        )
        
    # Filter by category
    category_id = request.args.get('category', type=int)
    if category_id:
        query = query.filter_by(category_id=category_id)
        
    # Filter by priority
    priority = request.args.get('priority', '')
    if priority:
        query = query.filter_by(priority=priority)
        
    # Filter by status
    status = request.args.get('status', '')
    if status:
        query = query.filter_by(status=status)
        
    # Sorting
    sort_by = request.args.get('sort_by', 'due_date')
    if sort_by == 'due_date':
        query = query.order_by(Task.due_date.asc().nullslast(), Task.created_at.desc())
    elif sort_by == 'priority':
        # Custom sorting logic for priority: Urgent -> High -> Medium -> Low
        # We can implement this in SQLite using CASE statements
        query = query.order_by(
            db.case(
                (Task.priority == 'Urgent', 1),
                (Task.priority == 'High', 2),
                (Task.priority == 'Medium', 3),
                (Task.priority == 'Low', 4),
                else_=5
            ),
            Task.due_date.asc().nullslast()
        )
    elif sort_by == 'status':
        query = query.order_by(
            db.case(
                (Task.status == 'In Progress', 1),
                (Task.status == 'Pending', 2),
                (Task.status == 'Completed', 3),
                else_=4
            ),
            Task.due_date.asc().nullslast()
        )
    else:  # default or 'created_at'
        query = query.order_by(Task.created_at.desc())
        
    tasks_list = query.all()
    categories = Category.query.filter_by(user_id=current_user.id).all()
    
    # Smart Recommendations Engine
    overdue_tasks = []
    upcoming_urgent = []
    recommended_task = None
    
    active_tasks = [t for t in tasks_list if t.status != 'Completed']
    if active_tasks:
        today = date.today()
        scored_tasks = []
        
        for task in active_tasks:
            score = 0
            
            # Priority weights
            if task.priority == 'Urgent':
                score += 40
            elif task.priority == 'High':
                score += 25
            elif task.priority == 'Medium':
                score += 10
                
            # Due date scoring
            if task.due_date:
                days_left = (task.due_date - today).days
                if days_left < 0:
                    score += 50  # Overdue
                    overdue_tasks.append(task)
                elif days_left == 0:
                    score += 40  # Due today
                elif days_left == 1:
                    score += 25  # Due tomorrow
                elif days_left <= 3:
                    score += 15  # Due in 3 days
                elif days_left <= 7:
                    score += 5   # Due in a week
            
            # Status bonus
            if task.status == 'In Progress':
                score += 8  # Encourage finishing started work
                
            scored_tasks.append((score, task))
            
            # Categorize upcoming urgent tasks (due in <= 3 days, priority Urgent or High)
            if task.due_date and 0 <= (task.due_date - today).days <= 3 and task.priority in ['High', 'Urgent']:
                upcoming_urgent.append(task)
                
        # Sort by score descending to find recommended task
        if scored_tasks:
            scored_tasks.sort(key=lambda x: x[0], reverse=True)
            recommended_task = scored_tasks[0][1]

    # Overall User Stats for Dashboard KPI Cards
    stats = {
        'total': Task.query.filter_by(user_id=current_user.id).count(),
        'completed': Task.query.filter_by(user_id=current_user.id, status='Completed').count(),
        'pending': Task.query.filter(Task.user_id == current_user.id, Task.status != 'Completed').count(),
        'overdue': Task.query.filter(Task.user_id == current_user.id, Task.due_date < date.today(), Task.status != 'Completed').count()
    }

    return render_template(
        'tasks/dashboard.html',
        tasks=tasks_list,
        categories=categories,
        overdue_tasks=overdue_tasks,
        upcoming_urgent=upcoming_urgent,
        recommended_task=recommended_task,
        stats=stats,
        current_filters={
            'q': search_query,
            'category': category_id,
            'priority': priority,
            'status': status,
            'sort_by': sort_by
        }
    )


@tasks.route('/task/new', methods=['GET', 'POST'])
@login_required
def create_task():
    form = TaskForm()
    
    # Populate categories
    categories = Category.query.filter_by(user_id=current_user.id).all()
    form.category_id.choices = [(0, 'None / General')] + [(c.id, c.name) for c in categories]
    
    if form.validate_on_submit():
        category_val = form.category_id.data
        selected_category_id = None if category_val == 0 else category_val
        
        task = Task(
            title=form.title.data,
            description=form.description.data,
            due_date=form.due_date.data,
            priority=form.priority.data,
            status=form.status.data,
            category_id=selected_category_id,
            user_id=current_user.id
        )
        
        try:
            db.session.add(task)
            db.session.flush() # Flush to get task.id
            log_activity(task.id, 'Task created')
            db.session.commit()
            flash('Task created successfully!', 'success')
            return redirect(url_for('tasks.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating task. Please try again.', 'danger')
            
    return render_template('tasks/task_form.html', title='New Task', form=form, legend='Create a New Task')


@tasks.route('/task/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        abort(403)
        
    form = TaskForm()
    
    # Populate categories
    categories = Category.query.filter_by(user_id=current_user.id).all()
    form.category_id.choices = [(0, 'None / General')] + [(c.id, c.name) for c in categories]
    
    if form.validate_on_submit():
        category_val = form.category_id.data
        task.category_id = None if category_val == 0 else category_val
        task.title = form.title.data
        task.description = form.description.data
        task.due_date = form.due_date.data
        task.priority = form.priority.data
        
        old_status = task.status
        new_status = form.status.data
        task.status = new_status
        
        try:
            log_activity(task.id, 'Task details updated')
            if old_status != new_status:
                log_activity(task.id, f"Status updated to: {new_status}")
            db.session.commit()
            flash('Task updated successfully!', 'success')
            return redirect(url_for('tasks.task_detail', task_id=task.id))
        except Exception as e:
            db.session.rollback()
            flash('Error updating task. Please try again.', 'danger')
            
    elif request.method == 'GET':
        form.title.data = task.title
        form.description.data = task.description
        form.due_date.data = task.due_date
        form.priority.data = task.priority
        form.status.data = task.status
        form.category_id.data = task.category_id if task.category_id else 0
        
    return render_template('tasks/task_form.html', title='Edit Task', form=form, legend=f'Edit: {task.title}')


@tasks.route('/task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def task_detail(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        abort(403)
        
    subtask_form = SubtaskForm()
    
    if subtask_form.validate_on_submit():
        subtask = Subtask(title=subtask_form.title.data, task_id=task.id)
        db.session.add(subtask)
        
        # If task was completed, and we add a subtask, we might want to revert it to In Progress/Pending
        status_reverted = False
        if task.status == 'Completed':
            task.status = 'In Progress'
            status_reverted = True
            
        try:
            db.session.flush() # get subtask id / track
            log_activity(task.id, f"Checklist item '{subtask.title}' added")
            if status_reverted:
                log_activity(task.id, "Status automatically updated to In Progress")
            db.session.commit()
            flash('Subtask added!', 'success')
            return redirect(url_for('tasks.task_detail', task_id=task.id))
        except Exception as e:
            db.session.rollback()
            flash('Error adding subtask.', 'danger')
            
    return render_template('tasks/detail.html', task=task, subtask_form=subtask_form)


@tasks.route('/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        abort(403)
        
    try:
        db.session.delete(task)
        db.session.commit()
        flash('Task has been deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting task.', 'danger')
        
    return redirect(url_for('tasks.dashboard'))


@tasks.route('/subtask/<int:subtask_id>/toggle', methods=['POST'])
@login_required
def toggle_subtask(subtask_id):
    subtask = Subtask.query.get_or_404(subtask_id)
    task = subtask.task
    if task.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    subtask.is_completed = not subtask.is_completed
    
    # Auto-update parent task status if all subtasks are complete/incomplete
    old_status = task.status
    all_completed = all(sub.is_completed for sub in task.subtasks)
    if all_completed and task.status != 'Completed':
        task.status = 'Completed'
    elif not all_completed and task.status == 'Completed':
        task.status = 'In Progress'
        
    try:
        log_activity(task.id, f"Checklist item '{subtask.title}' marked {'completed' if subtask.is_completed else 'incomplete'}")
        if old_status != task.status:
            log_activity(task.id, f"Status updated to: {task.status}")
        db.session.commit()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.args.get('ajax') == '1':
            return jsonify({
                'success': True,
                'is_completed': subtask.is_completed,
                'completion_percentage': task.completion_percentage,
                'task_status': task.status
            })
        flash('Subtask updated!', 'success')
        return redirect(url_for('tasks.task_detail', task_id=task.id))
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database transaction failed'}), 500


@tasks.route('/subtask/<int:subtask_id>/delete', methods=['POST'])
@login_required
def delete_subtask(subtask_id):
    subtask = Subtask.query.get_or_404(subtask_id)
    task = subtask.task
    if task.user_id != current_user.id:
        abort(403)
        
    try:
        log_activity(task.id, f"Checklist item '{subtask.title}' deleted")
        db.session.delete(subtask)
        db.session.commit()
        flash('Subtask deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting subtask.', 'danger')
        
    return redirect(url_for('tasks.task_detail', task_id=task.id))


@tasks.route('/categories', methods=['GET', 'POST'])
@login_required
def manage_categories():
    form = CategoryForm()
    categories = Category.query.filter_by(user_id=current_user.id).all()
    
    if form.validate_on_submit():
        category = Category(name=form.name.data, color=form.color.data, icon=form.icon.data, user_id=current_user.id)
        try:
            db.session.add(category)
            db.session.commit()
            flash('Category added successfully!', 'success')
            return redirect(url_for('tasks.manage_categories'))
        except Exception as e:
            db.session.rollback()
            flash('Error adding category. It might already exist.', 'danger')
            
    return render_template('tasks/categories.html', title='Manage Categories', form=form, categories=categories)


@tasks.route('/category/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.user_id != current_user.id:
        abort(403)
        
    try:
        # Note: tasks associated with this category will have category_id set to NULL automatically due to SET NULL
        db.session.delete(category)
        db.session.commit()
        flash('Category has been deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting category.', 'danger')
        
    return redirect(url_for('tasks.manage_categories'))


@tasks.route('/analytics')
@login_required
def analytics():
    tasks_query = Task.query.filter_by(user_id=current_user.id)
    all_tasks = tasks_query.all()
    total_count = len(all_tasks)
    
    if total_count == 0:
        return render_template('tasks/analytics.html', title='Analytics', total_count=0)
        
    completed_count = sum(1 for t in all_tasks if t.status == 'Completed')
    in_progress_count = sum(1 for t in all_tasks if t.status == 'In Progress')
    pending_count = sum(1 for t in all_tasks if t.status == 'Pending')
    
    overdue_count = sum(1 for t in all_tasks if t.is_overdue)
    completion_rate = int((completed_count / total_count) * 100)
    
    # Priority counts
    urgent_count = sum(1 for t in all_tasks if t.priority == 'Urgent')
    high_count = sum(1 for t in all_tasks if t.priority == 'High')
    medium_count = sum(1 for t in all_tasks if t.priority == 'Medium')
    low_count = sum(1 for t in all_tasks if t.priority == 'Low')
    
    # Category task distribution
    categories = Category.query.filter_by(user_id=current_user.id).all()
    category_labels = []
    category_counts = []
    category_colors = []
    
    # General (unassigned category) tasks
    category_completion_rates = []
    no_cat_count = sum(1 for t in all_tasks if t.category_id is None)
    if no_cat_count > 0:
        category_labels.append('General')
        category_counts.append(no_cat_count)
        category_colors.append('#6b7280') # gray color
        no_cat_completed = sum(1 for t in all_tasks if t.category_id is None and t.status == 'Completed')
        category_completion_rates.append(int((no_cat_completed / no_cat_count) * 100))
        
    for cat in categories:
        cat_tasks = [t for t in all_tasks if t.category_id == cat.id]
        cat_count = len(cat_tasks)
        if cat_count > 0:
            category_labels.append(cat.name)
            category_counts.append(cat_count)
            category_colors.append(cat.color)
            cat_completed = sum(1 for t in cat_tasks if t.status == 'Completed')
            category_completion_rates.append(int((cat_completed / cat_count) * 100))
            
    return render_template(
        'tasks/analytics.html',
        title='Analytics',
        total_count=total_count,
        completed_count=completed_count,
        in_progress_count=in_progress_count,
        pending_count=pending_count,
        overdue_count=overdue_count,
        completion_rate=completion_rate,
        priority_data={
            'Urgent': urgent_count,
            'High': high_count,
            'Medium': medium_count,
            'Low': low_count
        },
        category_labels=category_labels,
        category_counts=category_counts,
        category_colors=category_colors,
        category_completion_rates=category_completion_rates
    )


import csv
import io
from flask import make_response

@tasks.route('/export/csv')
@login_required
def export_csv():
    # Fetch all tasks for current user
    tasks_list = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).all()
    
    # Create an in-memory string buffer for CSV
    si = io.StringIO()
    cw = csv.writer(si)
    
    # Write CSV Header
    cw.writerow([
        'Task ID', 'Title', 'Description', 'Priority', 'Status', 
        'Due Date', 'Category', 'Completion %', 'Date Created', 'Date Updated'
    ])
    
    # Write Task Rows
    for t in tasks_list:
        category_name = t.category.name if t.category else 'General'
        cw.writerow([
            t.id,
            t.title,
            t.description or '',
            t.priority,
            t.status,
            t.due_date.strftime('%Y-%m-%d') if t.due_date else 'No Due Date',
            category_name,
            t.completion_percentage,
            t.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            t.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
        
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=tasks_export.csv"
    output.headers["Content-type"] = "text/csv"
    return output
