import os
import json

patients = {}
doctors = {}

def save_to_json(file_path, obj):
    backup_path = file_path.replace('.json', '_backup.json')
    
    # Backup current file
    if os.path.exists(file_path):
        try:
            os.replace(file_path, backup_path)
            print(f"Backup created: {backup_path}")
        except Exception as e:
            print(f"Failed to backup: {e}")
    
    # Load backup data if it exists
    data = {}
    if os.path.exists(backup_path):
        with open(backup_path, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Failed to load backup JSON: {e}")

    data[obj.id] = obj.to_dict()
    
    # Save new data
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Saved to {file_path}")

def save_patient_to_json(patient):
    save_to_json('patients.json', patient)

def save_doctor_to_json(doctor):
    save_to_json('doctors.json', doctor)
