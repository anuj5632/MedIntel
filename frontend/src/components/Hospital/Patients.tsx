import React, { useState, useEffect } from 'react';
import './Hospital.css';

interface Patient {
  id: number;
  patient_id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  date_of_birth: string;
  gender: string;
  blood_group: string;
  address: string;
  emergency_contact: string;
  is_active: boolean;
  created_at: string;
}

const Patients: React.FC = () => {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    date_of_birth: '',
    gender: 'male',
    blood_group: '',
    address: '',
    emergency_contact: '',
  });

  const API_URL = 'http://localhost:5000/api';

  useEffect(() => {
    fetchPatients();
  }, []);

  const getToken = () => localStorage.getItem('token');

  const fetchPatients = async () => {
    try {
      const response = await fetch(`${API_URL}/patients?search=${searchTerm}`, {
        headers: { 'Authorization': `Bearer ${getToken()}` },
      });
      if (response.ok) {
        const data = await response.json();
        setPatients(data.patients || []);
      }
    } catch (err) {
      console.error('Error fetching patients:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const url = selectedPatient 
        ? `${API_URL}/patients/${selectedPatient.id}`
        : `${API_URL}/patients`;
      
      const response = await fetch(url, {
        method: selectedPatient ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getToken()}`,
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        setShowModal(false);
        resetForm();
        fetchPatients();
      }
    } catch (err) {
      console.error('Error saving patient:', err);
    }
  };

  const resetForm = () => {
    setFormData({
      first_name: '',
      last_name: '',
      email: '',
      phone: '',
      date_of_birth: '',
      gender: 'male',
      blood_group: '',
      address: '',
      emergency_contact: '',
    });
    setSelectedPatient(null);
  };

  const handleEdit = (patient: Patient) => {
    setSelectedPatient(patient);
    setFormData({
      first_name: patient.first_name,
      last_name: patient.last_name,
      email: patient.email || '',
      phone: patient.phone || '',
      date_of_birth: patient.date_of_birth?.split('T')[0] || '',
      gender: patient.gender,
      blood_group: patient.blood_group || '',
      address: patient.address || '',
      emergency_contact: patient.emergency_contact || '',
    });
    setShowModal(true);
  };

  if (loading) return <div className="loading">Loading patients...</div>;

  return (
    <div className="hospital-module">
      <div className="module-header">
        <div>
          <h1>👥 Patient Management</h1>
          <p>Register and manage patient records</p>
        </div>
        <button className="btn-primary" onClick={() => { resetForm(); setShowModal(true); }}>
          + Register Patient
        </button>
      </div>

      <div className="search-bar">
        <input
          type="text"
          placeholder="Search patients by name, phone, or ID..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && fetchPatients()}
        />
        <button onClick={fetchPatients}>Search</button>
      </div>

      <div className="data-table">
        <table>
          <thead>
            <tr>
              <th>Patient ID</th>
              <th>Name</th>
              <th>Phone</th>
              <th>Gender</th>
              <th>Blood Group</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {patients.length === 0 ? (
              <tr><td colSpan={7} className="no-data">No patients found</td></tr>
            ) : (
              patients.map((patient) => (
                <tr key={patient.id}>
                  <td>{patient.patient_id}</td>
                  <td>{patient.first_name} {patient.last_name}</td>
                  <td>{patient.phone}</td>
                  <td>{patient.gender}</td>
                  <td>{patient.blood_group || '-'}</td>
                  <td>
                    <span className={`status ${patient.is_active ? 'active' : 'inactive'}`}>
                      {patient.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td>
                    <button className="btn-sm" onClick={() => handleEdit(patient)}>Edit</button>
                    <button className="btn-sm view">View</button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2>{selectedPatient ? 'Edit Patient' : 'Register New Patient'}</h2>
              <button className="close-btn" onClick={() => setShowModal(false)}>×</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-grid">
                <div className="form-group">
                  <label>First Name *</label>
                  <input
                    type="text"
                    required
                    value={formData.first_name}
                    onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                  />
                </div>
                <div className="form-group">
                  <label>Last Name *</label>
                  <input
                    type="text"
                    required
                    value={formData.last_name}
                    onChange={(e) => setFormData({...formData, last_name: e.target.value})}
                  />
                </div>
                <div className="form-group">
                  <label>Phone *</label>
                  <input
                    type="tel"
                    required
                    value={formData.phone}
                    onChange={(e) => setFormData({...formData, phone: e.target.value})}
                  />
                </div>
                <div className="form-group">
                  <label>Email</label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                  />
                </div>
                <div className="form-group">
                  <label>Date of Birth</label>
                  <input
                    type="date"
                    value={formData.date_of_birth}
                    onChange={(e) => setFormData({...formData, date_of_birth: e.target.value})}
                  />
                </div>
                <div className="form-group">
                  <label>Gender *</label>
                  <select
                    value={formData.gender}
                    onChange={(e) => setFormData({...formData, gender: e.target.value})}
                  >
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Blood Group</label>
                  <select
                    value={formData.blood_group}
                    onChange={(e) => setFormData({...formData, blood_group: e.target.value})}
                  >
                    <option value="">Select</option>
                    <option value="A+">A+</option>
                    <option value="A-">A-</option>
                    <option value="B+">B+</option>
                    <option value="B-">B-</option>
                    <option value="O+">O+</option>
                    <option value="O-">O-</option>
                    <option value="AB+">AB+</option>
                    <option value="AB-">AB-</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Emergency Contact</label>
                  <input
                    type="tel"
                    value={formData.emergency_contact}
                    onChange={(e) => setFormData({...formData, emergency_contact: e.target.value})}
                  />
                </div>
                <div className="form-group full-width">
                  <label>Address</label>
                  <textarea
                    value={formData.address}
                    onChange={(e) => setFormData({...formData, address: e.target.value})}
                  />
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn-secondary" onClick={() => setShowModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  {selectedPatient ? 'Update Patient' : 'Register Patient'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Patients;
