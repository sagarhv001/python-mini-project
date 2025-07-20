// Global variables
let symptoms = [];
let currentPatient = null;

// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing app...');
    // Initialize the application
    init();
    setupEventListeners();
});

// Initialize application
function init() {
    console.log('Initializing application...');
    showSection('dashboard');
    loadDashboard();
}

// Setup event listeners
function setupEventListeners() {
    console.log('Setting up event listeners...');
    
    // Doctor registration form
    const doctorForm = document.getElementById('doctor-form');
    if (doctorForm) {
        doctorForm.addEventListener('submit', handleDoctorRegistration);
        console.log('Doctor form listener added');
    } else {
        console.warn('Doctor form not found');
    }
    
    // Patient registration form
    const patientForm = document.getElementById('patient-form');
    if (patientForm) {
        patientForm.addEventListener('submit', handlePatientRegistration);
        console.log('Patient form listener added');
    } else {
        console.warn('Patient form not found');
    }
    
    // Treatment form
    const treatmentForm = document.getElementById('treatment-form');
    if (treatmentForm) {
        treatmentForm.addEventListener('submit', handleTreatment);
        console.log('Treatment form listener added');
    } else {
        console.warn('Treatment form not found');
    }
    
    // Symptom input
    const symptomInput = document.getElementById('symptom-input');
    if (symptomInput) {
        symptomInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                addSymptom();
            }
        });
        console.log('Symptom input listener added');
    } else {
        console.warn('Symptom input not found');
    }
    
    // Discharge checkbox
    const dischargeCheckbox = document.getElementById('discharge-patient');
    if (dischargeCheckbox) {
        dischargeCheckbox.addEventListener('change', toggleDischargeSection);
        console.log('Discharge checkbox listener added');
    } else {
        console.warn('Discharge checkbox not found');
    }
}

// Navigation functions
function showSection(sectionId) {
    console.log(`Switching to section: ${sectionId}`);
    
    // Hide all sections
    const sections = document.querySelectorAll('.content-section');
    console.log(`Found ${sections.length} sections`);
    
    sections.forEach(section => {
        section.classList.remove('active');
    });
    
    // Show selected section
    const section = document.getElementById(sectionId);
    if (section) {
        section.classList.add('active');
        console.log(`Section ${sectionId} activated`);
    } else {
        console.error(`Section ${sectionId} not found!`);
        return;
    }
    
    // Update navigation
    const navLinks = document.querySelectorAll('.nav-link');
    console.log(`Found ${navLinks.length} nav links`);
    
    navLinks.forEach(link => {
        link.classList.remove('active');
    });
    
    const activeLink = document.querySelector(`[onclick="showSection('${sectionId}')"]`);
    if (activeLink) {
        activeLink.classList.add('active');
        console.log(`Nav link for ${sectionId} activated`);
    } else {
        console.warn(`Nav link for ${sectionId} not found`);
    }
    
    // Load section-specific data
    switch(sectionId) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'patients':
            loadPatients();
            break;
        case 'doctors':
            loadDoctors();
            break;
        default:
            console.log(`No specific loader for section: ${sectionId}`);
    }
}

