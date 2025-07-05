from flask import Blueprint, flash, make_response, redirect, render_template, request, session, url_for, current_app
from werkzeug.utils import secure_filename
import os
import uuid
from models import Admin, Doctor, Patient
from function.helpers import allowed_file
from function.tumor import predict_brain_tumor, predict_tumor
from function.valid import validate_xray_image
from app import db
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__, template_folder='../templates')
def nocache(view):
    def no_cache_wrapper(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    no_cache_wrapper.__name__ = view.__name__
    return no_cache_wrapper

###Admin dashboard
@dashboard_bp.route('/admin_dashboard', methods=['GET'])
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('login.login'))

    doctors = Doctor.query.all()
    patients = Patient.query.all()
    total_doctors = len(doctors)
    total_patients = len(patients)
    admin = Admin.query.get(session['admin_id'])

    # Diagnosis summary
    diagnosis_counts = (
        Patient.query
        .with_entities(Patient.result, func.count(Patient.id))
        .group_by(Patient.result)
        .all()
    )
    chart_labels = [d[0] if d[0] else "Unknown" for d in diagnosis_counts]
    chart_data = [d[1] for d in diagnosis_counts]

    return render_template(
        'admin_dashboard.html',
        admin=admin,
        total_doctors=total_doctors,
        total_patients=total_patients,
        chart_labels=chart_labels,
        chart_data=chart_data
    )


@dashboard_bp.route('/add_doctor', methods=['GET', 'POST'])
def add_doctor():
    if 'admin_id' not in session:
        return redirect(url_for('login.admin_login'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')  
        password = request.form.get('password')
        specialization = request.form.get('specialization')
        phone = request.form.get('phone')

        if not username or not password:
            flash('Username and Password are required!', 'danger')
            return render_template('add_doctor.html')

        # Check if doctor with this username already exists
        existing_doctor = Doctor.query.filter_by(username=username).first()
        if existing_doctor:
            flash('Doctor with this username already exists.', 'danger')
            return render_template('add_doctor.html')

        new_doctor = Doctor(username=username, email=email,password=password, specialization=specialization, phone=phone)
        db.session.add(new_doctor)
        db.session.commit()

        flash('Doctor added successfully!', 'success')
        return redirect(url_for('dashboard.admin_dashboard'))

    return render_template('add_doctor.html')


@dashboard_bp.route('/view_patients')
def view_patients():
    if 'admin_id' not in session:
        return redirect(url_for('login.admin_login'))
    patients = Patient.query.all()
    return render_template('patient_view.html', patients=patients)

# Example route


@dashboard_bp.route('/delete_patient/<int:patient_id>', methods=['POST'])
def delete_patient(patient_id):
    if 'admin_id' not in session:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('login.admin_login'))

    patient = Patient.query.get_or_404(patient_id)

    if patient.xray_image or patient.brain_mri_image:
        flash('Cannot delete patient with uploaded scans.', 'warning')
        return redirect(url_for('dashboard.view_patients'))

    db.session.delete(patient)
    db.session.commit()
    flash('Patient deleted successfully.', 'success')
    return redirect(url_for('dashboard.view_patients'))

# @dashboard_bp.route('/edit_patient/<int:patient_id>', methods=['GET', 'POST'])
# def edit_patient(patient_id):
#     if 'admin_id' not in session:
#         flash('Unauthorized access.', 'danger')
#         return redirect(url_for('login.admin_login'))

#     patient = Patient.query.get_or_404(patient_id)

#     if request.method == 'POST':
#         patient.name = request.form['name']
#         patient.age = request.form['age']
#         patient.gender = request.form['gender']
#         # Add more fields as needed
#         db.session.commit()
#         flash('Patient updated successfully.', 'success')
#         return redirect(url_for('dashboard.view_patients'))

#     return render_template('edit_patient.html', patient=patient)

###doctor dashboard
@dashboard_bp.route('/doctor_dashboard', methods=['GET', 'POST'])
def doctor_dashboard():
    if 'doctor_id' not in session:
        flash('You must be logged in as a doctor to access the dashboard.', 'danger')
        return redirect(url_for('login.login'))
    patients = Patient.query.order_by(Patient.id.desc()).all()

    gender_counts = {'Male': 0, 'Female': 0}
    xray_counts = {'Bone': 0, 'Brain': 0}
    tumor_data = {
        'Bone Tumor': 0,
        'Bone Non-Tumor': 0,
        'Brain Tumor': 0,
        'Brain Non-Tumor': 0,
    }
    brain_class_counts = {
        'Glioma Tumor': 0,
        'Meningioma Tumor': 0,
        'Pituitary Tumor': 0,
        'No Tumor': 0
    }
    seen_count = 0
    unseen_count = 0

    for p in patients:
        # Gender
        gender = (p.gender or '').capitalize()
        if gender in gender_counts:
            gender_counts[gender] += 1

        # Bone X-ray
        if p.xray_image:
            xray_counts['Bone'] += 1
            tumor_stage = (p.tumor_stage or '').strip().lower()
            if tumor_stage and tumor_stage != 'normal':
                tumor_data['Bone Tumor'] += 1
            else:
                tumor_data['Bone Non-Tumor'] += 1

        # Brain MRI
        if p.brain_mri_image:
            xray_counts['Brain'] += 1
            brain_class = (p.brain_mri_class or '').strip().title()
            print(f"Brain MRI Class: {p.brain_mri_class}")

            if brain_class != 'No Tumor':
                tumor_data['Brain Tumor'] += 1
            else:
                tumor_data['Brain Non-Tumor'] += 1

            if brain_class + " Tumor" in brain_class_counts:
                brain_class_counts[brain_class + " Tumor"] += 1
            elif brain_class == "No Tumor":
                brain_class_counts["No Tumor"] += 1

        # Seen/Unseen
        if p.report_pdf or p.brain_report_pdf:
            seen_count += 1
        else:
            unseen_count += 1

    return render_template("doctor_dashboard.html",
                           gender_counts=gender_counts,
                           xray_counts=xray_counts,
                           seen_count=seen_count,
                           unseen_count=unseen_count,
                           tumor_data=tumor_data,
                           brain_class_counts=brain_class_counts,
                           recent_patients=patients[:5],
                           total_patients=len(patients))


@dashboard_bp.route('/doctor/brain_mri_reports')
def brain_mri_reports():
    if 'doctor_id' not in session:
        flash('You must be logged in as a doctor to access the dashboard.', 'danger')
        return redirect(url_for('login.login'))

    doctor = Doctor.query.get_or_404(session['doctor_id'])

    patients = Patient.query.filter(Patient.brain_mri_image.isnot(None)).all()

    for patient in patients:
        if patient.brain_mri_image:
            mri_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], patient.brain_mri_image)
            
            if os.path.exists(mri_image_path):
                predicted_class, confidence = predict_brain_tumor(mri_image_path)

                patient.brain_mri_class = predicted_class
                patient.brain_mri_confidence = confidence
            else:
                flash(f"Image for patient {patient.id} not found. Prediction skipped.", 'warning')

    db.session.commit()

    return render_template('doctor_mri_reports.html', patients=patients, doctor=doctor)


