import os
import uuid
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from function.biopsy import predict_biopsy
from function.helpers import allowed_file
from function.valid import is_valid_biopsy, is_valid_xray, validate_xray_image
from models import Patient
from app import db

upload_bp = Blueprint('upload', __name__, template_folder='../templates')

@upload_bp.route('/upload_biopsy/<int:patient_id>', methods=['GET', 'POST'])
def upload_biopsy(patient_id):
    patient = Patient.query.get_or_404(patient_id)

   
    if request.method == 'POST':
        biopsy_file = request.files.get('biopsy_file')
        
        if biopsy_file and allowed_file(biopsy_file.filename):
            filename = secure_filename(f"biopsy_{uuid.uuid4().hex}_{biopsy_file.filename}")
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

            try:
                biopsy_file.save(filepath)

                if not is_valid_biopsy(filepath):
                    os.remove(filepath)  
                    flash("Uploaded file is not a valid image. Please upload a valid biopsy image.", "danger")
                    return redirect(url_for('upload.upload_biopsy', patient_id=patient.id))

                biopsy_result = predict_biopsy(filepath)

                if biopsy_result:  
                    patient.biopsy_file = filename
                    patient.biopsy_result = biopsy_result 
                    db.session.commit()

                    flash(f"Biopsy uploaded successfully. Tumor classified as {biopsy_result}.", "success")
                    return redirect(url_for('dashboard.doctor_dashboard'))  
                else:
                    flash("Could not classify the tumor. Please try again with a different image.", "danger")
                    return redirect(url_for('upload.upload_biopsy', patient_id=patient.id))

            except Exception as e:
                os.remove(filepath)  
                flash(f"Error during biopsy upload: {e}", "danger")
                return redirect(url_for('upload.upload_biopsy', patient_id=patient.id))

        flash("Invalid file type or no file uploaded. Please upload a valid image file.", "danger")
        return redirect(url_for('upload.upload_biopsy', patient_id=patient.id))

    return render_template('upload_biopsy.html', patient=patient)

@upload_bp.route('/upload/upload_bonesxray/<int:patient_id>', methods=['GET', 'POST'])
def upload_bonesxray(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    if request.method == 'POST':
        if 'xray_image' not in request.files:
            flash('No file part', 'danger')
            return redirect(url_for('upload.upload_bonesxray', patient_id=patient.id))

        xray_image = request.files['xray_image']

        if xray_image.filename == '':
            flash('No selected file', 'danger')
            return redirect(url_for('upload.upload_bonesxray', patient_id=patient.id))

        if xray_image and allowed_file(xray_image.filename):
            filename = secure_filename(f"{uuid.uuid4().hex}_{xray_image.filename}")
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

            try:
                xray_image.save(filepath)

                if not validate_xray_image(filepath):
                    os.remove(filepath)  
                    flash('Invalid file! Only X-ray images are allowed.', 'danger')
                    return redirect(url_for('upload.upload_bonesxray', patient_id=patient.id))

                # Save the valid X-ray file path to the database
                patient.xray_image = filename
                db.session.commit()

                flash('X-ray image uploaded successfully!', 'success')
                return redirect(url_for('upload.upload_bonesxray', patient_id=patient.id))
            except Exception as e:
                flash(f"Error uploading X-ray image: {e}", 'danger')
                return redirect(url_for('upload.upload_bonesxray', patient_id=patient.id))
        else:
            flash('Invalid file type. Please upload a valid image.', 'danger')
            return redirect(url_for('upload.upload_bonesxray', patient_id=patient.id))
    
    return render_template('upload_bonesxray.html', patient=patient)




@upload_bp.route('/upload/upload_brainmri/<int:patient_id>', methods=['GET', 'POST'])
def upload_brainmri(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    if request.method == 'POST':
        if 'brain_mri_image' not in request.files:
            flash('No file part', 'danger')
            return redirect(url_for('upload.upload_brainmri', patient_id=patient.id))

        brain_mri_image = request.files['brain_mri_image']

        if brain_mri_image.filename == '':
            flash('No selected file', 'danger')
            return redirect(url_for('upload.upload_brainmri', patient_id=patient.id))

        if brain_mri_image and allowed_file(brain_mri_image.filename):
            filename = secure_filename(f"{uuid.uuid4().hex}_{brain_mri_image.filename}")
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

            try:
                brain_mri_image.save(filepath)

                patient.brain_mri_image = filename
                db.session.commit()

                flash('MRI image uploaded successfully!', 'success')
                return redirect(url_for('upload.upload_brainmri', patient_id=patient.id))
            except Exception as e:
                flash(f"Error uploading MRI image: {e}", 'danger')
                return redirect(url_for('upload.upload_brainmri', patient_id=patient.id))
        else:
            flash('Invalid file type. Please upload a valid image.', 'danger')
            return redirect(url_for('upload.upload_brainmri', patient_id=patient.id))
    
    return render_template('upload_brainMri.html', patient=patient)


