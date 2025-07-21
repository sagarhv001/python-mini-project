import sys
import os
import json
from patient import Patient, register_patient
from doctor import Doctor
from utilities import register_doctor, simulate_treatment
from data_storage import patients, doctors


def load_json_with_backup(primary_path, backup_path):
    """
    Try to load JSON data from primary file.
    If it fails, try to load from backup file.
    """
    data = {}
    abs_path = os.path.abspath(primary_path)
    
    if os.path.exists(primary_path):
        with open(primary_path, 'r') as f:
            try:
                txt = f.read().strip()
               
                if txt:
                    data = json.loads(txt)
                   
                else:
                   
                    return load_backup(backup_path)
            except Exception as e:
               
                return load_backup(backup_path)
        return data
    else:
        
        return load_backup(backup_path)

def load_backup(backup_path):
    if os.path.exists(backup_path):
        with open(backup_path, 'r') as f:
            try:
                txt = f.read().strip()
                if txt:
                    print(f"Loaded data from backup: {backup_path}")
                    return json.loads(txt)
            except json.JSONDecodeError as e:
                print(f"Failed to load backup {backup_path}: {e}")
    return {}

def load_patients():
    file_path = 'patients.json'
    backup_path = 'patients_backup.json'
    data = load_json_with_backup(file_path, backup_path)

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
    backup_path = 'doctors_backup.json'
    data = load_json_with_backup(file_path, backup_path)

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
        print("3. List All Doctors")
        print("4. List All Patients")
        print("5. Simulate Treatment for Inpatient")
        print("6. Show Patient History & Bill")
        print("7. Mark Doctor On Leave & Reassign Patients")
        print("8. Exit")
        choice = input("Enter choice: ")

        if choice == '1':
            register_doctor()
        elif choice == '2':
            # Register patient and assign doctor
            pid = register_patient()
            load_patients()  # Ensure in-memory patients dict is updated
            patient = patients[pid]
            from utilities import assign_doctor_to_patient
            doctor = assign_doctor_to_patient(patient)
            if doctor:
                from data_storage import save_patient_to_json
                save_patient_to_json(patient)  # Persist assigned_doctor
            else:
                print("No doctor assigned.")
        elif choice == '3':
            print("\n--- Doctors List ---")
            for d in doctors.values():
                print(f"{d.id}: {d.name} ({d.specialization}), Patients: {len(d.patients)}")
        elif choice == '4':
            print("\n--- Patients List ---")
            for p in patients.values():
                print(f"{p.id}: {p.name}, Status: {p.status}, Assigned Doctor: {p.assigned_doctor}, Bill: ₹{p.bill_amount}")
        elif choice == '5':
            if not patients:
                print("No patients available.")
                continue
            valid_patients = [p for p in patients.values() if p.status == 'inpatient' and p.assigned_doctor]
            if not valid_patients:
                print("No inpatients with assigned doctor available for treatment simulation.")
                continue
            print(f"\nSimulating treatment for {len(valid_patients)} inpatients:")
            for patient in valid_patients:
                print(f"\n--- {patient.name} (ID: {patient.id}) | Doctor: {patient.assigned_doctor} ---")
                doctor = next((d for d in doctors.values() if d.name == patient.assigned_doctor), None)
                if not doctor:
                    print(f"Assigned doctor {patient.assigned_doctor} not found. Skipping patient.")
                    continue
                note = input("Enter condition update: ")
                treatment = input("Treatment/Test conducted: ")
                try:
                    cost = float(input("Enter cost for this treatment/test: ₹"))
                except ValueError:
                    print("Invalid cost. Skipping patient.")
                    continue
                doctor.log_condition(patient.id, note, treatment, cost)
                patient.add_history(f"{note}, Treatment: {treatment}", cost=cost)
                from data_storage import save_patient_to_json, save_doctor_to_json
                save_patient_to_json(patient)
                save_doctor_to_json(doctor)
                print(f"Treatment recorded. Current bill: ₹{patient.bill_amount}")
                discharge = input("Discharge patient? (y/n): ").lower()
                if discharge == 'y':
                    total_cost = sum(entry.get('cost', 0) for entry in patient.history)
                    doctor.discharge_patient(patient, total_cost)
                    save_patient_to_json(patient)
                    save_doctor_to_json(doctor)
                    print(f"Patient discharged. Final bill: ₹{patient.bill_amount}")
            print("\nAll inpatients have had their treatments updated.")
        elif choice == '6':
            pid = input("Enter Patient ID: ")
            if pid in patients:
                patient = patients[pid]
                print(f"\n--- History for {patient.name} (ID: {patient.id}) ---")
                for entry in patient.history:
                    print(f"{entry['date']}: {entry['notes']} (Cost: ₹{entry.get('cost', 0)})")
                print(f"Current Bill: ₹{patient.bill_amount}")
                print(f"Status: {patient.status}")
            else:
                print("Patient not found.")
        elif choice == '7':
            # Mark doctor on leave and reassign patients
            print("\n--- Doctors List ---")
            for d in doctors.values():
                print(f"{d.id}: {d.name} ({d.specialization}), Patients: {len(d.patients)}")
            did = input("Enter Doctor ID to mark as on leave: ").strip()
            doctor = doctors.get(did)
            if not doctor:
                print("Doctor not found.")
                return
            from utilities import mark_doctor_on_leave
            mark_doctor_on_leave(doctor)
        elif choice == '8':
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        print("[FATAL ERROR] Exception in main():", e)
        traceback.print_exc()