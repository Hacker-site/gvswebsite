from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import date

app = Flask(__name__)
app.secret_key = "gvs_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(10), default='student')

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.String(20))
    status = db.Column(db.String(5))

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password='admin123', role='admin')
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def home(): return render_template('index.html')

@app.route('/about')
def about(): return render_template('about.html')

@app.route('/contact')
def contact(): return render_template('contact.html')

@app.route('/courses')
def courses(): return render_template('courses.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        user = User.query.filter_by(username=u, password=p).first()
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            return redirect(url_for('dashboard'))
        flash("Invalid Credentials!")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    history = Attendance.query.filter_by(user_id=user.id).all()
    students = User.query.filter_by(role='student').all() if user.role == 'admin' else []
    return render_template('dashboard.html', user=user, history=history, students=students)

@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    if 'user_id' not in session: return redirect(url_for('login'))
    today = str(date.today())
    user_id = session['user_id']
    exists = Attendance.query.filter_by(user_id=user_id, date=today).first()
    if exists: flash("Already marked for today!")
    else:
        new_att = Attendance(user_id=user_id, date=today, status='P')
        db.session.add(new_att)
        db.session.commit()
        flash("Attendance Marked!")
    return redirect(url_for('dashboard'))

@app.route('/admin_mark', methods=['POST'])
def admin_mark():
    if session.get('role') != 'admin': return "Unauthorized"
    target_id = request.form['user_id']
    today = str(date.today())
    new_att = Attendance(user_id=target_id, date=today, status='P')
    db.session.add(new_att)
    db.session.commit()
    flash("Admin marked attendance!")
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
