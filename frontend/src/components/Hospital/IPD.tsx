import React, { useState, useEffect } from 'react';
import './Hospital.css';

interface Admission {
  id: number;
  admission_id: string;
  patient_name: string;
  doctor_name: string;
  ward: string;
  bed_number: string;
  admission_date: string;
  discharge_date: string;
  status: string;
  diagnosis: string;
}

interface Bed {
  id: number;
  bed_number: string;
  ward: string;
  bed_type: string;
  is_occupied: boolean;
  daily_rate: number;
}

const IPD: React.FC = () => {
  const [activeTab, setActiveTab] = useState('admissions');
  const [admissions, setAdmissions] = useState<Admission[]>([]);
  const [beds, setBeds] = useState<Bed[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [filter, setFilter] = useState('admitted');
  const [formData, setFormData] = useState({
    patient_id: '',
    doctor_id: '',
    bed_id: '',
    diagnosis: '',
    notes: '',
  });

  const API_URL = 'http://localhost:5000/api';

  useEffect(() => {
    if (activeTab === 'admissions') {
      fetchAdmissions();
    } else {
      fetchBeds();
    }
  }, [activeTab, filter]);

  const getToken = () => localStorage.getItem('token');

  const fetchAdmissions = async () => {
    try {
      const response = await fetch(`${API_URL}/ipd/admissions?status=${filter}`, {
        headers: { 'Authorization': `Bearer ${getToken()}` },
      });
      if (response.ok) {
        const data = await response.json();
        setAdmissions(data.admissions || []);
      }
    } catch (err) {
      console.error('Error fetching admissions:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchBeds = async () => {
    try {
      const response = await fetch(`${API_URL}/ipd/beds`, {
        headers: { 'Authorization': `Bearer ${getToken()}` },
      });
      if (response.ok) {
        const data = await response.json();
        setBeds(data.beds || []);
      }
    } catch (err) {
      console.error('Error fetching beds:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAdmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API_URL}/ipd/admissions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getToken()}`,
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        setShowModal(false);
        fetchAdmissions();
        fetchBeds();
      }
    } catch (err) {
      console.error('Error admitting patient:', err);
    }
  };

  const handleDischarge = async (id: number) => {
    if (!window.confirm('Are you sure you want to discharge this patient?')) return;
    try {
      await fetch(`${API_URL}/ipd/admissions/${id}/discharge`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${getToken()}` },
      });
      fetchAdmissions();
      fetchBeds();
    } catch (err) {
      console.error('Error discharging patient:', err);
    }
  };

  const getWardStats = () => {
    const wards = beds.reduce((acc, bed) => {
      if (!acc[bed.ward]) {
        acc[bed.ward] = { total: 0, occupied: 0, available: 0 };
      }
      acc[bed.ward].total++;
      if (bed.is_occupied) {
        acc[bed.ward].occupied++;
      } else {
        acc[bed.ward].available++;
      }
      return acc;
    }, {} as Record<string, { total: number; occupied: number; available: number }>);
    return Object.entries(wards);
  };

  if (loading) return <div className="loading">Loading IPD...</div>;

  return (
    <div className="hospital-module">
      <div className="module-header">
        <div>
          <h1>🏨 In-Patient Department</h1>
          <p>Admissions and bed management</p>
        </div>
        <button className="btn-primary" onClick={() => setShowModal(true)}>
          + New Admission
        </button>
      </div>

      {/* Ward Summary */}
      <div className="ward-summary">
        {getWardStats().map(([ward, stats]) => (
          <div key={ward} className="ward-card">
            <h4>{ward}</h4>
            <div className="ward-stats">
              <span className="available">{stats.available} Available</span>
              <span className="occupied">{stats.occupied} Occupied</span>
              <span className="total">{stats.total} Total</span>
            </div>
            <div className="occupancy-bar">
              <div 
                className="filled" 
                style={{ width: `${(stats.occupied / stats.total) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      <div className="tab-navigation">
        <button
          className={activeTab === 'admissions' ? 'active' : ''}
          onClick={() => setActiveTab('admissions')}
        >
          Current Admissions
        </button>
        <button
          className={activeTab === 'beds' ? 'active' : ''}
          onClick={() => setActiveTab('beds')}
        >
          Bed Management
        </button>
      </div>

      {activeTab === 'admissions' && (
        <>
          <div className="filter-tabs">
            {['admitted', 'discharged'].map((f) => (
              <button
                key={f}
                className={filter === f ? 'active' : ''}
                onClick={() => setFilter(f)}
              >
                {f.charAt(0).toUpperCase() + f.slice(1)}
              </button>
            ))}
          </div>

          <div className="data-table">
            <table>
              <thead>
                <tr>
                  <th>Admission ID</th>
                  <th>Patient</th>
                  <th>Doctor</th>
                  <th>Ward / Bed</th>
                  <th>Admitted On</th>
                  <th>Diagnosis</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {admissions.length === 0 ? (
                  <tr><td colSpan={7} className="no-data">No {filter} patients</td></tr>
                ) : (
                  admissions.map((adm) => (
                    <tr key={adm.id}>
                      <td>{adm.admission_id}</td>
                      <td>{adm.patient_name}</td>
                      <td>Dr. {adm.doctor_name}</td>
                      <td>{adm.ward} - {adm.bed_number}</td>
                      <td>{new Date(adm.admission_date).toLocaleDateString()}</td>
                      <td>{adm.diagnosis || '-'}</td>
                      <td>
                        {adm.status === 'admitted' && (
                          <>
                            <button className="btn-sm">View</button>
                            <button 
                              className="btn-sm danger"
                              onClick={() => handleDischarge(adm.id)}
                            >
                              Discharge
                            </button>
                          </>
                        )}
                        {adm.status === 'discharged' && (
                          <button className="btn-sm view">Summary</button>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </>
      )}

      {activeTab === 'beds' && (
        <div className="beds-grid">
          {beds.map((bed) => (
            <div key={bed.id} className={`bed-card ${bed.is_occupied ? 'occupied' : 'available'}`}>
              <div className="bed-icon">🛏️</div>
              <div className="bed-info">
                <h4>{bed.bed_number}</h4>
                <p>{bed.ward}</p>
                <span className="bed-type">{bed.bed_type}</span>
              </div>
              <div className={`bed-status ${bed.is_occupied ? 'occupied' : 'available'}`}>
                {bed.is_occupied ? 'Occupied' : 'Available'}
              </div>
              <div className="bed-rate">₹{bed.daily_rate}/day</div>
            </div>
          ))}
        </div>
      )}

      {/* Admission Modal */}
      {showModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2>New Patient Admission</h2>
              <button className="close-btn" onClick={() => setShowModal(false)}>×</button>
            </div>
            <form onSubmit={handleAdmit}>
              <div className="form-grid">
                <div className="form-group">
                  <label>Patient ID *</label>
                  <input
                    type="text"
                    required
                    value={formData.patient_id}
                    onChange={(e) => setFormData({...formData, patient_id: e.target.value})}
                    placeholder="Enter patient ID"
                  />
                </div>
                <div className="form-group">
                  <label>Attending Doctor ID *</label>
                  <input
                    type="text"
                    required
                    value={formData.doctor_id}
                    onChange={(e) => setFormData({...formData, doctor_id: e.target.value})}
                    placeholder="Enter doctor ID"
                  />
                </div>
                <div className="form-group">
                  <label>Bed *</label>
                  <select
                    required
                    value={formData.bed_id}
                    onChange={(e) => setFormData({...formData, bed_id: e.target.value})}
                  >
                    <option value="">Select available bed</option>
                    {beds.filter(b => !b.is_occupied).map((bed) => (
                      <option key={bed.id} value={bed.id}>
                        {bed.ward} - {bed.bed_number} ({bed.bed_type}) - ₹{bed.daily_rate}/day
                      </option>
                    ))}
                  </select>
                </div>
                <div className="form-group full-width">
                  <label>Diagnosis</label>
                  <textarea
                    value={formData.diagnosis}
                    onChange={(e) => setFormData({...formData, diagnosis: e.target.value})}
                    placeholder="Primary diagnosis"
                  />
                </div>
                <div className="form-group full-width">
                  <label>Notes</label>
                  <textarea
                    value={formData.notes}
                    onChange={(e) => setFormData({...formData, notes: e.target.value})}
                    placeholder="Additional notes"
                  />
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn-secondary" onClick={() => setShowModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">Admit Patient</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default IPD;
