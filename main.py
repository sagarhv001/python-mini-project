import os
import json
from patient import Patient
from doctor import Doctor
from utilities import register_doctor, register_patient, simulate_treatment
from data_storage import patients, doctors
def load_patients():
    file_path = 'patients.json'
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                txt = f.read().strip()
                if not txt:
                    data = {}
                else:
                    data = json.loads(txt)
            except Exception:
                data = {}
            for pid, pinfo in data.items():
                patient = Patient(
                    pinfo['name'], pinfo['age'], pinfo['gender'], pinfo['symptoms']
                )
                patient.id = pid
                patient.assigned_doctor = pinfo.get('assigned_doctor')
                patient.status = pinfo.get('status')
                patient.history = pinfo.get('history', [])
                patient.admission = pinfo.get('admission')
                patient.discharge_date = pinfo.get('discharge_date')
                patient.bill_amount = pinfo.get('bill_amount', 0)
                patients[pid] = patient

def load_doctors():
    file_path = 'doctors.json'
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                txt = f.read().strip()
                if not txt:
                    data = {}
                else:
                    data = json.loads(txt)
            except Exception:
                data = {}
            for did, dinfo in data.items():
                doctor = Doctor(
                    dinfo['name'], dinfo['specialization']
                )
                doctor.id = did
                doctor.patients = dinfo.get('patients', [])
                doctor.notes = dinfo.get('notes', {})
                doctors[did] = doctor



def main():
    load_doctors()
    load_patients()
    print("=== Patient Tracking System ===")
    while True:
        print("\n1. Register Doctor")
        print("2. Register Patient")
        print("3. Simulate Treatment")
        print("4. Exit")
        choice = input("Enter choice: ")

        if choice == '1':
            register_doctor()
        elif choice == '2':
            register_patient()
        elif choice == '3':
            pid = input("Enter Patient ID: ")
            if pid in patients:
                patient = patients[pid]
                doctor = next((d for d in doctors.values() if d.name == patient.assigned_doctor), None)
                if doctor:
                    simulate_treatment(patient, doctor)
                else:
                    print("Assigned doctor not found.")
            else:
                print("Patient not found.")
        elif choice == '4':
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()