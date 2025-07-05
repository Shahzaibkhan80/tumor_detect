import re
from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for, jsonify
from models import Admin, Doctor, Patient
from werkzeug.security import check_password_hash, generate_password_hash
from app import db, mail
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer



login_bp = Blueprint('login', __name__, template_folder='../templates')

# ------------------ Admin Login ------------------
@login_bp.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']


        admin = Admin.query.filter_by(email=email, username=username).first()
        if admin:
            if check_password_hash(admin.password, password):
                session['admin_id'] = admin.id
                return redirect(url_for('dashboard.admin_dashboard'))
            else:
                return render_template('admin_login.html', error='Invalid password')

    return render_template('admin_login.html')

@login_bp.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)  
    return redirect(url_for('login.admin_login'))  

# ------------------ Patient Signup ------------------
@login_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        age = request.form['age']
        gender = request.form['gender']
        phone_number = request.form['phone_number']

        print(f"[SIGNUP] Received: username={username}, email={email}, password={password}, age={age}, gender={gender}, phone={phone_number}")

        # Username validation: only letters
        if not re.match(r"^[A-Za-z]+$", username):
            print("[SIGNUP] Username validation failed")
            flash("Username can only contain letters (no numbers or special characters).", "danger")
            return redirect(url_for('login.signup'))

        # Email validation (basic)
        if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
            print("[SIGNUP] Email validation failed")
            flash("Please enter a valid email address.", "danger")
            return redirect(url_for('login.signup'))

        # Password validation: 8-12 chars, at least one uppercase letter, one special char
        if not re.match(r"^(?=.*[A-Z])(?=.*[!@#$%^&*()_+{}\[\]:;<>,.?~\\/-]).{8,12}$", password):
            print("[SIGNUP] Password validation failed")
            flash("Password must be 8-12 characters long, include at least one uppercase letter and one special character.", "danger")
            return redirect(url_for('login.signup'))

        # Phone number validation: digits only, max 11 digits
        if not re.match(r"^\d{1,11}$", phone_number):
            print("[SIGNUP] Phone validation failed")
            flash("Phone number must contain only digits and be maximum 11 digits long.", "danger")
            return redirect(url_for('login.signup'))

        # Check for existing user
        existing_user = Patient.query.filter((Patient.username == username) | (Patient.email == email)).first()
        print(f"[SIGNUP] Existing user: {existing_user}")
        if existing_user:
            print("[SIGNUP] Username or email already exists")
            flash('Username or email already exists. Please try again.', 'danger')
            return redirect(url_for('login.signup'))

        # Add new user
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        print(f"[SIGNUP] Hashed password: {hashed_password}")
        new_patient = Patient(
            username=username,
            email=email,
            password=hashed_password,
            age=age,
            gender=gender,
            phone_number=phone_number
            
        )
        db.session.add(new_patient)
        db.session.commit()
        print(f"[SIGNUP] New patient created with id: {new_patient.id}")

        flash('Account created successfully! You can now login.', 'success')
        return redirect(url_for('login.login'))

    return render_template('signup.html')

# ------------------ Login (Doctor/Patient) ------------------
@login_bp.route('/login', methods=['GET', 'POST']) 
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

        print(f"[LOGIN] Attempt: username={username}, role={role}, password={password}")

        if not username or not password or not role:
            print("[LOGIN] Missing fields")
            return jsonify({'success': False, 'message': 'Please fill in all fields.'})

        if role == 'Doctor':
            doctor = Doctor.query.filter_by(username=username).first()
            print(f"[LOGIN] Doctor found: {doctor}")
            if doctor:
                print(f"[LOGIN] Doctor password hash: {doctor.password}")
                print(f"[LOGIN] Password check: {check_password_hash(doctor.password, password)}")
            if doctor and check_password_hash(doctor.password, password):
                print("[LOGIN] Doctor login success")
                session['doctor_id'] = doctor.id
                return jsonify({'success': True, 'redirect_url': url_for('dashboard.doctor_dashboard')})
            print("[LOGIN] Doctor login failed")
            return jsonify({'success': False, 'message': 'Invalid doctor credentials.'})

        elif role == 'Patient':
            patient = Patient.query.filter(Patient.username.ilike(username)).first()
            print(f"[LOGIN] Patient found: {patient}")
            if patient:
                print(f"[LOGIN] Patient password hash: {patient.password}")
                print(f"[LOGIN] Password check: {check_password_hash(patient.password, password)}")
            if patient and check_password_hash(patient.password, password):
                print("[LOGIN] Patient login success")
                session['patient_id'] = patient.id
                return jsonify({'success': True, 'redirect_url': url_for('dashboard.patient_dashboard', patient_id=patient.id)})
            print("[LOGIN] Patient login failed")
            return jsonify({'success': False, 'message': 'Invalid patient credentials.'})

    return render_template('login.html')  

# ------------------ Forgot Password (Patient) ------------------
@login_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'success': False, 'message': 'Email is required'}), 400

    user = Patient.query.filter_by(email=email).first()
    if not user:
        return jsonify({'success': False, 'message': 'Email not found'}), 404

    token = generate_token(user.email)
    reset_url = url_for('login.reset_password', token=token, _external=True)

    msg = Message('Password Reset Request',
              sender=current_app.config['MAIL_DEFAULT_SENDER'],
              recipients=[user.email])
    msg.html = f'''
        <p>To reset your password, click the link below:</p>
        <p><a href="{reset_url}">{reset_url}</a></p>
        <p>If you did not request this, please ignore this email.</p>
    '''
    try:
        mail.send(msg)
        return jsonify({'success': True, 'message': 'Password reset email sent'}), 200
    except Exception as e:
        current_app.logger.error(f"Email sending failed: {e}")
        return jsonify({'success': False, 'message': 'Failed to send email'}), 500

@login_bp.route('/forgot-password-page', methods=['GET'])
def forgot_password_page():
    return render_template('forgot_password.html')

# ------------------ Reset Password (Patient) ------------------
@login_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = verify_token(token)
    if not email:
        flash('Invalid or expired token.', 'danger')
        return redirect(url_for('login.login')) 

    user = Patient.query.filter_by(email=email).first()
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('login.login'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not password or not confirm_password:
            flash('Please fill out both password fields.', 'warning')
            return render_template('reset_password.html', token=token)

        if password != confirm_password:
            flash('Passwords do not match.', 'warning')
            return render_template('reset_password.html', token=token)

        user.password = generate_password_hash(password, method='pbkdf2:sha256')
        db.session.commit()
        flash('Your password has been reset successfully. You can now login.', 'success')
        return redirect(url_for('login.login'))

    # GET request: render reset password form
    return render_template('reset_password.html', token=token)

# ------------------ Token Helpers ------------------
def generate_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='password-reset-salt')

def verify_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=expiration)
    except Exception:
        return None
    return email
