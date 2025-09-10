from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import cv2
import face_recognition
import numpy as np
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
import time
import threading
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
import bcrypt
import jwt
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///staff_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # student, teacher, headteacher, deputy, bursar
    full_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20))
    face_encoding = db.Column(db.Text)  # Store face encoding as JSON string
    fingerprint_data = db.Column(db.Text)  # Store fingerprint data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time_in = db.Column(db.DateTime)
    time_out = db.Column(db.DateTime)
    method = db.Column(db.String(20))  # face, fingerprint
    status = db.Column(db.String(20))  # present, absent, late
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Timetable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    day_of_week = db.Column(db.String(20), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    room = db.Column(db.String(20))
    class_name = db.Column(db.String(20))

class Performance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    attendance_score = db.Column(db.Float, default=0.0)
    punctuality_score = db.Column(db.Float, default=0.0)
    overall_score = db.Column(db.Float, default=0.0)
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Salary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    base_salary = db.Column(db.Float, nullable=False)
    attendance_bonus = db.Column(db.Float, default=0.0)
    performance_bonus = db.Column(db.Float, default=0.0)
    total_salary = db.Column(db.Float, nullable=False)
    paid = db.Column(db.Boolean, default=False)
    paid_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20))  # email, sms, system
    sent = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Procurement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    supplier = db.Column(db.String(100))
    requested_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Utility Functions
