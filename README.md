
# Hospital Patient Tracking System

This repository provides a simple, object-oriented hospital patient and doctor management system, with a command-line interface, RESTful web server, and a comprehensive test suite. All unit and integration test activities are logged to both the console and a log file.

---

## Features
- **Patient Management**: Register, admit, discharge, and track patient history using the `Patient` class.
- **Doctor Management**: Register doctors, assign patients, log conditions, and discharge patients using the `Doctor` class.
- **JSON Data Storage**: All patient and doctor data is serialized to `patients.json` and `doctors.json`.
- **Web Server**: Flask-based REST API and web frontend for patient/doctor management and statistics.
- **Comprehensive Testing**: Unit and integration tests for all major classes and data flows, with detailed logging.

---

## Project Structure

```
├── patient.py              # Patient class and logic
├── doctor.py               # Doctor class and logic
├── data_storage.py         # JSON save/load utilities
├── utilities.py            # Registration and assignment helpers
├── main.py                 # CLI for patient/doctor management
├── web_server.py           # Flask REST API and web frontend
├── unit_test.py            # Unit tests for all classes and storage
├── integration_test.py     # Integration tests for patient flows
├── test_log.txt            # Log file for unit tests
├── integration_test_log.txt# Log file for integration tests
├── patients.json           # Patient data (auto-generated)
├── doctors.json            # Doctor data (auto-generated)
├── README.md
```

---

## Usage

### 1. Command-Line Patient/Doctor Management
```bash
python main.py
```
Follow the prompts to register doctors, register patients, and simulate treatments.

### 2. Web Server (REST API & Frontend)
```bash
python web_server.py
```
Visit [http://localhost:5000](http://localhost:5000) in your browser.

### 3. Run Unit Tests
```bash
python unit_test.py
```
All test case results are printed to the console and logged in `test_log.txt`.

### 4. Run Integration Tests
```bash
python integration_test.py
```
Integration test results are logged in `integration_test_log.txt`.

---

## Example Test Log Output

```
2025-07-18 18:45:30,123 [INFO] ============================
2025-07-18 18:45:30,123 [INFO] Starting Test Module: TestPatient
2025-07-18 18:45:30,124 [INFO] ============================
2025-07-18 18:45:30,124 [INFO] Setting up test case: test_patient_creation
2025-07-18 18:45:30,124 [INFO] ---- Running test: test_patient_creation ----
[PASSED] TestPatient.test_patient_creation
...
```

---

## Prerequisites
- Python 3.10+
- For web server: `pip install flask flask-cors`

---

## Extending the Project
- Add more OOP models (appointments, billing, etc.)
- Add authentication, validation, or a richer web UI for production use.

---

**This is a demonstration project. For real-world use, add authentication, robust validation, and production-ready deployment.**

