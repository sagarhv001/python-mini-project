
import json
import os
import uuid
from datetime import datetime


# --------------------- DOCTOR CLASS ---------------------
class Doctor:
    def __init__(self, name, specialization):
        self.id = "DOC-" + str(uuid.uuid4())[:5]
        self.name = name
        self.specialization = specialization
        self.patients = []
        self.notes = {}

    def assign_patient(self, patient):
        if patient.id not in self.patients:
            self.patients.append(patient.id)
            patient.assigned_doctor = self.name
            print(f"Patient {patient.name} assigned to Dr. {self.name}")

    def log_condition(self, patient_id, note):
        today = datetime.now().strftime("%Y-%m-%d")
        if patient_id not in self.notes:
            self.notes[patient_id] = []
        self.notes[patient_id].append({'date': today, 'note': note})

    def discharge_patient(self, patient, bill):
        patient.discharge(bill)
        print(f"Dr. {self.name} discharged {patient.name} with bill ₹{bill}")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "specialization": self.specialization,
            "patients": self.patients,
            "notes": self.notes
        }
