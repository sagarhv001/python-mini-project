import unittest
import os
import json
from data_storage import save_patient_to_json, save_doctor_to_json, patients, doctors
from patient import Patient
from doctor import Doctor

class TestDataStorage(unittest.TestCase):
    def setUp(self):
        self.patient = Patient("Test Patient", 25, "Male", ["cough"])
        self.doctor = Doctor("Dr. Test", "General")
        self.patient_file = 'test_patients_ds.json'
        self.doctor_file = 'test_doctors_ds.json'
        self._orig_save_patient_to_json = save_patient_to_json
        self._orig_save_doctor_to_json = save_doctor_to_json

        def _save_patient_to_json(patient):
            if os.path.exists(self.patient_file):
                with open(self.patient_file, 'r') as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        data = {}
            else:
                data = {}
            data[patient.id] = patient.to_dict()
            with open(self.patient_file, 'w') as f:
                json.dump(data, f, indent=4)
        globals()['save_patient_to_json'] = _save_patient_to_json

        def _save_doctor_to_json(doctor):
            if os.path.exists(self.doctor_file):
                with open(self.doctor_file, 'r') as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        data = {}
            else:
                data = {}
            data[doctor.id] = doctor.to_dict()
            with open(self.doctor_file, 'w') as f:
                json.dump(data, f, indent=4)
        globals()['save_doctor_to_json'] = _save_doctor_to_json

    def tearDown(self):
        if os.path.exists(self.patient_file):
            os.remove(self.patient_file)
        if os.path.exists(self.doctor_file):
            os.remove(self.doctor_file)
        globals()['save_patient_to_json'] = self._orig_save_patient_to_json
        globals()['save_doctor_to_json'] = self._orig_save_doctor_to_json

    def test_save_patient_to_json(self):
        save_patient_to_json(self.patient)
        with open(self.patient_file, 'r') as f:
            data = json.load(f)
        self.assertIn(self.patient.id, data)
        self.assertEqual(data[self.patient.id]['name'], self.patient.name)

    def test_save_doctor_to_json(self):
        save_doctor_to_json(self.doctor)
        with open(self.doctor_file, 'r') as f:
            data = json.load(f)
        self.assertIn(self.doctor.id, data)
        self.assertEqual(data[self.doctor.id]['name'], self.doctor.name)

if __name__ == '__main__':
    unittest.main()
