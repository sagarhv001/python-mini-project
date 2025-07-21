import unittest
import os
import json
from patient import Patient
from doctor import Doctor
from data_storage import save_patient_to_json, save_doctor_to_json, patients, doctors
from utilities import assign_doctor_to_patient, mark_doctor_on_leave

class TestIntegration(unittest.TestCase):
    def setUp(self):
        patients.clear()
        doctors.clear()
        for fname in ["test_patients.json", "test_doctors.json"]:
            if os.path.exists(fname):
                os.remove(fname)
        # Patch save functions to use test files
        def _save_patient_to_json(patient):
            fname = "test_patients.json"
            if os.path.exists(fname):
                with open(fname, "r") as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        data = {}
            else:
                data = {}
            data[patient.id] = patient.to_dict()
            with open(fname, "w") as f:
                json.dump(data, f, indent=4)
        def _save_doctor_to_json(doctor):
            fname = "test_doctors.json"
            if os.path.exists(fname):
                with open(fname, "r") as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        data = {}
            else:
                data = {}
            data[doctor.id] = doctor.to_dict()
            with open(fname, "w") as f:
                json.dump(data, f, indent=4)
        globals()['save_patient_to_json'] = _save_patient_to_json
        globals()['save_doctor_to_json'] = _save_doctor_to_json

    def tearDown(self):
        for fname in ["test_patients.json", "test_doctors.json"]:
            if os.path.exists(fname):
                os.remove(fname)
        patients.clear()
        doctors.clear()

    def test_full_patient_lifecycle(self):
        # Register doctor and patient, assign, admit, treat, discharge
        doc = Doctor("Dr. Smith", "Cardiology")
        doctors[doc.id] = doc
        save_doctor_to_json(doc)

        pat = Patient("John Doe", 55, "Male", ["chest pain"])
        patients[pat.id] = pat
        save_patient_to_json(pat)

        # Assign doctor based on symptoms
        assigned = assign_doctor_to_patient(pat)
        # Patch save functions to use test files
        def _save_patient_to_json(patient):
            fname = "test_patients.json"
            if os.path.exists(fname):
                with open(fname, "r") as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        data = {}
            else:
                data = {}
            data[patient.id] = patient.to_dict()
            with open(fname, "w") as f:
                json.dump(data, f, indent=4)
        def _save_doctor_to_json(doctor):
            fname = "test_doctors.json"
            if os.path.exists(fname):
                with open(fname, "r") as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        data = {}
            else:
                data = {}
            data[doctor.id] = doctor.to_dict()
            with open(fname, "w") as f:
                json.dump(data, f, indent=4)
        globals()['save_patient_to_json'] = _save_patient_to_json
        globals()['save_doctor_to_json'] = _save_doctor_to_json

        save_doctor_to_json(doc)

        self.assertEqual(assigned.specialization, "Cardiology")
        self.assertEqual(pat.assigned_doctor, doc.name)
        save_patient_to_json(pat)
        # Admit and treat patient
        pat.admit()
        pat.add_history("ECG performed", cost=500)
        save_patient_to_json(pat)
        doc.log_condition(pat.id, "Stable", "ECG", 500)
        save_doctor_to_json(doc)

        # Discharge patient
        doc.discharge_patient(pat, 1200)
        save_patient_to_json(pat)
        save_doctor_to_json(doc)
        self.assertEqual(pat.status, "discharged")
        self.assertEqual(pat.bill_amount, 1200)
        self.assertNotIn(pat.id, doc.patients)

    def test_doctor_on_leave_and_reassignment(self):
        # Register two doctors and a patient
        doc1 = Doctor("Dr. A", "Neurology")
        doc2 = Doctor("Dr. B", "Neurology")
        doctors[doc1.id] = doc1
        doctors[doc2.id] = doc2
        save_doctor_to_json(doc1)
        save_doctor_to_json(doc2)

        pat = Patient("Jane Roe", 40, "Female", ["stroke"])
        patients[pat.id] = pat
        save_patient_to_json(pat)
        save_doctor_to_json(doc1)
        save_doctor_to_json(doc2)
        doc1.assign_patient(pat)
        pat.assigned_doctor = doc1.name
        save_patient_to_json(pat)
        save_doctor_to_json(doc1)

        # Mark doc1 on leave and reassign
        mark_doctor_on_leave(doc1)
        self.assertTrue(getattr(doc1, 'on_leave', False))
        self.assertNotIn(pat.id, doc1.patients)
        self.assertIn(pat.id, doc2.patients)
        self.assertEqual(pat.assigned_doctor, doc2.name)

    def test_json_persistence(self):
        # Register and save doctor/patient, reload from file
        doc = Doctor("Dr. Persist", "General")
        doctors[doc.id] = doc
        save_doctor_to_json(doc)

        pat = Patient("Persist Patient", 60, "Male", ["fever"])
        patients[pat.id] = pat
        save_patient_to_json(pat)

        # Clear in-memory dicts and reload from file
        patients.clear()
        doctors.clear()
        with open("test_patients.json", "r") as f:
            data = json.load(f)
        with open("test_doctors.json", "r") as f:
            doc_data = json.load(f)
        self.assertIn(pat.id, data)
        self.assertIn(doc.id, doc_data)

if __name__ == "__main__":
    unittest.main()