// API functions
async function apiRequest(url, method = 'GET', data = null) {
    console.log(`Making ${method} request to ${url}`);
    
    // Check if server is running
    if (url.startsWith('/api/')) {
        console.log('API request detected, checking server connection...');
    }
    
    showLoading();
    
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
        };
        
        if (data) {
            options.body = JSON.stringify(data);
            console.log('Request data:', data);
        }
        
        const response = await fetch(url, options);
        console.log(`Response status: ${response.status}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('API response:', result);
        
        if (!result.success) {
            throw new Error(result.error || 'An error occurred');
        }
        
        return result;
    } catch (error) {
        console.error('API request failed:', error);
        
        // Check if it's a network error
        if (error.message.includes('fetch')) {
            showNotification('Connection Error', 'Cannot connect to server. Please ensure the Flask server is running on http://localhost:5000', 'error');
        } else {
            showNotification('Error', error.message, 'error');
        }
        throw error;
    } finally {
        hideLoading();
    }
}

// Loading functions
function showLoading() {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.style.display = 'flex';
    } else {
        console.warn('Loading element not found');
    }
}

function hideLoading() {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.style.display = 'none';
    }
}

// Notification functions
function showNotification(title, message, type = 'info') {
    console.log(`Notification: ${type} - ${title}: ${message}`);
    
    const container = document.getElementById('notification-container');
    if (!container) {
        console.error('Notification container not found');
        alert(`${title}: ${message}`); // Fallback
        return;
    }
    
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    notification.innerHTML = `
        <div class="notification-header">
            <span class="notification-title">${title}</span>
            <button class="notification-close" onclick="removeNotification(this)">&times;</button>
        </div>
        <div class="notification-message">${message}</div>
    `;
    
    container.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        const closeBtn = notification.querySelector('.notification-close');
        if (closeBtn) {
            removeNotification(closeBtn);
        }
    }, 5000);
}

function removeNotification(button) {
    const notification = button.closest('.notification');
    if (notification) {
        notification.remove();
    }
}

// Dashboard functions
async function loadDashboard() {
    console.log('Loading dashboard...');
    
    try {
        // Test server connection first
        console.log('Testing server connection...');
        
        const [statisticsResult, patientsResult] = await Promise.all([
            apiRequest('/api/statistics'),
            apiRequest('/api/patients')
        ]);
        
        const stats = statisticsResult.data;
        const patients = patientsResult.data;
        
        console.log('Statistics:', stats);
        console.log('Patients:', patients);
        
        // Update header stats
        updateElementText('total-patients', stats.total_patients);
        updateElementText('total-doctors', stats.total_doctors);
        
        // Update dashboard stats
        updateElementText('inpatients-count', stats.inpatients);
        updateElementText('outpatients-count', stats.outpatients);
        updateElementText('discharged-count', stats.discharged);
        updateElementText('total-revenue', `₹${stats.total_revenue.toFixed(2)}`);
        
        // Load recent patients
        loadRecentPatients(patients);
        loadCurrentInpatients(patients);
        
        console.log('Dashboard loaded successfully');
        
    } catch (error) {
        console.error('Error loading dashboard:', error);
        
        // Show fallback message
        const dashboardSection = document.getElementById('dashboard');
        if (dashboardSection) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            errorDiv.innerHTML = `
                <h3>Unable to load data</h3>
                <p>Please ensure the Flask server is running:</p>
                <code>python web_server.py</code>
                <p>Then refresh this page.</p>
            `;
            dashboardSection.appendChild(errorDiv);
        }
    }
}

// Helper function to safely update element text
function updateElementText(elementId, text) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = text;
    } else {
        console.warn(`Element with ID '${elementId}' not found`);
    }
}

function loadRecentPatients(patients) {
    console.log('Loading recent patients...');
    
    const container = document.getElementById('recent-patients');
    if (!container) {
        console.error('Recent patients container not found');
        return;
    }
    
    container.innerHTML = '';
    
    const patientEntries = Object.entries(patients);
    const recentPatients = patientEntries.slice(-5).reverse();
    
    console.log(`Found ${recentPatients.length} recent patients`);
    
    if (recentPatients.length === 0) {
        container.innerHTML = '<p class="text-center">No patients registered yet.</p>';
        return;
    }
    
    recentPatients.forEach(([patientId, patient]) => {
        const patientItem = createPatientItem(patientId, patient);
        container.appendChild(patientItem);
    });
}

function loadCurrentInpatients(patients) {
    console.log('Loading current inpatients...');
    
    const container = document.getElementById('current-inpatients');
    if (!container) {
        console.error('Current inpatients container not found');
        return;
    }
    
    container.innerHTML = '';
    
    const inpatients = Object.entries(patients).filter(([id, patient]) => patient.status === 'inpatient');
    
    console.log(`Found ${inpatients.length} inpatients`);
    
    if (inpatients.length === 0) {
        container.innerHTML = '<p class="text-center">No inpatients currently.</p>';
        return;
    }
    
    inpatients.forEach(([patientId, patient]) => {
        const patientItem = createPatientItem(patientId, patient);
        container.appendChild(patientItem);
    });
}

function createPatientItem(patientId, patient) {
    const item = document.createElement('div');
    item.className = 'patient-item';
    
    item.innerHTML = `
        <div class="patient-info">
            <h4>${patient.name}</h4>
            <p>ID: ${patientId} | ${patient.age} years | ${patient.gender}</p>
            <p>Status: <span class="status-badge status-${patient.status}">${patient.status}</span></p>
        </div>
        <button class="btn btn-secondary btn-sm" onclick="viewPatientDetails('${patientId}')">
            <i class="fas fa-eye"></i> View
        </button>
    `;
    
    return item;
}

// Doctor registration
async function handleDoctorRegistration(e) {
    e.preventDefault();
    console.log('Handling doctor registration...');
    
    const name = document.getElementById('doctor-name').value.trim();
    const specialization = document.getElementById('doctor-specialization').value;
    
    console.log(`Doctor data: ${name}, ${specialization}`);
    
    if (!name || !specialization) {
        showNotification('Error', 'Please fill in all required fields.', 'error');
        return;
    }
    
    try {
        const result = await apiRequest('/api/doctors', 'POST', {
            name: name,
            specialization: specialization
        });
        
        showNotification('Success', result.message, 'success');
        document.getElementById('doctor-form').reset();
        loadDashboard();
        
    } catch (error) {
        console.error('Error registering doctor:', error);
    }
}

// Patient registration
async function handlePatientRegistration(e) {
    e.preventDefault();
    console.log('Handling patient registration...');
    
    const name = document.getElementById('patient-name').value.trim();
    const age = document.getElementById('patient-age').value;
    const gender = document.getElementById('patient-gender').value;
    const condition = document.getElementById('condition').value;
    
    console.log(`Patient data: ${name}, ${age}, ${gender}, ${condition}, symptoms:`, symptoms);
    
    if (!name || !age || !gender || !condition || symptoms.length === 0) {
        showNotification('Error', 'Please fill in all required fields and add at least one symptom.', 'error');
        return;
    }
    
    try {
        const result = await apiRequest('/api/patients', 'POST', {
            name: name,
            age: parseInt(age),
            gender: gender,
            symptoms: symptoms,
            condition: condition
        });
        
        showNotification('Success', result.message, 'success');
        clearPatientForm();
        loadDashboard();
        
    } catch (error) {
        console.error('Error registering patient:', error);
    }
}

// Symptom management
function addSymptom() {
    const input = document.getElementById('symptom-input');
    if (!input) {
        console.error('Symptom input not found');
        return;
    }
    
    const symptom = input.value.trim();
    console.log(`Adding symptom: ${symptom}`);
    
    if (symptom && !symptoms.includes(symptom)) {
        symptoms.push(symptom);
        input.value = '';
        updateSymptomsDisplay();
        console.log('Symptoms list:', symptoms);
    }
}

function removeSymptom(index) {
    console.log(`Removing symptom at index: ${index}`);
    symptoms.splice(index, 1);
    updateSymptomsDisplay();
}

function updateSymptomsDisplay() {
    const container = document.getElementById('symptoms-list');
    if (!container) {
        console.error('Symptoms list container not found');
        return;
    }
    
    container.innerHTML = '';
    
    symptoms.forEach((symptom, index) => {
        const tag = document.createElement('span');
        tag.className = 'symptom-tag';
        tag.innerHTML = `
            ${symptom}
            <button type="button" class="remove-btn" onclick="removeSymptom(${index})">×</button>
        `;
        container.appendChild(tag);
    });
}

function clearPatientForm() {
    const form = document.getElementById('patient-form');
    if (form) {
        form.reset();
    }
    symptoms = [];
    updateSymptomsDisplay();
}

// Load patients
async function loadPatients() {
    console.log('Loading patients...');
    
    try {
        const result = await apiRequest('/api/patients');
        const patients = result.data;
        const tbody = document.querySelector('#patients-table tbody');
        
        if (!tbody) {
            console.error('Patients table body not found');
            return;
        }
        
        tbody.innerHTML = '';
        
        console.log(`Displaying ${Object.keys(patients).length} patients`);
        
        Object.entries(patients).forEach(([patientId, patient]) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${patientId}</td>
                <td>${patient.name}</td>
                <td>${patient.age}</td>
                <td>${patient.gender}</td>
                <td><span class="status-badge status-${patient.status}">${patient.status}</span></td>
                <td>${patient.assigned_doctor || 'Not assigned'}</td>
                <td>₹${patient.bill_amount.toFixed(2)}</td>
                <td>
                    <button class="btn btn-secondary btn-sm" onclick="viewPatientDetails('${patientId}')">
                        <i class="fas fa-eye"></i> View
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
        
        if (Object.keys(patients).length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" class="text-center">No patients found.</td></tr>';
        }
    } catch (error) {
        console.error('Error loading patients:', error);
    }
}

// Load doctors
async function loadDoctors() {
    console.log('Loading doctors...');
    
    try {
        const result = await apiRequest('/api/doctors');
        const doctors = result.data;
        const tbody = document.querySelector('#doctors-table tbody');
        
        if (!tbody) {
            console.error('Doctors table body not found');
            return;
        }
        
        tbody.innerHTML = '';
        
        console.log(`Displaying ${Object.keys(doctors).length} doctors`);
        
        Object.entries(doctors).forEach(([doctorId, doctor]) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${doctorId}</td>
                <td>${doctor.name}</td>
                <td>${doctor.specialization}</td>
                <td>${doctor.patients.length}</td>
            `;
            tbody.appendChild(row);
        });
        
        if (Object.keys(doctors).length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center">No doctors found.</td></tr>';
        }
    } catch (error) {
        console.error('Error loading doctors:', error);
    }
}

