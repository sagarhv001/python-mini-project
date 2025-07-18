import json
import os
import uuid
from datetime import datetime
class Patient:
    def __init__(self, name, age, gender, symptoms):
        self.id = "HOS-" + str(uuid.uuid4())
        self.name = name
        self.age = age
        self.gender = gender
        self.symptoms = [s.strip() for s in symptoms]
        self.assigned_doctor = None
        self.status = 'registered'
        self.history = []
        self.admission = None
        self.discharge_date = None
        self.bill_amount = 0

    def add_history(self, notes):
        self.history.append({
            'date': datetime.now().strftime("%Y-%m-%d"),
            'notes': notes
        })

    def admit(self):
        self.admission = datetime.now().strftime("%Y-%m-%d")
        self.status = 'inpatient'

    def discharge(self, bill):
        self.discharge_date = datetime.now().strftime("%Y-%m-%d")
        self.status = 'discharged'
        self.bill_amount = bill

    def set_outpatient(self, notes):
        self.status = 'outpatient'
        self.add_history(notes)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "symptoms": self.symptoms,
            "assigned_doctor": self.assigned_doctor,
            "status": self.status,
            "history": self.history,
            "admission": self.admission,
            "discharge_date": self.discharge_date,
            "bill_amount": self.bill_amount
        }

patients = {}
def save_patient_to_json(patient):
    file_path = 'patients.json'
    # Load existing data if file exists
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}

    # Add or update the patient record
    data[patient.id] = patient.to_dict()

    # Save back to file
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def load_patients_from_json():
    file_path = 'patients.json'
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
            for pid, pinfo in data.items():
                patient = Patient(
                    pinfo['name'], pinfo['age'], pinfo['gender'], pinfo['symptoms']
                )
                patient.id = pid  # avoid generating a new ID
                patient.assigned_doctor = pinfo.get('assigned_doctor')
                patient.status = pinfo.get('status')
                patient.history = pinfo.get('history', [])
                patient.admission = pinfo.get('admission')
                patient.discharge_date = pinfo.get('discharge_date')
                patient.bill_amount = pinfo.get('bill_amount', 0)
                patients[pid] = patient



def register_patient():
    name = input("Patient Name: ")
    age = input("Age: ")
    gender = input("Gender: ")
    symptoms = input("Symptoms (comma-separated): ").split(',')
    condition = input("Condition: ")
    if condition.lower() == Critical:
        admission = True
    patient = Patient(name, age, gender, symptoms)
    patients[patient.id] = patient

    print(f"Patient registered with ID: {patient.id}")

    save_patient_to_json(patient)

    return patient.id
# register_patient()