def send_email(to_email, subject, message):
    """Send email notification"""
    try:
        msg = MIMEMultipart()
        msg['From'] = os.getenv('EMAIL_USER', 'noreply@school.com')
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(message, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASSWORD'))
        text = msg.as_string()
        server.sendmail(os.getenv('EMAIL_USER'), to_email, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

def send_sms(phone_number, message):
    """Send SMS notification using Twilio"""
    try:
        from twilio.rest import Client
        client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
        message = client.messages.create(
            body=message,
            from_=os.getenv('TWILIO_PHONE_NUMBER'),
            to=phone_number
        )
        return True
    except Exception as e:
        print(f"SMS error: {e}")
        return False

def calculate_performance_score(teacher_id, month, year):
    """Calculate teacher performance score"""
    attendances = Attendance.query.filter_by(
        user_id=teacher_id
    ).filter(
        db.extract('month', Attendance.date) == month,
        db.extract('year', Attendance.date) == year
    ).all()
    
    if not attendances:
        return 0.0
    
    total_days = len(attendances)
    present_days = len([a for a in attendances if a.status == 'present'])
    on_time_days = len([a for a in attendances if a.status != 'late'])
    
    attendance_score = (present_days / total_days) * 10
    punctuality_score = (on_time_days / total_days) * 10
    
    return (attendance_score + punctuality_score) / 2

def generate_performance_report(month, year):
    """Generate performance report for all teachers"""
    teachers = User.query.filter_by(role='teacher').all()
    report_data = []
    
    for teacher in teachers:
        score = calculate_performance_score(teacher.id, month, year)
        report_data.append({
            'teacher_name': teacher.full_name,
            'score': score,
            'status': 'Good' if score >= 7 else 'Needs Improvement'
        })
    
    return report_data

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'student':
        return redirect(url_for('student_dashboard'))
    elif current_user.role == 'teacher':
        return redirect(url_for('teacher_dashboard'))
    elif current_user.role in ['headteacher', 'deputy']:
        return redirect(url_for('admin_dashboard'))
    elif current_user.role == 'bursar':
        return redirect(url_for('bursar_dashboard'))
    
    return redirect(url_for('index'))

@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('student/dashboard.html')

@app.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    # Get teacher's timetable
    timetable = Timetable.query.filter_by(teacher_id=current_user.id).all()
    
    # Get today's attendance
    today = datetime.now().date()
    today_attendance = Attendance.query.filter_by(
        user_id=current_user.id,
        date=today
    ).first()
    
    return render_template('teacher/dashboard.html', 
                         timetable=timetable, 
                         today_attendance=today_attendance)

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role not in ['headteacher', 'deputy']:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    # Get statistics
    total_teachers = User.query.filter_by(role='teacher').count()
    total_students = User.query.filter_by(role='student').count()
    
    # Get today's attendance
    today = datetime.now().date()
    today_attendance = Attendance.query.filter_by(date=today).count()
    
    return render_template('admin/dashboard.html',
                         total_teachers=total_teachers,
                         total_students=total_students,
                         today_attendance=today_attendance)

@app.route('/bursar/dashboard')
@login_required
def bursar_dashboard():
    if current_user.role != 'bursar':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    # Get salary statistics
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    pending_salaries = Salary.query.filter_by(
        month=current_month,
        year=current_year,
        paid=False
    ).count()
    
    total_salary_budget = db.session.query(db.func.sum(Salary.total_salary)).filter_by(
        month=current_month,
        year=current_year
    ).scalar() or 0
    
    return render_template('bursar/dashboard.html',
                         pending_salaries=pending_salaries,
                         total_salary_budget=total_salary_budget)

# Attendance Routes
@app.route('/attendance/check-in', methods=['GET', 'POST'])
@login_required
def check_in():
    if request.method == 'POST':
        method = request.form.get('method', 'manual')
        
        # Check if already checked in today
        today = datetime.now().date()
        existing_attendance = Attendance.query.filter_by(
            user_id=current_user.id,
            date=today
        ).first()
        
        if existing_attendance and existing_attendance.time_in:
            flash('Already checked in today!', 'error')
            return redirect(url_for('dashboard'))
        
        # Create attendance record
        if existing_attendance:
            existing_attendance.time_in = datetime.now()
            existing_attendance.method = method
            existing_attendance.status = 'present'
        else:
            attendance = Attendance(
                user_id=current_user.id,
                date=today,
                time_in=datetime.now(),
                method=method,
                status='present'
            )
            db.session.add(attendance)
        
        db.session.commit()
        flash('Check-in successful!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('attendance/check_in.html')

@app.route('/attendance/check-out', methods=['GET', 'POST'])
@login_required
def check_out():
    if request.method == 'POST':
        today = datetime.now().date()
        attendance = Attendance.query.filter_by(
            user_id=current_user.id,
            date=today
        ).first()
        
        if not attendance or not attendance.time_in:
            flash('No check-in record found for today!', 'error')
            return redirect(url_for('dashboard'))
        
        if attendance.time_out:
            flash('Already checked out today!', 'error')
            return redirect(url_for('dashboard'))
        
        attendance.time_out = datetime.now()
        db.session.commit()
        flash('Check-out successful!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('attendance/check_out.html')

# Face Recognition Routes
@app.route('/face-recognition/register', methods=['GET', 'POST'])
@login_required
def register_face():
    if request.method == 'POST':
        # Handle face registration
        # This would typically involve capturing an image and encoding it
        flash('Face registration feature will be implemented with camera integration', 'info')
        return redirect(url_for('dashboard'))
    
    return render_template('face_recognition/register.html')

@app.route('/face-recognition/verify', methods=['GET', 'POST'])
@login_required
def verify_face():
    if request.method == 'POST':
        # Handle face verification
        flash('Face verification feature will be implemented with camera integration', 'info')
        return redirect(url_for('dashboard'))
    
    return render_template('face_recognition/verify.html')

# Report Routes
@app.route('/reports/performance')
@login_required
def performance_report():
    if current_user.role not in ['headteacher', 'deputy', 'bursar']:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    month = request.args.get('month', datetime.now().month, type=int)
    year = request.args.get('year', datetime.now().year, type=int)
    
    report_data = generate_performance_report(month, year)
    
    return render_template('reports/performance.html', 
                         report_data=report_data,
                         month=month,
                         year=year)

@app.route('/reports/attendance')
@login_required
def attendance_report():
    if current_user.role not in ['headteacher', 'deputy', 'bursar']:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    start_date = request.args.get('start_date', datetime.now().date())
    end_date = request.args.get('end_date', datetime.now().date())
    
    attendances = Attendance.query.filter(
        Attendance.date >= start_date,
        Attendance.date <= end_date
    ).all()
    
    return render_template('reports/attendance.html', attendances=attendances)

# Salary Routes
@app.route('/salary/calculate')
@login_required
def calculate_salary():
    if current_user.role != 'bursar':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    month = request.args.get('month', datetime.now().month, type=int)
    year = request.args.get('year', datetime.now().year, type=int)
    
    # Calculate salaries for all staff
    users = User.query.filter(User.role.in_(['teacher', 'headteacher', 'deputy'])).all()
    
    for user in users:
        # Check if salary already calculated
        existing_salary = Salary.query.filter_by(
            user_id=user.id,
            month=month,
            year=year
        ).first()
        
        if not existing_salary:
            # Calculate performance score
            performance_score = calculate_performance_score(user.id, month, year)
            
            # Base salary (this would come from user profile)
            base_salary = 50000  # Default base salary
            
            # Calculate bonuses
            attendance_bonus = base_salary * 0.1 if performance_score >= 8 else 0
            performance_bonus = base_salary * 0.05 if performance_score >= 7 else 0
            
            total_salary = base_salary + attendance_bonus + performance_bonus
            
            salary = Salary(
                user_id=user.id,
                month=month,
                year=year,
                base_salary=base_salary,
                attendance_bonus=attendance_bonus,
                performance_bonus=performance_bonus,
                total_salary=total_salary
            )
            db.session.add(salary)
    
    db.session.commit()
    flash('Salaries calculated successfully!', 'success')
    return redirect(url_for('bursar_dashboard'))

# Notification Routes
@app.route('/notifications/send', methods=['GET', 'POST'])
@login_required
def send_notification():
    if current_user.role not in ['headteacher', 'deputy']:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        title = request.form.get('title')
        message = request.form.get('message')
        notification_type = request.form.get('type', 'system')
        
        user = User.query.get(user_id)
        if not user:
            flash('User not found!', 'error')
            return redirect(url_for('send_notification'))
        
        # Create notification record
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=notification_type
        )
        db.session.add(notification)
        
        # Send notification based on type
        if notification_type == 'email' and user.email:
            if send_email(user.email, title, message):
                notification.sent = True
                notification.sent_at = datetime.now()
        
        elif notification_type == 'sms' and user.phone_number:
            if send_sms(user.phone_number, message):
                notification.sent = True
                notification.sent_at = datetime.now()
        
        db.session.commit()
        flash('Notification sent successfully!', 'success')
        return redirect(url_for('send_notification'))
    
    users = User.query.filter(User.role.in_(['teacher', 'student'])).all()
    return render_template('notifications/send.html', users=users)

# Procurement Routes
@app.route('/procurement')
@login_required
def procurement():
    if current_user.role not in ['headteacher', 'deputy', 'bursar']:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    procurements = Procurement.query.all()
    return render_template('procurement/index.html', procurements=procurements)

@app.route('/procurement/create', methods=['GET', 'POST'])
@login_required
def create_procurement():
    if request.method == 'POST':
        procurement = Procurement(
            item_name=request.form.get('item_name'),
            description=request.form.get('description'),
            quantity=int(request.form.get('quantity')),
            unit_price=float(request.form.get('unit_price')),
            total_amount=float(request.form.get('quantity')) * float(request.form.get('unit_price')),
            supplier=request.form.get('supplier'),
            requested_by=current_user.id
        )
        db.session.add(procurement)
        db.session.commit()
        flash('Procurement request created successfully!', 'success')
        return redirect(url_for('procurement'))
    
    return render_template('procurement/create.html')

# API Routes for AJAX calls
@app.route('/api/attendance/today')
@login_required
def api_today_attendance():
    today = datetime.now().date()
    attendances = Attendance.query.filter_by(date=today).all()
    
    data = []
    for attendance in attendances:
        user = User.query.get(attendance.user_id)
        data.append({
            'user_name': user.full_name,
            'role': user.role,
            'time_in': attendance.time_in.strftime('%H:%M') if attendance.time_in else None,
            'time_out': attendance.time_out.strftime('%H:%M') if attendance.time_out else None,
            'status': attendance.status
        })
    
    return jsonify(data)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create default admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@school.com',
                password_hash=generate_password_hash('admin123'),
                role='headteacher',
                full_name='System Administrator'
            )
            db.session.add(admin)
            db.session.commit()
    
    app.run(debug=True, host='0.0.0.0', port=5000) 