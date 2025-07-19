import os
import json

patients = {}
doctors = {}

def save_patient_to_json(patient):
    file_path = 'patients.json'
    data = {}
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                data = json.load(f)
            except:
                pass
    data[patient.id] = patient.to_dict()
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def save_doctor_to_json(doctor):
    file_path = 'doctors.json'
    data = {}
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                data = json.load(f)
            except:
                pass
    data[doctor.id] = doctor.to_dict()
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)