@dashboard_bp.route('/doctor/bones_xray_reports')
def bones_xray_reports():
    if 'doctor_id' not in session:
        return redirect(url_for('login.login')) 

    doctor = Doctor.query.get_or_404(session['doctor_id'])
    patients = Patient.query.filter(Patient.xray_image.isnot(None)).all()
    for patient in patients:
        if patient.xray_image:
            xray_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], patient.xray_image)

            result, confidence = predict_tumor(xray_image_path)

            if result == "Tumor Detected":
                patient.tumor_stage = "Tumor Detected"
            else:
                patient.tumor_stage = "Normal"
            db.session.commit()

    return render_template('doctor_bones_reports.html', patients=patients, doctor=doctor)

##Patient dashboard
@dashboard_bp.route('/patient_dashboard/<int:patient_id>', methods=['GET','POST'])
@nocache
def patient_dashboard(patient_id):
    if 'patient_id' not in session or session['patient_id'] != patient_id:
        return redirect(url_for('login.login', patient_id=patient_id))
    patient = Patient.query.get_or_404(patient_id)
    return render_template('patient_dashboard.html', patient=patient)



@dashboard_bp.route('/about_doctor')
def about_doctor():
    return render_template('about_doctor.html')

@dashboard_bp.route('/about_patient', methods=['GET'])
def about_patient():
    patients = Patient.query.all()  
    return render_template('about_patient.html', patients=patients)

