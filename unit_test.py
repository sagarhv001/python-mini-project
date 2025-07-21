import unittest
import os
import json
from patient import Patient
from doctor import Doctor
from data_storage import save_patient_to_json, save_doctor_to_json, patients, doctors

class TestPatient(unittest.TestCase):
    def setUp(self):
        self.patient = Patient("Alice", 30, "Female", ["cough", "fever"])
        patients.clear()
        if os.path.exists("test_patients.json"):
            os.remove("test_patients.json")

    def tearDown(self):
        if os.path.exists("test_patients.json"):
            os.remove("test_patients.json")
        patients.clear()

    def test_patient_creation(self):
        # Test that patient fields are set correctly
        self.assertEqual(self.patient.name, "Alice")
        self.assertEqual(self.patient.age, 30)
        self.assertEqual(self.patient.gender, "Female")
        self.assertIn("cough", self.patient.symptoms)

    def test_admit_and_discharge(self):
        self.patient.admit()
        self.assertEqual(self.patient.status, "inpatient")
        self.patient.discharge(1000)
        self.assertEqual(self.patient.status, "discharged")
        self.assertEqual(self.patient.bill_amount, 1000)

    def test_add_history_and_bill(self):
        self.patient.add_history("Initial checkup", cost=200)
        self.assertEqual(len(self.patient.history), 1)
        self.assertEqual(self.patient.bill_amount, 200)

    def test_set_outpatient(self):
        self.patient.set_outpatient("Consulted and sent home")
        self.assertEqual(self.patient.status, "outpatient")
        self.assertEqual(self.patient.bill_amount, 0)
        self.assertIn("Consulted", self.patient.history[0]['notes'])

    def test_save_and_load_patient(self):
        # Save patient and check file contents
        save_patient_to_json(self.patient)
        with open("patients.json", "r") as f:
            data = json.load(f)
        self.assertIn(self.patient.id, data)
        self.assertEqual(data[self.patient.id]['name'], "Alice")

class TestDoctor(unittest.TestCase):
    def setUp(self):
        self.doctor = Doctor("Dr. Bob", "Cardiology")
        self.patient = Patient("Charlie", 40, "Male", ["chest pain"])
        doctors.clear()
        if os.path.exists("test_doctors.json"):
            os.remove("test_doctors.json")

    def tearDown(self):
        if os.path.exists("test_doctors.json"):
            os.remove("test_doctors.json")
        doctors.clear()

    def test_doctor_creation(self):
        self.assertEqual(self.doctor.name, "Dr. Bob")
        self.assertEqual(self.doctor.specialization, "Cardiology")
        self.assertEqual(self.doctor.patients, [])

    def test_assign_patient(self):
        self.doctor.assign_patient(self.patient)
        self.assertIn(self.patient.id, self.doctor.patients)
        self.assertEqual(self.patient.assigned_doctor, self.doctor.name)

    def test_log_condition(self):
        self.doctor.log_condition(self.patient.id, "Stable", "ECG", 300)
        self.assertIn(self.patient.id, self.doctor.notes)
        self.assertEqual(self.doctor.notes[self.patient.id][0]['note'], "Stable")

    def test_discharge_patient(self):
        self.patient.admit()  # Ensure patient is inpatient so bill is set correctly
        self.doctor.assign_patient(self.patient)
        self.doctor.discharge_patient(self.patient, 1200)
        self.assertNotIn(self.patient.id, self.doctor.patients)
        self.assertEqual(self.patient.status, "discharged")
        self.assertEqual(self.patient.bill_amount, 1200)

    def test_save_and_load_doctor(self):
        save_doctor_to_json(self.doctor)
        with open("doctors.json", "r") as f:
            data = json.load(f)
        self.assertIn(self.doctor.id, data)
        self.assertEqual(data[self.doctor.id]['name'], "Dr. Bob")

class TestDataStorage(unittest.TestCase):
    def setUp(self):
        self.patient = Patient("Daisy", 22, "Female", ["headache"])
        self.doctor = Doctor("Dr. Eve", "Neurology")
        patients.clear()
        doctors.clear()

    def tearDown(self):
        if os.path.exists("patients.json"):
            os.remove("patients.json")
        if os.path.exists("doctors.json"):
            os.remove("doctors.json")
        patients.clear()
        doctors.clear()

    def test_save_patient_to_json(self):
        save_patient_to_json(self.patient)
        self.assertTrue(os.path.exists("patients.json"))
        with open("patients.json", "r") as f:
            data = json.load(f)
        self.assertIn(self.patient.id, data)

    def test_save_doctor_to_json(self):
        save_doctor_to_json(self.doctor)
        self.assertTrue(os.path.exists("doctors.json"))
        with open("doctors.json", "r") as f:
            data = json.load(f)
        self.assertIn(self.doctor.id, data)


if __name__ == "__main__":
    unittest.main()