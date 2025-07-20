import json
import os
import uuid
from datetime import datetime
class Patient:
    @staticmethod
    def should_admit(symptoms, condition):
        critical_symptoms = [
            'abdominal pain',
            'severe abdominal pain',
            'abdominal bleeding',
            'chest pain',
            'difficulty breathing',
            'unconscious',
            'severe bleeding',
            'heart attack',
            'stroke',
            'severe allergic reaction',
            'severe burns',
        ]
        if condition.lower() == 'critical':
            return True
        for symptom in symptoms:
            s_clean = symptom.strip().lower()
            for crit in critical_symptoms:
                crit_clean = crit.lower()
                if crit_clean in s_clean or s_clean in crit_clean:
                    return True
        return False
    def __init__(self, name, age, gender, symptoms):
        self.id = "PAT-" + str(uuid.uuid4())[:5]
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
    def add_history(self, notes, cost=0):
        self.history.append({
            'date': datetime.now().strftime("%Y-%m-%d"),
            'notes': notes,
            'cost': cost
        })
        # Add cost to running total
        if not hasattr(self, 'treatment_total_cost'):
            self.treatment_total_cost = 0
        self.treatment_total_cost += cost
        self.bill_amount = self.treatment_total_cost
    def admit(self):
        self.admission = datetime.now().strftime("%Y-%m-%d")
        self.status = 'inpatient'
    def discharge(self, bill=None):
        self.discharge_date = datetime.now().strftime("%Y-%m-%d")
        if self.status == 'inpatient' or self.admission:
            self.bill_amount = sum(entry.get('cost', 0) for entry in self.history)
        elif bill is not None:
            self.bill_amount = bill
        self.status = 'discharged'
        # For inpatients, bill is sum of all treatment costs
        
        # For outpatients, bill_amount should already be set by set_outpatient
        
    def set_outpatient(self, notes):
        self.status = 'outpatient'
        self.bill_amount = 500  # Set a constant consultation fee for outpatients
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
            "bill_amount": self.bill_amount,
            "treatment_total_cost": getattr(self, 'treatment_total_cost', 0)
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

    patient = Patient(name, age, gender, symptoms)
    if Patient.should_admit(patient.symptoms, condition):
        patient.admit()
    patients[patient.id] = patient
    print(f"Patient registered with ID: {patient.id}")
    save_patient_to_json(patient)
    return patient.id
# register_patient()