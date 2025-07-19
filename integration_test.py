import unittest
import os
import json
import logging
from patient import Patient, save_patient_to_json, load_patients_from_json, patients

# Configure logging to both file and terminal
INTEGRATION_LOG_FILE = "integration_test_log.txt"
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Remove any old handlers
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# File Handler
file_handler = logging.FileHandler(INTEGRATION_LOG_FILE, mode='w')
file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

# Console Handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))

# Add handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)

class TestPatientIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logging.info("=" * 50)
        logging.info("Starting Test Module: %s", cls.__name__)
        logging.info("=" * 50)
        cls.test_file = "integration_test_patients.json"

    @classmethod
    def tearDownClass(cls):
        logging.info("=" * 50)
        logging.info("Finishing Test Module: %s", cls.__name__)
        logging.info("=" * 50)

    def setUp(self):
        patients.clear()
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
        patients.clear()
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

    def test_register_and_admit_patient(self):
        p = Patient("Grace", 36, "Female", ["dizziness"])
        save_patient_to_json(p)
        p.admit()
        p.add_history("Initial tests performed")
        save_patient_to_json(p)
        with open(self.test_file, 'r') as f:
            data = json.load(f)
        self.assertEqual(data[p.id]['status'], 'inpatient')
        self.assertEqual(len(data[p.id]['history']), 1)
        self.assertIn("Initial tests performed", data[p.id]['history'][0]['notes'])

    def test_full_patient_lifecycle(self):
        p = Patient("Henry", 50, "Male", ["fracture"])
        save_patient_to_json(p)
        p.admit()
        p.add_history("X-ray done")
        p.discharge(2500)
        save_patient_to_json(p)
        with open(self.test_file, 'r') as f:
            data = json.load(f)
        self.assertEqual(data[p.id]['status'], 'discharged')
        self.assertEqual(data[p.id]['bill_amount'], 2500)
        self.assertIsNotNone(data[p.id]['discharge_date'])
        self.assertEqual(len(data[p.id]['history']), 1)
        self.assertIn("X-ray done", data[p.id]['history'][0]['notes'])

    def test_outpatient_then_admit(self):
        p = Patient("Ivy", 29, "Female", ["migraine"])
        p.set_outpatient("Prescribed medication")
        save_patient_to_json(p)
        p.admit()
        p.add_history("Admitted for observation")
        save_patient_to_json(p)
        with open(self.test_file, 'r') as f:
            data = json.load(f)
        self.assertEqual(data[p.id]['status'], 'inpatient')
        self.assertEqual(len(data[p.id]['history']), 2)
        self.assertIn("Prescribed medication", data[p.id]['history'][0]['notes'])
        self.assertIn("Admitted for observation", data[p.id]['history'][1]['notes'])

    def test_multiple_patients_json(self):
        p1 = Patient("Jack", 40, "Male", ["cough"])
        p2 = Patient("Kate", 34, "Female", ["fever"])
        save_patient_to_json(p1)
        save_patient_to_json(p2)
        with open(self.test_file, 'r') as f:
            data = json.load(f)
        self.assertIn(p1.id, data)
        self.assertIn(p2.id, data)
        self.assertEqual(data[p1.id]['name'], "Jack")
        self.assertEqual(data[p2.id]['name'], "Kate")

    def test_load_patients_from_json(self):
        p = Patient("Liam", 55, "Male", ["hypertension"])
        save_patient_to_json(p)
        with open(self.test_file, 'r') as f:
            data = json.load(f)
        loaded = {}
        for pid, pinfo in data.items():
            patient = Patient(
                pinfo['name'], pinfo['age'], pinfo['gender'], pinfo['symptoms']
            )
            patient.id = pid
            patient.status = pinfo.get('status')
            loaded[pid] = patient
        self.assertIn(p.id, loaded)
        self.assertEqual(loaded[p.id].name, "Liam")
        self.assertEqual(loaded[p.id].symptoms, ["hypertension"])

if __name__ == '__main__':
    unittest.main()