// Patient details
async function viewPatientDetails(patientId) {
    console.log(`Viewing details for patient: ${patientId}`);
    
    try {
        const result = await apiRequest(`/api/patients/${patientId}`);
        const patient = result.data;
        
        const modalTitle = document.getElementById('modal-patient-title');
        const modalBody = document.getElementById('patient-modal-body');
        
        if (!modalTitle || !modalBody) {
            console.error('Modal elements not found');
            return;
        }
        
        modalTitle.textContent = `Patient Details - ${patient.name}`;
        modalBody.innerHTML = createPatientDetailsHTML(patient);
        
        showModal('patient-modal');
    } catch (error) {
        console.error('Error loading patient details:', error);
    }
}

function createPatientDetailsHTML(patient) {
    let html = `
        <div class="patient-details">
            <div class="detail-group">
                <span class="detail-label">Patient ID:</span>
                <span class="detail-value">${patient.id}</span>
            </div>
            <div class="detail-group">
                <span class="detail-label">Name:</span>
                <span class="detail-value">${patient.name}</span>
            </div>
            <div class="detail-group">
                <span class="detail-label">Age:</span>
                <span class="detail-value">${patient.age}</span>
            </div>
            <div class="detail-group">
                <span class="detail-label">Gender:</span>
                <span class="detail-value">${patient.gender}</span>
            </div>
            <div class="detail-group">
                <span class="detail-label">Status:</span>
                <span class="detail-value"><span class="status-badge status-${patient.status}">${patient.status}</span></span>
            </div>
            <div class="detail-group">
                <span class="detail-label">Symptoms:</span>
                <span class="detail-value">${patient.symptoms.join(', ')}</span>
            </div>
            <div class="detail-group">
                <span class="detail-label">Assigned Doctor:</span>
                <span class="detail-value">${patient.assigned_doctor || 'Not assigned'}</span>
            </div>
            <div class="detail-group">
                <span class="detail-label">Bill Amount:</span>
                <span class="detail-value">₹${patient.bill_amount.toFixed(2)}</span>
            </div>
    `;
    
    if (patient.admission) {
        html += `
            <div class="detail-group">
                <span class="detail-label">Admission Date:</span>
                <span class="detail-value">${patient.admission}</span>
            </div>
        `;
    }
    
    if (patient.discharge_date) {
        html += `
            <div class="detail-group">
                <span class="detail-label">Discharge Date:</span>
                <span class="detail-value">${patient.discharge_date}</span>
            </div>
        `;
    }
    
    if (patient.history && patient.history.length > 0) {
        html += `
            <div class="history-section">
                <h4>Medical History</h4>
        `;
        
        patient.history.forEach(entry => {
            html += `
                <div class="history-entry">
                    <strong>${entry.date}:</strong> ${entry.notes}
                </div>
            `;
        });
        
        html += '</div>';
    }
    
    html += '</div>';
    return html;
}

