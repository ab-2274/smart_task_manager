# Smart Task Manager Web Application

A feature-rich, modern, and beautiful **Smart Task Manager** web application built using **Python Flask**, **SQLite**, and **SQLAlchemy** (using Flask-SQLAlchemy). 

The application features a sleek dark-mode **glassmorphic design** built on Bootstrap 5, complete with interactive charts, user authentication, a categorization engine, subtask checklists, and a custom **Smart Focus Assistant** recommendation engine.

---

## 🌟 Key Features

1. **User Authentication System**: Fully secure registration, login, and logout routines powered by `Flask-Login` and `Werkzeug` security password hashing.
2. **Category & Tag Management**: Create custom workflow labels/tags with dedicated hex color selectors to categorize and sort tasks.
3. **Subtask Checklists**: Break down tasks into smaller steps. Checking off items dynamically updates progress bars and parent task states via AJAX in real-time.
4. **Productivity Analytics**: Full integration with `Chart.js` rendering breakdowns of tasks by status (doughnut), priorities (bar), and categories (polar area).
5. **Intelligent Smart Focus Assistant**:
   An algorithm scores active tasks using priority metrics, due-dates, and progression status:
   * **Overdue**: +50 points
   * **Urgent Priority**: +40 points
   * **Due Today**: +40 points
   * **Due Tomorrow**: +25 points
   * **In Progress status**: +8 points (to promote finishing started items)
   * High priority tasks due in under 3 days are highlighted.
   * The task with the highest cumulative score is highlighted as the recommended **Next Best Task**.

---

## 📁 Directory Structure

```
smart_task_manager/
│
├── app/
│   ├── __init__.py          # Flask Application Factory and SQLite Database init
│   ├── config.py            # Local app and SQL configurations
│   ├── models.py            # Database schemas (User, Category, Task, Subtask)
│   ├── auth/                # User authentication blueprint
│   │   ├── __init__.py
│   │   ├── routes.py        # Login, logout, and sign-up handlers
│   │   └── forms.py         # WTForms validation for auth inputs
│   ├── tasks/               # Core tasks and management blueprint
│   │   ├── __init__.py
│   │   ├── routes.py        # Task CRUD, AJAX toggling, analytics, categories
│   │   └── forms.py         # WTForms validation for tasks & checklists
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css    # Premium custom HSL variables and glassmorphic UI CSS
│   │   └── js/
│   │       └── main.js      # Client controller for AJAX toggles and alert fading
│   └── templates/
│       ├── base.html        # Main layouts with navbar, sidebar, and messaging
│       ├── auth/
│       │   ├── login.html
│       │   └── register.html
│       └── tasks/
│           ├── dashboard.html # The main task manager viewport and filtering panels
│           ├── task_form.html # Create / edit task viewport
│           ├── detail.html    # Detailed view & subtasks checklist manager
│           ├── categories.html# Category creator and manager
│           └── analytics.html # Productivity metrics and visual charts
│
├── requirements.txt         # Dependency declarations
├── run.py                   # Development server execution script
└── README.md                # System documentation
```

---

## 🚀 Quick Setup Instructions

Make sure you have **Python 3.8+** installed on your system.

### 1. Clone or Open the Workspace
Open the project directory in your terminal:
```bash
cd C:/Users/Abhinandan/.gemini/antigravity/scratch/smart_task_manager
```

### 2. Create a Virtual Environment
It is recommended to run the app in a isolated environment.
```powershell
# On Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
Install the required packages from `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 4. Run the Application
Start the development server:
```bash
python run.py
```

### 5. Access the Web App
Open your browser and navigate to:
[http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🛠️ Verification & Development Details
- On first startup, SQLite will automatically create `app/tasks.db` database inside the `app/` folder.
- When registering a new user, the system automatically seeds four default categories: **Work** (Indigo), **Personal** (Green), **Learning** (Yellow), and **Urgent** (Red).
- Flask runs with `debug=True` by default in `run.py`. Turn this off for staging deployment environment settings.
