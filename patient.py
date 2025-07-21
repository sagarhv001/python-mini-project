import json
import os
import uuid
from datetime import datetime

class Patient:
    @staticmethod
    def should_admit(symptoms, condition):
        critical_symptoms = {
    'abdominal pain': 'Gastroenterology',
    'severe abdominal pain': 'Gastroenterology',
    'abdominal bleeding': 'Gastroenterology',
    'chest pain': 'Cardiology',
    'difficulty breathing': 'Pulmonology',
    'unconscious': 'Neurology',
    'severe bleeding': 'Trauma Surgeon',
    'heart attack': 'Cardiology',
    'stroke': 'Neurology',
    'severe allergic reaction': 'Allergist',
    'severe burns': 'Burn Specialist'
}
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
            # If bill is provided, use it; else sum history
            if bill is not None:
                self.bill_amount = bill
            else:
                self.bill_amount = sum(entry.get('cost', 0) for entry in self.history)
        else:
            # Outpatient: always set to 500
            self.bill_amount = 500
        self.status = 'discharged'

    def set_outpatient(self, notes):
        self.status = 'outpatient'
        self.bill_amount = 500
        self.add_history(notes)
        print(f"Patient {self.name} discharged with bill ₹{self.bill_amount}")
    
    def update_bill(self, amount):
        """Add amount to existing bill"""
        self.bill_amount += float(amount)
        print(f"Updated bill for {self.name}: ₹{self.bill_amount}")
    

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
            "treatment_total_cost": getattr(self, 'treatment_total_cost', 0),
            "bill_amount": float(self.bill_amount)
        }

from data_storage import save_patient_to_json

def register_patient():
    name = input("Patient Name: ")
    age = input("Age: ")
    gender = input("Gender: ")
    symptoms = input("Symptoms (comma-separated): ").split(',')
    condition = input("Condition: ")

    patient = Patient(name, age, gender, symptoms)
    if Patient.should_admit(patient.symptoms, condition):
        patient.admit()
    from data_storage import patients  # ensure correct patients dict
    patients[patient.id] = patient
    print(f"Patient registered with ID: {patient.id}")
    save_patient_to_json(patient)
    return patient.id