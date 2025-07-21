# --- Doctor Leave and Reassignment ---
def mark_doctor_on_leave(doctor):
    doctor.on_leave = True
    print(f"Doctor {doctor.name} is now marked as on leave.")
    # Reassign all patients
    reassigned = 0
    for pid in list(doctor.patients):
        # Find the patient object
        patient = patients.get(pid)
        if not patient:
            continue
        # Find eligible doctors with same specialization and not on leave
        eligible_doctors = [d for d in doctors.values() if d.specialization == doctor.specialization and getattr(d, 'on_leave', False) == False and d.id != doctor.id]
        if not eligible_doctors:
            # Fallback: any doctor not on leave
            eligible_doctors = [d for d in doctors.values() if getattr(d, 'on_leave', False) == False and d.id != doctor.id]
        if not eligible_doctors:
            print(f"No available doctor to reassign patient {patient.name}.")
            continue
        new_doctor = min(eligible_doctors, key=lambda d: len(d.patients))
        new_doctor.assign_patient(patient)
        patient.assigned_doctor = new_doctor.name
        doctor.patients.remove(pid)
        save_doctor_to_json(new_doctor)
        save_patient_to_json(patient)
        reassigned += 1
    save_doctor_to_json(doctor)
    print(f"Total patients reassigned: {reassigned}")
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

    # Symptom to specialization mapping
    symptom_specialization_map = {
        'chest pain': 'Cardiology',
        'heart attack': 'Cardiology',
        'stroke': 'Neurology',
        'unconscious': 'Neurology',
        'abdominal pain': 'General Medicine',
        'severe abdominal pain': 'General Surgery',
        'abdominal bleeding': 'General Surgery',
        'difficulty breathing': 'Pulmonology',
        'severe bleeding': 'Emergency Response',
        'severe allergic reaction': 'General Medicine',
        'severe burns': 'Emergency Response',
    }

    # Find the most relevant specialization for the patient's symptoms
    matched_specializations = []
    for symptom in patient.symptoms:
        s_clean = symptom.strip().lower()
        for key, spec in symptom_specialization_map.items():
            if key in s_clean or s_clean in key:
                matched_specializations.append(spec)

    # Prefer the first matched specialization
    specialization = matched_specializations[0] if matched_specializations else None

    # Find doctors with the matched specialization
    if specialization:
        eligible_doctors = [d for d in doctors.values() if d.specialization.lower() == specialization.lower()]
        if eligible_doctors:
            # Assign to the doctor with the fewest patients in that specialization
            doctor = min(eligible_doctors, key=lambda d: len(d.patients))
            doctor.assign_patient(patient)
            save_doctor_to_json(doctor)
            return doctor

    # Fallback: assign to any doctor with the fewest patients
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