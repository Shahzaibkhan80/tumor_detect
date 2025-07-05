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

    # Check if a biopsy file is already uploaded
    # if patient.biopsy_file:
    #     flash("Biopsy has already been uploaded for this patient.", "info")
    #     return redirect(url_for('view_biopsy', patient_id=patient.id))  # Redirect to the view biopsy page

    if request.method == 'POST':
        # Handle file upload
        biopsy_file = request.files.get('biopsy_file')
        
        # Check if file is selected and is valid
        if biopsy_file and allowed_file(biopsy_file.filename):
            filename = secure_filename(f"biopsy_{uuid.uuid4().hex}_{biopsy_file.filename}")
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

            try:
                # Temporarily save the file for validation
                biopsy_file.save(filepath)

                # Validate if the uploaded file is a valid image
                if not is_valid_biopsy(filepath):
                    os.remove(filepath)  # Remove invalid file
                    flash("Uploaded file is not a valid image. Please upload a valid biopsy image.", "danger")
                    return redirect(url_for('upload.upload_biopsy', patient_id=patient.id))

                # Use the model to predict whether the image is benign or malignant
                biopsy_result = predict_biopsy(filepath)

                if biopsy_result:  # If prediction returns benign or malignant
                    patient.biopsy_file = filename
                    patient.biopsy_result = biopsy_result  # Save result in database
                    db.session.commit()

                    flash(f"Biopsy uploaded successfully. Tumor classified as {biopsy_result}.", "success")
                    return redirect(url_for('dashboard.doctor_dashboard'))  # Redirect after success
                else:
                    os.remove(filepath)  # Remove file if unable to classify
                    flash("Could not classify the tumor. Please try again with a different image.", "danger")
                    return redirect(url_for('upload.upload_biopsy', patient_id=patient.id))

            except Exception as e:
                os.remove(filepath)  # Remove the file in case of error
                flash(f"Error during biopsy upload: {e}", "danger")
                return redirect(url_for('upload.upload_biopsy', patient_id=patient.id))

        flash("Invalid file type or no file uploaded. Please upload a valid image file.", "danger")
        return redirect(url_for('upload.upload_biopsy', patient_id=patient.id))

    return render_template('upload_biopsy.html', patient=patient)

@upload_bp.route('/upload/upload_bonesxray/<int:patient_id>', methods=['GET', 'POST'])
def upload_bonesxray(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    if request.method == 'POST':
        # Check if file is part of the request
        if 'xray_image' not in request.files:
            flash('No file part', 'danger')
            return redirect(url_for('upload.upload_bonesxray', patient_id=patient.id))

        xray_image = request.files['xray_image']

        if xray_image.filename == '':
            flash('No selected file', 'danger')
            return redirect(url_for('upload.upload_bonesxray', patient_id=patient.id))

        # Check if the file is allowed
        if xray_image and allowed_file(xray_image.filename):
            filename = secure_filename(f"{uuid.uuid4().hex}_{xray_image.filename}")
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

            try:
                # Save the file temporarily for validation
                xray_image.save(filepath)

                # Validate if the image is an X-ray
                if not validate_xray_image(filepath):
                    os.remove(filepath)  # Invalid image, delete it
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
        # Check if the file part exists in the request
        if 'brain_mri_image' not in request.files:
            flash('No file part', 'danger')
            return redirect(url_for('upload.upload_brainmri', patient_id=patient.id))

        brain_mri_image = request.files['brain_mri_image']

        if brain_mri_image.filename == '':
            flash('No selected file', 'danger')
            return redirect(url_for('upload.upload_brainmri', patient_id=patient.id))

        # Validate file type
        if brain_mri_image and allowed_file(brain_mri_image.filename):
            # Save the file with a unique filename
            filename = secure_filename(f"{uuid.uuid4().hex}_{brain_mri_image.filename}")
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

            try:
                # Save the MRI image temporarily
                brain_mri_image.save(filepath)

                # Save the filename to the patient's record
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


