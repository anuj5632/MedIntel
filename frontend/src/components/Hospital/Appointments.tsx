import React, { useState, useEffect } from 'react';
import './Hospital.css';

interface Appointment {
  id: number;
  appointment_id: string;
  patient_id: number;
  patient_name: string;
  doctor_id: number;
  doctor_name: string;
  appointment_date: string;
  appointment_time: string;
  type: string;
  status: string;
  reason: string;
  notes: string;
}

const Appointments: React.FC = () => {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [formData, setFormData] = useState({
    patient_id: '',
    doctor_id: '',
    appointment_date: '',
    appointment_time: '',
    type: 'consultation',
    reason: '',
  });

  const API_URL = 'http://localhost:5000/api';

  useEffect(() => {
    fetchAppointments();
  }, [selectedDate]);

  const getToken = () => localStorage.getItem('token');

  const fetchAppointments = async () => {
    try {
      const response = await fetch(`${API_URL}/appointments?date=${selectedDate}`, {
        headers: { 'Authorization': `Bearer ${getToken()}` },
      });
      if (response.ok) {
        const data = await response.json();
        setAppointments(data.appointments || []);
      }
    } catch (err) {
      console.error('Error fetching appointments:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API_URL}/appointments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getToken()}`,
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        setShowModal(false);
        fetchAppointments();
      }
    } catch (err) {
      console.error('Error creating appointment:', err);
    }
  };

  const updateStatus = async (id: number, status: string) => {
    try {
      await fetch(`${API_URL}/appointments/${id}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getToken()}`,
        },
        body: JSON.stringify({ status }),
      });
      fetchAppointments();
    } catch (err) {
      console.error('Error updating appointment:', err);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      scheduled: 'blue',
      'in-queue': 'orange',
      'in-progress': 'purple',
      completed: 'green',
      cancelled: 'red',
      'no-show': 'gray',
    };
    return colors[status] || 'gray';
  };

  if (loading) return <div className="loading">Loading appointments...</div>;

  return (
    <div className="hospital-module">
      <div className="module-header">
        <div>
          <h1>📅 Appointments</h1>
          <p>Manage patient appointments and scheduling</p>
        </div>
        <button className="btn-primary" onClick={() => setShowModal(true)}>
          + New Appointment
        </button>
      </div>

      <div className="filter-bar">
        <div className="date-picker">
          <label>Date:</label>
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
          />
        </div>
        <div className="quick-dates">
          <button onClick={() => setSelectedDate(new Date().toISOString().split('T')[0])}>
            Today
          </button>
          <button onClick={() => {
            const tomorrow = new Date();
            tomorrow.setDate(tomorrow.getDate() + 1);
            setSelectedDate(tomorrow.toISOString().split('T')[0]);
          }}>
            Tomorrow
          </button>
        </div>
      </div>

      <div className="appointments-grid">
        {appointments.length === 0 ? (
          <div className="no-data-card">
            <span>📅</span>
            <p>No appointments scheduled for this date</p>
          </div>
        ) : (
          appointments.map((apt) => (
            <div key={apt.id} className={`appointment-card status-${getStatusColor(apt.status)}`}>
              <div className="apt-header">
                <span className="apt-time">{apt.appointment_time}</span>
                <span className={`status-badge ${apt.status}`}>{apt.status}</span>
              </div>
              <div className="apt-body">
                <h4>{apt.patient_name}</h4>
                <p className="doctor">Dr. {apt.doctor_name}</p>
                <p className="type">{apt.type}</p>
                {apt.reason && <p className="reason">{apt.reason}</p>}
              </div>
              <div className="apt-actions">
                {apt.status === 'scheduled' && (
                  <>
                    <button onClick={() => updateStatus(apt.id, 'in-queue')}>Check In</button>
                    <button className="danger" onClick={() => updateStatus(apt.id, 'cancelled')}>Cancel</button>
                  </>
                )}
                {apt.status === 'in-queue' && (
                  <button onClick={() => updateStatus(apt.id, 'in-progress')}>Start Consultation</button>
                )}
                {apt.status === 'in-progress' && (
                  <button onClick={() => updateStatus(apt.id, 'completed')}>Complete</button>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {showModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2>New Appointment</h2>
              <button className="close-btn" onClick={() => setShowModal(false)}>×</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-grid">
                <div className="form-group">
                  <label>Patient ID *</label>
                  <input
                    type="text"
                    required
                    placeholder="Enter patient ID"
                    value={formData.patient_id}
                    onChange={(e) => setFormData({...formData, patient_id: e.target.value})}
                  />
                </div>
                <div className="form-group">
                  <label>Doctor ID *</label>
                  <input
                    type="text"
                    required
                    placeholder="Enter doctor ID"
                    value={formData.doctor_id}
                    onChange={(e) => setFormData({...formData, doctor_id: e.target.value})}
                  />
                </div>
                <div className="form-group">
                  <label>Date *</label>
                  <input
                    type="date"
                    required
                    value={formData.appointment_date}
                    onChange={(e) => setFormData({...formData, appointment_date: e.target.value})}
                  />
                </div>
                <div className="form-group">
                  <label>Time *</label>
                  <input
                    type="time"
                    required
                    value={formData.appointment_time}
                    onChange={(e) => setFormData({...formData, appointment_time: e.target.value})}
                  />
                </div>
                <div className="form-group">
                  <label>Type</label>
                  <select
                    value={formData.type}
                    onChange={(e) => setFormData({...formData, type: e.target.value})}
                  >
                    <option value="consultation">Consultation</option>
                    <option value="follow-up">Follow-up</option>
                    <option value="emergency">Emergency</option>
                    <option value="procedure">Procedure</option>
                  </select>
                </div>
                <div className="form-group full-width">
                  <label>Reason</label>
                  <textarea
                    value={formData.reason}
                    onChange={(e) => setFormData({...formData, reason: e.target.value})}
                    placeholder="Brief reason for appointment"
                  />
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn-secondary" onClick={() => setShowModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">Book Appointment</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Appointments;
