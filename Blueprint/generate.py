from flask import Blueprint, current_app, flash, redirect, url_for, request, send_file
import io
import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from function.biopsy import predict_biopsy
from function.tumor import predict_tumor, predict_brain_tumor
from function.valid import is_valid_biopsy
from models import Patient, Doctor
from app import db

generate_bp = Blueprint('generate', __name__, template_folder='../templates')

@generate_bp.route('/generate_report/<int:patient_id>', methods=['POST'])
def generate_report(patient_id):
    patient = Patient.query.get(patient_id)
    if not patient:
        flash("Patient not found!", "danger")
        return redirect(url_for('dashboard.doctor_dashboard'))

    # Doctor name (assuming one doctor in DB or linked to patient)
    doctor = Doctor.query.first()  # ya patient.doctor_id se fetch karen agar relation ho
    doctor_name = doctor.username if doctor else "N/A"

    report_type = request.form.get('report_type')  # 'bone' or 'brain'
    report_filename = f"patient_{patient.id}_{report_type}_report.pdf"
    report_path = os.path.join(current_app.config['REPORT_FOLDER'], report_filename)

    # Initialize results
    xray_result, xray_confidence = "No X-ray uploaded", 0
    biopsy_result = "Not applicable"
    biopsy_included = False
    biopsy_error = None
    mri_result, mri_confidence = "No MRI uploaded", None

    # Bone X-ray & Biopsy
    if patient.xray_image:
        xray_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], patient.xray_image)
        xray_result, xray_confidence = predict_tumor(xray_image_path)

        if xray_result == "Tumor Detected" and patient.biopsy_file:
            biopsy_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], patient.biopsy_file)
            if not is_valid_biopsy(biopsy_image_path):
                biopsy_error = "Invalid biopsy image. Could not process biopsy."
            else:
                biopsy_result = predict_biopsy(biopsy_image_path)
                biopsy_included = True

    # Brain MRI
    if patient.brain_mri_image:
        mri_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], patient.brain_mri_image)
        mri_result, mri_confidence = predict_brain_tumor(mri_image_path)

    # Create PDF
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Logo
    logo_path = os.path.join(current_app.config['STATIC_FOLDER'], 'images', 'logo.jpg')
    pdf.drawImage(logo_path, 50, height - 120, width=80, height=80, mask='auto')

    # Title
    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawCentredString(width / 2, height - 70, "OncoDetect - Patient Report")

    # Doctor & Date
    pdf.setFont("Helvetica", 12)
    pdf.drawString(400, height - 110, f"Doctor: {doctor_name}")
    pdf.drawString(400, height - 130, f"Date: {datetime.now().strftime('%b %d, %Y')}")

    # Patient Info Box
    pdf.setFillColor(colors.lightgrey)
    pdf.roundRect(50, height - 220, width - 100, 70, 10, fill=1, stroke=0)
    pdf.setFillColor(colors.black)
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(60, height - 190, "Patient Information:")
    pdf.setFont("Helvetica", 11)
    pdf.drawString(60, height - 210, f"Name: {patient.username}   |   Email: {patient.email}   |   Age: {patient.age}   |   Gender: {patient.gender}  |   Phone: {patient.phone_number}" )

    # Test Results Table
    table_data = [["Test Type", "Result", "Confidence", "Notes"]]
    if report_type == "bone":
        table_data.append([
            "X-ray",
            xray_result,
            f"{xray_confidence:.2f}%" if xray_confidence else "N/A",
            "Detected using uploaded X-ray image"
        ])
        table_data.append([
            "Biopsy",
            biopsy_result if biopsy_included else "N/A",
            "-",
            "Based on uploaded biopsy" if biopsy_included else (biopsy_error or "No biopsy uploaded")
        ])
    elif report_type == "brain":
        table_data.append([
            "Brain MRI",
            mri_result,
            f"{mri_confidence:.2f}%" if mri_confidence else "N/A",
            "Based on uploaded MRI scan"
        ])

    table = Table(table_data, colWidths=[100, 120, 80, 200])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#b3d9ff')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    table.wrapOn(pdf, width, height)
    table.drawOn(pdf, 60, height - 320)

    # Suggestions Section
    pdf.setFont("Helvetica-Bold", 13)
    pdf.setFillColor(colors.HexColor('#007acc'))
    pdf.drawString(60, height - 340, "Suggestions:")
    pdf.setFillColor(colors.black)
    pdf.setFont("Helvetica", 11)

    suggestions = []
    if report_type == "bone":
        if xray_result == "Tumor Detected":
            suggestions = [
                "• Consult an orthopedic oncologist immediately.",
                "• Schedule a biopsy if not already done.",
                "• Avoid strenuous activity until cleared by your doctor."
            ]
        else:
            suggestions = ["• No tumor detected in bone X-ray. Maintain regular checkups."]

    elif report_type == "brain":
        # Brain tumor specific suggestions based on class
        if mri_result.lower() == "glioma":
            suggestions = [
                "• Glioma detected: Consult a neuro-oncologist promptly.",
                "• Consider MRI with contrast for detailed imaging.",
                "• Discuss treatment options including surgery, radiation, and chemotherapy."
            ]
        elif mri_result.lower() == "pituitary":
            suggestions = [
                "• Pituitary tumor detected: Consult an endocrinologist and neurosurgeon.",
                "• Monitor hormone levels regularly.",
                "• Treatment may include surgery or medication."
            ]
        elif mri_result.lower() == "meningioma":
            suggestions = [
                "• Meningioma detected: Consult a neurosurgeon.",
                "• Regular imaging to monitor tumor growth.",
                "• Surgery may be recommended depending on symptoms."
            ]
        elif mri_result in ["No Tumor Detected", "Normal"]:
            suggestions = [
                "• No brain tumor detected. Continue routine monitoring and follow-up."
            ]
        else:
           
            suggestions = [
                "• Brain MRI result unclear. Please consult your neurologist for further evaluation."
            ]

    for i, line in enumerate(suggestions):
        pdf.drawString(75, height - 360 - (i * 18), line)

    # Footer
    pdf.setFont("Helvetica-Oblique", 9)
    pdf.setFillColor(colors.grey)
    pdf.drawCentredString(width / 2, 30, "For more info, visit www.oncodetect.com or email support@oncodetect.com")

    # Finalize PDF
    pdf.save()
    buffer.seek(0)
    pdf_bytes = buffer.getvalue()

    # Save PDF to disk
    with open(report_path, 'wb') as f:
        f.write(pdf_bytes)

    # Save to database
    if report_type == "brain":
        patient.brain_report_pdf = report_filename
    else:
        patient.report_pdf = report_filename
    db.session.commit()

    return send_file(
        io.BytesIO(pdf_bytes),
        as_attachment=True,
        download_name=report_filename,
        mimetype='application/pdf'
    )
