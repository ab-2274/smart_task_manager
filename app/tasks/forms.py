from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, SubmitField
from wtforms.fields import ColorField
from wtforms.validators import DataRequired, Length, Optional

class TaskForm(FlaskForm):
    title = StringField('Task Title', validators=[
        DataRequired(message="Task title is required."),
        Length(max=100, message="Title must be under 100 characters.")
    ])
    description = TextAreaField('Description', validators=[Length(max=1000)])
    due_date = DateField('Due Date', validators=[Optional()], format='%Y-%m-%d')
    priority = SelectField('Priority Level', choices=[
        ('Low', 'Low 🟢'),
        ('Medium', 'Medium 🟡'),
        ('High', 'High 🟠'),
        ('Urgent', 'Urgent 🔴')
    ], default='Medium')
    status = SelectField('Task Status', choices=[
        ('Pending', 'Pending ⏳'),
        ('In Progress', 'In Progress 🔄'),
        ('Completed', 'Completed ✅')
    ], default='Pending')
    category_id = SelectField('Category', coerce=int, validators=[Optional()])
    submit = SubmitField('Save Task')


class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[
        DataRequired(message="Category name is required."),
        Length(max=50)
    ])
    color = ColorField('Category Theme Color', default='#4f46e5')
    icon = SelectField('Category Icon', choices=[
        ('fa-briefcase', '💼 Work / Office'),
        ('fa-user', '👤 Personal / Life'),
        ('fa-book', '📚 Study / School'),
        ('fa-heart-pulse', '❤️ Health / Wellness'),
        ('fa-tag', '🏷️ Label / General'),
        ('fa-cart-shopping', '🛒 Shopping / Tasks'),
        ('fa-dumbbell', '💪 Fitness / Sports'),
        ('fa-money-bill-wave', '💵 Finance / Budget'),
        ('fa-graduation-cap', '🎓 Learning / Skills'),
        ('fa-house', '🏠 Home / Family')
    ], default='fa-tag')
    submit = SubmitField('Save Category')


class SubtaskForm(FlaskForm):
    title = StringField('Subtask Title', validators=[
        DataRequired(message="Subtask title is required."),
        Length(max=100)
    ])
    submit = SubmitField('Add')
