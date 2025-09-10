# Staff Management System

A comprehensive web-based staff management system designed for educational institutions. This system provides attendance tracking, performance monitoring, salary management, and administrative tools with biometric authentication capabilities.

## Features

### 🔐 Authentication & Security
- **Multi-role Login System**: Student, Teacher, Headteacher, Deputy, and Bursar access levels
- **Biometric Authentication**: Face recognition and fingerprint scanning support
- **Secure Password Management**: Encrypted password storage with bcrypt
- **Role-based Access Control**: Different permissions for different user types

### 📊 Attendance Management
- **Real-time Check-in/Check-out**: Manual and biometric attendance tracking
- **Face Recognition**: Camera-based face verification system
- **Fingerprint Scanning**: Biometric fingerprint authentication
- **Attendance Reports**: Daily, weekly, and monthly attendance analytics
- **Late Detection**: Automatic late arrival detection and reporting

### 👨‍🏫 Teacher Management
- **Performance Tracking**: 0-10 scale performance scoring system
- **Timetable Management**: Class schedules and room assignments
- **Email/SMS Notifications**: Automated timetable reminders
- **Performance Reports**: Weekly and monthly performance analytics
- **Low Performance Alerts**: Automatic notifications for scores below 7

### 💰 Financial Management (Bursar)
- **Salary Calculation**: Performance-based salary computation
- **Attendance Bonuses**: Automatic bonus calculation based on attendance
- **Performance Bonuses**: Rewards for high-performing staff
- **Payment Tracking**: Salary payment status and history
- **Budget Management**: Financial oversight and reporting

### 📈 Reporting & Analytics
- **Performance Reports**: Teacher performance analysis
- **Attendance Reports**: Comprehensive attendance statistics
- **Salary Reports**: Financial reporting and analysis
- **Export Capabilities**: PDF and Excel export functionality
- **Real-time Dashboards**: Live data visualization

### 🛒 Procurement Management
- **Purchase Requests**: Item procurement tracking
- **Approval Workflow**: Multi-level approval system
- **Budget Monitoring**: Financial oversight of purchases
- **Supplier Management**: Vendor information tracking
- **Status Tracking**: Request status monitoring

### 🔔 Notification System
- **Email Notifications**: Automated email alerts
- **SMS Notifications**: Text message alerts via Twilio
- **System Notifications**: In-app notification system
- **Customizable Alerts**: Configurable notification rules
- **Bulk Messaging**: Mass notification capabilities

## Technology Stack

### Backend
- **Flask**: Python web framework
- **SQLAlchemy**: Database ORM
- **SQLite**: Database (can be upgraded to PostgreSQL/MySQL)
- **Flask-Login**: User session management
- **Werkzeug**: Security utilities

### Frontend
- **Bootstrap 5**: Responsive UI framework
- **Font Awesome**: Icon library
- **jQuery**: JavaScript library
- **Chart.js**: Data visualization (optional)

### Biometric & AI
- **OpenCV**: Computer vision library
- **face_recognition**: Face detection and recognition
- **dlib**: Machine learning library

### External Services
- **Twilio**: SMS notifications
- **SMTP**: Email notifications
- **ReportLab**: PDF generation
- **openpyxl**: Excel file handling

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Web browser with JavaScript enabled

### Setup Instructions

1. **Clone or Download the Project**
   ```bash
   cd C:\Users\user\Desktop\StaffManagementSystem
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   Create a `.env` file in the project root with the following variables:
   ```
   SECRET_KEY=your-secret-key-here
   EMAIL_USER=your-email@gmail.com
   EMAIL_PASSWORD=your-email-password
   TWILIO_ACCOUNT_SID=your-twilio-sid
   TWILIO_AUTH_TOKEN=your-twilio-token
   TWILIO_PHONE_NUMBER=your-twilio-phone
   ```

4. **Run the Application**
   ```bash
   python app.py
   ```

5. **Access the System**
   Open your web browser and navigate to: `http://localhost:5000`

## Default Login Credentials

### Admin Account
- **Username**: admin
- **Password**: admin123
- **Role**: Headteacher

### Demo Teacher Account
- **Username**: teacher
- **Password**: teacher123
- **Role**: Teacher

## User Roles & Permissions

### 👨‍🎓 Student
- View personal attendance records
- Check in/out manually or via biometric
- Access academic information
- Register face for biometric authentication

### 👨‍🏫 Teacher
- All student permissions
- View personal timetable
- Access performance reports
- Receive notifications about classes
- View attendance statistics

### 👨‍💼 Headteacher/Deputy
- All teacher permissions
- View all staff performance reports
- Send notifications to staff
- Access comprehensive analytics
- Manage procurement requests
- Generate reports

### 💰 Bursar
- All administrative permissions
- Calculate and manage salaries
- Monitor financial activities
- Approve procurement requests
- Access financial reports
- Manage budget allocations

## System Architecture

### Database Schema
- **Users**: User accounts and profiles
- **Attendance**: Check-in/out records
- **Timetable**: Class schedules
- **Performance**: Teacher performance scores
- **Salary**: Salary calculations and payments
- **Notifications**: Communication records
- **Procurement**: Purchase requests and approvals

### Security Features
- Password hashing with bcrypt
- Session management with Flask-Login
- Role-based access control
- CSRF protection
- Input validation and sanitization

### API Endpoints
- `/api/attendance/today`: Real-time attendance data
- `/attendance/check-in`: Attendance check-in
- `/attendance/check-out`: Attendance check-out
- `/reports/performance`: Performance reports
- `/salary/calculate`: Salary calculations
- `/notifications/send`: Send notifications

## Configuration

### Email Settings
Configure SMTP settings in the `.env` file for email notifications:
```
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

### SMS Settings
Configure Twilio settings for SMS notifications:
```
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=your-twilio-number
```

### Face Recognition
The face recognition system uses the `face_recognition` library:
- Supports multiple face encodings per user
- Configurable confidence thresholds
- Camera integration ready

## Deployment

### Development
```bash
python app.py
```

### Production
For production deployment, consider:
- Using a production WSGI server (Gunicorn)
- Setting up a reverse proxy (Nginx)
- Using a production database (PostgreSQL/MySQL)
- Implementing SSL/TLS certificates
- Setting up automated backups

## Customization

### Adding New Roles
1. Update the User model in `app.py`
2. Add role-specific routes and templates
3. Update navigation and permissions

### Customizing Reports
1. Modify report generation functions
2. Update template files
3. Add new export formats

### Biometric Integration
1. Implement camera capture functionality
2. Add fingerprint scanner integration
3. Configure recognition thresholds

## Troubleshooting

### Common Issues

1. **Installation Errors**
   - Ensure Python 3.8+ is installed
   - Update pip: `pip install --upgrade pip`
   - Install Visual C++ build tools (Windows)

2. **Face Recognition Issues**
   - Install dlib dependencies
   - Ensure camera permissions
   - Check face_recognition library installation

3. **Email/SMS Notifications**
   - Verify environment variables
   - Check service credentials
   - Test with simple messages first

4. **Database Issues**
   - Ensure write permissions
   - Check database file location
   - Verify SQLite installation

### Support
For technical support or feature requests, please contact the development team.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Version History

- **v1.0.0**: Initial release with core functionality
- Basic attendance tracking
- User management
- Performance monitoring
- Salary calculation
- Notification system

## Future Enhancements

- Mobile app development
- Advanced analytics dashboard
- Integration with school management systems
- Advanced biometric features
- Real-time video monitoring
- AI-powered performance insights
- Multi-language support
- Advanced reporting features 