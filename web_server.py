from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
import uuid
from datetime import datetime
from patient import Patient
from doctor import Doctor
from utilities import assign_doctor_to_patient
from data_storage import save_patient_to_json, save_doctor_to_json, patients, doctors
from main import load_patients, load_doctors
load_patients()
load_doctors()

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)


# --------------------- FLASK ROUTES ---------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/patients', methods=['GET'])
def get_patients():
    try:
        patients_data = {}
        for patient_id, patient in patients.items():
            patients_data[patient_id] = patient.to_dict()
        
        return jsonify({
            'success': True,
            'data': patients_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/doctors', methods=['GET'])
def get_doctors():
    try:
        doctors_data = {}
        for doctor_id, doctor in doctors.items():
            doctors_data[doctor_id] = doctor.to_dict()
        
        return jsonify({
            'success': True,
            'data': doctors_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/patients/<patient_id>', methods=['GET'])
def get_patient(patient_id):
    try:
        if patient_id not in patients:
            return jsonify({
                'success': False,
                'error': 'Patient not found'
            }), 404
        
        patient = patients[patient_id]
        return jsonify({
            'success': True,
            'data': patient.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/doctors', methods=['POST'])
def register_doctor():
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        specialization = data.get('specialization', '').strip()
        
        if not name or not specialization:
            return jsonify({
                'success': False,
                'error': 'Name and specialization are required'
            }), 400
        
        doctor = Doctor(name, specialization)
        doctors[doctor.id] = doctor
        save_doctor_to_json(doctor)
        
        return jsonify({
            'success': True,
            'message': f'Doctor registered successfully with ID: {doctor.id}',
            'data': doctor.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/patients', methods=['POST'])
def register_patient():
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        age = data.get('age', '')
        gender = data.get('gender', '').strip()
        symptoms = data.get('symptoms', [])
        condition = data.get('condition', '').lower()
        
        if not name or not age or not gender or not symptoms:
            return jsonify({
                'success': False,
                'error': 'All fields are required'
            }), 400
        
        patient = Patient(name, age, gender, symptoms)
        patients[patient.id] = patient
        
        doctor = assign_doctor_to_patient(patient)
        
        if Patient.should_admit(patient.symptoms, condition):
            patient.admit()
            status_message = f"{patient.name} admitted as inpatient."
        else:
            if doctor:
                patient.set_outpatient(f"Outpatient advice by {doctor.name}")
                status_message = f"{patient.name} set as outpatient."
            else:
                status_message = f"{patient.name} registered but no doctor available."
        
        save_patient_to_json(patient)
        
        return jsonify({
            'success': True,
            'message': f'Patient registered successfully. {status_message}',
            'data': {
                'patient': patient.to_dict(),
                'doctor': doctor.to_dict() if doctor else None
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/treatment', methods=['POST'])
def simulate_treatment():
    try:
        data = request.get_json()
        patient_id = data.get('patient_id', '').strip()
        note = data.get('note', '').strip()
        treatment = data.get('treatment', '').strip()

        cost = float(data.get('cost', 0))
        discharge = data.get('discharge', False)

        
        if patient_id not in patients:
            return jsonify({
                'success': False,
                'error': 'Patient not found'
            }), 404
        
        patient = patients[patient_id]
        
        if patient.status != 'inpatient':
            return jsonify({
                'success': False,
                'error': 'Patient is not admitted for treatment'
            }), 400
        
        # Find the assigned doctor
        doctor = None
        for d in doctors.values():
            if d.name == patient.assigned_doctor:
                doctor = d
                break
        
        if not doctor:
            return jsonify({
                'success': False,
                'error': 'Assigned doctor not found'
            }), 404
        
        # Add treatment note and cost
        treatment_note = f"{note}, Treatment: {treatment}"
        if additional_charges > 0:
            treatment_note += f", Charges: ₹{additional_charges}"
        
        doctor.log_condition(patient.id, treatment_note)

        # Always update bill_amount and treatment_total_cost
        if not hasattr(patient, 'treatment_total_cost'):
            patient.treatment_total_cost = 0
        patient.bill_amount = patient.treatment_total_cost
        if discharge:
            total_cost = sum(entry.get('cost', 0) for entry in patient.history)
            doctor.discharge_patient(patient, total_cost)
            message = f"Patient {patient.name} discharged with bill ₹{total_cost}"

        else:
            # For regular treatment, add additional charges to existing bill
            patient.bill_amount += additional_charges
            message = f"Treatment recorded for {patient.name}. Updated bill: ₹{patient.bill_amount}"
        
        print(f"Updated patient bill: ₹{patient.bill_amount}")  # Debug log
        
        save_patient_to_json(patient)
        save_doctor_to_json(doctor)
        
        return jsonify({
            'success': True,
            'message': message,
            'data': patient.to_dict()
        })
    except Exception as e:
        print(f"Treatment error: {e}")  # Debug log
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    try:
        total_patients = len(patients)
        inpatients = len([p for p in patients.values() if p.status == 'inpatient'])
        outpatients = len([p for p in patients.values() if p.status == 'outpatient'])
        discharged = len([p for p in patients.values() if p.status == 'discharged'])
        total_revenue = sum([p.bill_amount for p in patients.values()])
        total_doctors = len(doctors)
        
        return jsonify({
            'success': True,
            'data': {
                'total_patients': total_patients,
                'inpatients': inpatients,
                'outpatients': outpatients,
                'discharged': discharged,
                'total_revenue': total_revenue,
                'total_doctors': total_doctors
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Create templates and static directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    print("Starting Patient Tracking System Web Server...")
    print("Access the application at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)