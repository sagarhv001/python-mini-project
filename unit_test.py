import unittest
import os
import json
import logging
from patient import Patient, save_patient_to_json, load_patients_from_json, patients

# Configure logging to both log.txt and console
LOG_FILE = "test_log.txt"
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Remove any old handlers
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# File Handler
file_handler = logging.FileHandler(LOG_FILE, mode='w')
file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

# Console Handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

class TestPatient(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logging.info("="*50)
        logging.info("Starting Test Module: %s", cls.__name__)
        logging.info("="*50)

    @classmethod
    def tearDownClass(cls):
        logging.info("="*50)
        logging.info("Finishing Test Module: %s", cls.__name__)
        logging.info("="*50)

    def setUp(self):
        patients.clear()
        self.test_file = 'test_patients.json'
        self._orig_save_patient_to_json = save_patient_to_json

        def _save_patient_to_json(patient):
            if os.path.exists(self.test_file):
                with open(self.test_file, 'r') as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        data = {}
            else:
                data = {}
            data[patient.id] = patient.to_dict()
            with open(self.test_file, 'w') as f:
                json.dump(data, f, indent=4)
        globals()['save_patient_to_json'] = _save_patient_to_json

        logging.info("Setting up test case: %s", self._testMethodName)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        globals()['save_patient_to_json'] = self._orig_save_patient_to_json
        logging.info("Tearing down test case: %s", self._testMethodName)

    def run(self, result=None):
        test_name = self._testMethodName
        logging.info("---- Running test: %s ----", test_name)
        try:
            super().run(result)
            if result and hasattr(result, 'failures') and any(test_name in str(item[0]) for item in result.failures):
                logging.error("Test FAILED: %s", test_name)
            elif result and hasattr(result, 'errors') and any(test_name in str(item[0]) for item in result.errors):
                logging.error("Test ERROR: %s", test_name)
            else:
                logging.info("Test PASSED: %s", test_name)
        except Exception as e:
            logging.exception("Test ERRORED: %s (%s)", test_name, e)
        logging.info("----------------------------")

    def test_patient_creation(self):
        p = Patient("Alice", 28, "Female", ["cough", "fever"])
        self.assertTrue(p.id.startswith("HOS-"))
        self.assertEqual(p.name, "Alice")
        self.assertEqual(p.age, 28)
        self.assertEqual(p.gender, "Female")
        self.assertEqual(p.status, 'registered')
        self.assertIn("cough", p.symptoms)
        self.assertEqual(p.history, [])

    def test_add_history(self):
        p = Patient("Bob", 30, "Male", ["cold"])
        p.add_history("Checked for flu")
        self.assertEqual(len(p.history), 1)
        self.assertIn("Checked for flu", p.history[0]['notes'])

    def test_admit_discharge(self):
        p = Patient("Dan", 27, "Male", ["injury"])
        p.admit()
        self.assertEqual(p.status, 'inpatient')
        self.assertIsNotNone(p.admission)
        p.discharge(1000)
        self.assertEqual(p.status, 'discharged')
        self.assertEqual(p.bill_amount, 1000)
        self.assertIsNotNone(p.discharge_date)

    def test_set_outpatient(self):
        p = Patient("Eva", 31, "Female", ["headache"])
        p.set_outpatient("Prescribed painkillers")
        self.assertEqual(p.status, 'outpatient')
        self.assertEqual(len(p.history), 1)
        self.assertIn("Prescribed painkillers", p.history[0]['notes'])

    def test_json_save_and_load(self):
        p = Patient("Frank", 42, "Male", ["allergy"])
        save_patient_to_json(p)
        with open(self.test_file, 'r') as f:
            data = json.load(f)
        self.assertIn(p.id, data)
        self.assertEqual(data[p.id]['name'], "Frank")
        loaded_patients = {}
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
            loaded_patients[pid] = patient
        self.assertIn(p.id, loaded_patients)
        self.assertEqual(loaded_patients[p.id].name, "Frank")
        self.assertEqual(loaded_patients[p.id].symptoms, ["allergy"])

if __name__ == '__main__':
    unittest.main()