@dashboard_bp.route('/view_report/<int:patient_id>', methods=['GET'])
def view_report(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    bone_report_available = bool(patient.report_pdf)
    brain_report_available = bool(patient.brain_report_pdf)

    return render_template('view_report.html', patient=patient,
                           bone_report_available=bone_report_available,
                           brain_report_available=brain_report_available)



@dashboard_bp.route('/profile/<int:patient_id>', methods=['GET'])
def profile(patient_id):
    patient = Patient.query.get_or_404(patient_id)  
    return render_template('profile.html', patient=patient)

@dashboard_bp.route('/hospital_info/<int:patient_id>', methods=['GET', 'POST'])
def hospital_info(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    
    brain_class = (patient.brain_mri_class or '').lower()
    tumor_stage = (patient.tumor_stage or '').lower()

    brain_tumors = ['glioma', 'meningioma', 'pituitary']
    brain_has_tumor = brain_class in brain_tumors
    bone_has_tumor = tumor_stage != 'normal' and tumor_stage != ''

    if not brain_has_tumor and not bone_has_tumor:
        return render_template('hospital_info.html', patient=patient, show_hospitals=False)
    def hospital_info(patient_id):
   # ya jo logic aap use kar rahe hain

      if request.method == 'POST':
        selected_price = int(request.form['price'])  # Text box se price
        # Filter hospitals based on selected_price
        hospitals = Hospital.query.filter(Hospital.cost <= selected_price).all()
    selected_price = None
    hospitals = [
        {'name': 'Aga Khan Hospital', 'city': 'Karachi', 'address': 'https://maps.app.goo.gl/sGGdGCrQQ4KeTUkB6', 'cost': 500000},
        {'name': 'PIMS', 'city': 'Islamabad', 'address': 'https://www.google.com/maps/place/PIMS+Islamabad', 'cost': 0},
        {'name': 'Shaukat Khanum Memorial Hospital', 'city': 'Lahore', 'address': 'https://www.google.com/maps/place/Shaukat+Khanum+Memorial+Cancer+Hospital+%26+Research+Centre', 'cost': 1000000},
        {'name': 'KRL Hospital', 'city': 'Islamabad', 'address': 'https://www.google.com/maps/place/KRL+Hospital+Islamabad ', 'cost': 300000},
        {'name': 'Indus Hospital', 'city': 'Karachi', 'address': 'https://www.google.com/maps/place/The+Indus+Hospital', 'cost': 0},
        {'name': 'Liaquat University Hospital', 'city': 'Hyderabad', 'address': 'https://www.google.com/maps/place/Liaquat+University+Hospital', 'cost': 500000},
        {'name': 'Fatima Memorial Hospital', 'city': 'Lahore', 'address': 'https://www.google.com/maps/place/Fatima+Memorial+Hospital', 'cost': 1000000},
        {'name': 'Civil Hospital', 'city': 'Karachi', 'address': 'https://www.google.com/maps/place/Dr.+Ruth+K.M.+Pfau+Civil+Hospital+Karachi', 'cost': 0},
        {'name': 'Jinnah Postgraduate Medical Centre', 'city': 'Karachi', 'address': 'https://www.google.com/maps/place/Jinnah+Postgraduate+Medical+Centre', 'cost': 300000},
        {'name': 'Pakistan Institute of Medical Sciences', 'city': 'Islamabad', 'address': 'https://www.google.com/maps/place/PIMS+Islamabad', 'cost': 500000},
        {'name': 'Khyber Teaching Hospital', 'city': 'Peshawar', 'address': 'https://www.google.com/maps/place/Khyber+Teaching+Hospital', 'cost': 1000000},
        {'name': 'Lady Reading Hospital', 'city': 'Peshawar', 'address': 'https://www.google.com/maps/place/Lady+Reading+Hospital', 'cost': 0},
    ]

    # Generate unique and sorted price options
    unique_prices = sorted(set(h['cost'] for h in hospitals))
    prices = [{'label': 'Free or Minimal Charges', 'value': 0} if p == 0 else {'label': f"{p} PKR", 'value': p} for p in unique_prices]

    filtered = hospitals  # Default to all hospitals

    if request.method == 'POST':
        try:
            selected_price = int(request.form['price'])
            filtered = [hospital for hospital in hospitals if hospital['cost'] == selected_price]
        except ValueError:
            selected_price = None
            filtered = []

    return render_template('hospital_info.html', patient=patient, prices=prices,
                           selected_price=selected_price, hospitals=filtered, show_hospitals=True)


@dashboard_bp.route('/logout/<int:patient_id>', methods=['GET', 'POST'])
def logout(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    if 'patient_id' in session:
        session.pop('patient_id', None)
        flash('You have been logged out successfully.', 'success')
    else:
        flash('You are not logged in.', 'warning')
    return redirect(url_for('login.login', patient_id=patient.id))