// Treatment functions
async function searchPatientForTreatment() {
    const patientId = document.getElementById('treatment-patient-id').value.trim();
    console.log(`Searching for patient: ${patientId}`);
    
    if (!patientId) {
        showNotification('Error', 'Please enter a patient ID.', 'error');
        return;
    }
    
    try {
        const result = await apiRequest(`/api/patients/${patientId}`);
        const patient = result.data;
        
        if (patient.status !== 'inpatient') {
            showNotification('Error', 'Patient is not admitted for treatment.', 'error');
            return;
        }
        
        currentPatient = patient;
        displayPatientInfo(patient);
        
    } catch (error) {
        document.getElementById('patient-info').style.display = 'none';
        currentPatient = null;
    }
}

function displayPatientInfo(patient) {
    const container = document.getElementById('patient-info');
    if (!container) {
        console.error('Patient info container not found');
        return;
    }
    
    container.innerHTML = `
        <h4>${patient.name} (${patient.id})</h4>
        <p><strong>Status:</strong> <span class="status-badge status-${patient.status}">${patient.status}</span></p>
        <p><strong>Assigned Doctor:</strong> ${patient.assigned_doctor}</p>
        <p><strong>Admission Date:</strong> ${patient.admission}</p>
        <p><strong>Current Bill:</strong> ₹${patient.bill_amount.toFixed(2)}</p>
    `;
    container.style.display = 'block';
}

