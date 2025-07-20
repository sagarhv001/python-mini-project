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

def simulate_treatment(patient, doctor):
    if patient.status != 'inpatient':
        print("Patient is not admitted. No treatment simulation needed.")
        return

    days = int(input("Enter number of treatment days: "))
    total_bill = 0

    for day in range(1, days + 1):
        print(f"\n--- Day {day} ---")
        note = input("Enter condition update: ")
        treatment = input("Treatment/Test conducted: ")
        cost = float(input("Enter cost for this treatment/test: ₹"))
        doctor.log_condition(patient.id, f"Day {day}: {note}, Treatment: {treatment}, Cost: ₹{cost}")
        patient.add_history(f"Day {day}: {note}, Treatment: {treatment}", cost=cost)

        if input("Discharge patient? (y/n): ").lower() == 'y':
            # Calculate total cost from history
            total_cost = sum(entry.get('cost', 0) for entry in patient.history)
            doctor.discharge_patient(patient, total_cost)
            print(f"Total bill amount: ₹{total_cost}")

            break
    else:
        # If the loop completes without early discharge
        doctor.discharge_patient(patient, total_bill)

    save_patient_to_json(patient)
    save_doctor_to_json(doctor)