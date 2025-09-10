#!/usr/bin/env python3
"""
Staff Management System Startup Script
"""

import os
import sys
from app import app, db

def create_sample_data():
    """Create sample data for demonstration"""
    from app import User, Timetable
    from werkzeug.security import generate_password_hash
    from datetime import time
    
    # Create sample teacher
    teacher = User.query.filter_by(username='teacher').first()
    if not teacher:
        teacher = User(
            username='teacher',
            email='teacher@school.com',
            password_hash=generate_password_hash('teacher123'),
            role='teacher',
            full_name='John ',
            phone_number='+1234567890'
        )
        db.session.add(teacher)
        db.session.commit()
        
        # Add sample timetable
        timetable = Timetable(
            teacher_id=teacher.id,
            subject='Mathematics',
            day_of_week='Monday',
            start_time=time(8, 0),
            end_time=time(9, 0),
            room='Room 101',
            class_name='Class 10A'
        )
        db.session.add(timetable)
        
        timetable2 = Timetable(
            teacher_id=teacher.id,
            subject='Mathematics',
            day_of_week='Tuesday',
            start_time=time(9, 0),
            end_time=time(10, 0),
            room='Room 102',
            class_name='Class 10B'
        )
        db.session.add(timetable2)
        db.session.commit()

def main():
    """Main startup function"""
    print("=" * 50)
    print("Staff Management System")
    print("=" * 50)
    
    # Check if database exists
    if not os.path.exists('staff_management.db'):
        print("Creating database...")
        with app.app_context():
            db.create_all()
            create_sample_data()
        print("Database created successfully!")
    
    print("\nStarting the application...")
    print("Access the system at: http://localhost:5000")
    print("Default admin login: admin / admin123")
    print("Default teacher login: teacher / teacher123")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 50)
    
    # Run the application
    app.run(
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('DEBUG', 'True').lower() == 'true'
    )

if __name__ == '__main__':
    main() 