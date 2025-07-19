# --------------------- UTILITIES ---------------------
from doctor import Doctor
from patient import Patient
from data_storage import save_doctor_to_json, save_patient_to_json, doctors, patients

def register_doctor():
    name = input("Enter Doctor Name: ")
    specialization = input("Enter Specialization: ")
    doctor = Doctor(name, specialization)
    doctors[doctor.id] = doctor
    save_doctor_to_json(doctor)
    print(f"Doctor registered with ID: {doctor.id}")
    return doctor

def assign_doctor_to_patient(patient):
    if not doctors:
        print("No doctors available. Register a doctor first.")
        return None
    doctor = min(doctors.values(), key=lambda d: len(d.patients))
    doctor.assign_patient(patient)
    save_doctor_to_json(doctor)
    return doctor

def register_patient():
    name = input("Patient Name: ")
    age = input("Age: ")
    gender = input("Gender: ")
    symptoms = input("Symptoms (comma-separated): ").split(',')
    condition = input("Initial Condition: ").lower()

    patient = Patient(name, age, gender, symptoms)
    patients[patient.id] = patient
    doctor = assign_doctor_to_patient(patient)

    if condition == "critical":
        patient.admit()
        print(f"{patient.name} admitted as inpatient.")
    else:
        patient.set_outpatient(f"Outpatient advice by {doctor.name}")

    save_patient_to_json(patient)
    print(f"Patient registered with ID: {patient.id}")
    return patient, doctor

def simulate_treatment(patient, doctor):
    if patient.status != 'inpatient':
        print("Patient is not admitted. No treatment simulation needed.")
        return

    days = int(input("Enter number of treatment days: "))
    for day in range(1, days + 1):
        print(f"\n--- Day {day} ---")
        note = input("Enter condition update: ")
        treatment = input("Treatment/Test conducted: ")
        doctor.log_condition(patient.id, f"Day {day}: {note}, Treatment: {treatment}")
        patient.add_history(f"Day {day}: {note}, Treatment: {treatment}")

        if input("Discharge patient? (y/n): ").lower() == 'y':
            bill = int(input("Enter total bill amount: ₹"))
            doctor.discharge_patient(patient, bill)
            break

    save_patient_to_json(patient)
    save_doctor_to_json(doctor)
