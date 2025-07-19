# --- Standard Library Imports ---
import unittest
import os
import json
import logging
# --- Project Imports ---
from patient import Patient, save_patient_to_json
from doctor import Doctor
from data_storage import save_doctor_to_json, doctors, patients
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


# --------------------- TestPatient ---------------------
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
        print(f"\n[RUNNING] {self.__class__.__name__}.{test_name}")
        logging.info("---- Running test: %s ----", test_name)
        try:
            super().run(result)
            if result and hasattr(result, 'failures') and any(test_name in str(item[0]) for item in result.failures):
                print(f"[FAILED] {self.__class__.__name__}.{test_name}")
                logging.error("Test FAILED: %s", test_name)
            elif result and hasattr(result, 'errors') and any(test_name in str(item[0]) for item in result.errors):
                print(f"[ERROR] {self.__class__.__name__}.{test_name}")
                logging.error("Test ERROR: %s", test_name)
            else:
                print(f"[PASSED] {self.__class__.__name__}.{test_name}")
                logging.info("Test PASSED: %s", test_name)
        except Exception as e:
            print(f"[EXCEPTION] {self.__class__.__name__}.{test_name} ({e})")
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


    
# --------------------- TestDoctor ---------------------
class TestDoctor(unittest.TestCase):
    def run(self, result=None):
        test_name = self._testMethodName
        print(f"\n[RUNNING] {self.__class__.__name__}.{test_name}")
        logging.info("---- Running test: %s ----", test_name)
        try:
            super().run(result)
            if result and hasattr(result, 'failures') and any(test_name in str(item[0]) for item in result.failures):
                print(f"[FAILED] {self.__class__.__name__}.{test_name}")
                logging.error("Test FAILED: %s", test_name)
            elif result and hasattr(result, 'errors') and any(test_name in str(item[0]) for item in result.errors):
                print(f"[ERROR] {self.__class__.__name__}.{test_name}")
                logging.error("Test ERROR: %s", test_name)
            else:
                print(f"[PASSED] {self.__class__.__name__}.{test_name}")
                logging.info("Test PASSED: %s", test_name)
        except Exception as e:
            print(f"[EXCEPTION] {self.__class__.__name__}.{test_name} ({e})")
            logging.exception("Test ERRORED: %s (%s)", test_name, e)
        logging.info("----------------------------")
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
    
# --------------------- TestDataStorage ---------------------
class TestDataStorage(unittest.TestCase):
    def run(self, result=None):
        test_name = self._testMethodName
        print(f"\n[RUNNING] {self.__class__.__name__}.{test_name}")
        logging.info("---- Running test: %s ----", test_name)
        try:
            super().run(result)
            if result and hasattr(result, 'failures') and any(test_name in str(item[0]) for item in result.failures):
                print(f"[FAILED] {self.__class__.__name__}.{test_name}")
                logging.error("Test FAILED: %s", test_name)
            elif result and hasattr(result, 'errors') and any(test_name in str(item[0]) for item in result.errors):
                print(f"[ERROR] {self.__class__.__name__}.{test_name}")
                logging.error("Test ERROR: %s", test_name)
            else:
                print(f"[PASSED] {self.__class__.__name__}.{test_name}")
                logging.info("Test PASSED: %s", test_name)
        except Exception as e:
            print(f"[EXCEPTION] {self.__class__.__name__}.{test_name} ({e})")
            logging.exception("Test ERRORED: %s (%s)", test_name, e)
        logging.info("----------------------------")
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
