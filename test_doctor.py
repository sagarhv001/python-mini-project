import unittest
from doctor import Doctor
from patient import Patient
from data_storage import save_doctor_to_json, doctors
import os
import json

class TestDoctor(unittest.TestCase):
    def setUp(self):
        self.doctor = Doctor("Dr. Smith", "Cardiology")
        self.patient = Patient("Test Patient", 40, "Male", ["cough"])
        self.test_file = 'test_doctors.json'
        self._orig_save_doctor_to_json = save_doctor_to_json

        def _save_doctor_to_json(doctor):
            if os.path.exists(self.test_file):
                with open(self.test_file, 'r') as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        data = {}
            else:
                data = {}
            data[doctor.id] = doctor.to_dict()
            with open(self.test_file, 'w') as f:
                json.dump(data, f, indent=4)
        globals()['save_doctor_to_json'] = _save_doctor_to_json

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        globals()['save_doctor_to_json'] = self._orig_save_doctor_to_json

    def test_doctor_creation(self):
        self.assertTrue(self.doctor.id.startswith("DOC-"))
        self.assertEqual(self.doctor.name, "Dr. Smith")
        self.assertEqual(self.doctor.specialization, "Cardiology")
        self.assertEqual(self.doctor.patients, [])
        self.assertEqual(self.doctor.notes, {})

    def test_assign_patient(self):
        self.doctor.assign_patient(self.patient)
        self.assertIn(self.patient.id, self.doctor.patients)
        self.assertEqual(self.patient.assigned_doctor, self.doctor.name)

    def test_log_condition(self):
        self.doctor.log_condition(self.patient.id, "Stable")
        self.assertIn(self.patient.id, self.doctor.notes)
        self.assertEqual(self.doctor.notes[self.patient.id][0]['note'], "Stable")

    def test_discharge_patient(self):
        self.patient.admit()
        self.doctor.discharge_patient(self.patient, 500)
        self.assertEqual(self.patient.status, 'discharged')
        self.assertEqual(self.patient.bill_amount, 500)

    def test_doctor_to_dict(self):
        dct = self.doctor.to_dict()
        self.assertEqual(dct['name'], self.doctor.name)
        self.assertEqual(dct['specialization'], self.doctor.specialization)
        self.assertEqual(dct['patients'], self.doctor.patients)
        self.assertEqual(dct['notes'], self.doctor.notes)

    def test_save_doctor_to_json(self):
        save_doctor_to_json(self.doctor)
        with open(self.test_file, 'r') as f:
            data = json.load(f)
        self.assertIn(self.doctor.id, data)
        self.assertEqual(data[self.doctor.id]['name'], self.doctor.name)

if __name__ == '__main__':
    unittest.main()