async function handleTreatment(e) {
    e.preventDefault();
    console.log('Handling treatment...');
    
    if (!currentPatient) {
        showNotification('Error', 'Please search for a patient first.', 'error');
        return;
    }
    
    const patientId = document.getElementById('treatment-patient-id').value.trim();
    const note = document.getElementById('condition-note').value.trim();
    const treatment = document.getElementById('treatment-details').value.trim();
    const cost = parseFloat(document.getElementById('treatment-cost').value) || 0;
    const discharge = document.getElementById('discharge-patient').checked;

    console.log(`Treatment data: ${note}, ${treatment}, cost: ${cost}, discharge: ${discharge}`);

    if (!note || !treatment || cost <= 0) {
        showNotification('Error', 'Please fill in all required fields and enter a valid cost.', 'error');
        return;
    }

    try {
        const result = await apiRequest('/api/treatment', 'POST', {
            patient_id: patientId,
            note: note,
            treatment: treatment,
            cost: cost,
            discharge: discharge
        });

        showNotification('Success', result.message, 'success');
        document.getElementById('treatment-form').reset();
        document.getElementById('patient-info').style.display = 'none';
        currentPatient = null;
        loadDashboard();

    } catch (error) {
        console.error('Error processing treatment:', error);
    }
}

function toggleDischargeSection() {
    const discharge = document.getElementById('discharge-patient').checked;
    const dischargeSection = document.getElementById('discharge-section');
    
    if (dischargeSection) {
        dischargeSection.style.display = discharge ? 'block' : 'none';
    }
    
    const billAmountInput = document.getElementById('bill-amount');
    if (billAmountInput) {
        billAmountInput.required = discharge;
    }
}

// Modal functions
function showModal(modalId) {
    console.log(`Showing modal: ${modalId}`);
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('show');
    } else {
        console.error(`Modal ${modalId} not found`);
    }
}

function closeModal(modalId) {
    console.log(`Closing modal: ${modalId}`);
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('show');
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modal => {
            modal.classList.remove('show');
        });
    }
}

// Add some test functions for debugging
function testServerConnection() {
    console.log('Testing server connection...');
    fetch('/api/statistics')
        .then(response => {
            console.log('Server response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Server response data:', data);
            showNotification('Success', 'Server connection successful!', 'success');
        })
        .catch(error => {
            console.error('Server connection failed:', error);
            showNotification('Error', 'Server connection failed. Make sure Flask server is running.', 'error');
        });
}

// Expose test function globally for debugging
window.testServerConnection = testServerConnection;