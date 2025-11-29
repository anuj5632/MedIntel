import React, { useState, useEffect } from 'react';
import './Hospital.css';

interface Medicine {
  id: number;
  medicine_id: string;
  name: string;
  generic_name: string;
  category: string;
  manufacturer: string;
  unit_price: number;
  stock_quantity: number;
  reorder_level: number;
  expiry_date: string;
  is_active: boolean;
}

interface Prescription {
  id: number;
  prescription_id: string;
  patient_name: string;
  doctor_name: string;
  prescription_date: string;
  is_dispensed: boolean;
  items: { medicine_name: string; quantity: number; dosage: string }[];
}

const Pharmacy: React.FC = () => {
  const [activeTab, setActiveTab] = useState('medicines');
  const [medicines, setMedicines] = useState<Medicine[]>([]);
  const [prescriptions, setPrescriptions] = useState<Prescription[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [formData, setFormData] = useState({
    name: '',
    generic_name: '',
    category: 'tablet',
    manufacturer: '',
    unit_price: 0,
    stock_quantity: 0,
    reorder_level: 10,
    expiry_date: '',
  });

  const API_URL = 'http://localhost:5000/api';

  useEffect(() => {
    if (activeTab === 'medicines') {
      fetchMedicines();
    } else {
      fetchPrescriptions();
    }
  }, [activeTab, searchTerm]);

  const getToken = () => localStorage.getItem('token');

  const fetchMedicines = async () => {
    try {
      const response = await fetch(`${API_URL}/pharmacy/medicines?search=${searchTerm}`, {
        headers: { 'Authorization': `Bearer ${getToken()}` },
      });
      if (response.ok) {
        const data = await response.json();
        setMedicines(data.medicines || []);
      }
    } catch (err) {
      console.error('Error fetching medicines:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchPrescriptions = async () => {
    try {
      const response = await fetch(`${API_URL}/pharmacy/prescriptions?pending=true`, {
        headers: { 'Authorization': `Bearer ${getToken()}` },
      });
      if (response.ok) {
        const data = await response.json();
        setPrescriptions(data.prescriptions || []);
      }
    } catch (err) {
      console.error('Error fetching prescriptions:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API_URL}/pharmacy/medicines`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getToken()}`,
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        setShowModal(false);
        fetchMedicines();
      }
    } catch (err) {
      console.error('Error adding medicine:', err);
    }
  };

  const dispensePrescription = async (id: number) => {
    try {
      await fetch(`${API_URL}/pharmacy/prescriptions/${id}/dispense`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${getToken()}` },
      });
      fetchPrescriptions();
    } catch (err) {
      console.error('Error dispensing prescription:', err);
    }
  };

  const getStockStatus = (medicine: Medicine) => {
    if (medicine.stock_quantity <= 0) return 'out-of-stock';
    if (medicine.stock_quantity <= medicine.reorder_level) return 'low-stock';
    return 'in-stock';
  };

  if (loading) return <div className="loading">Loading pharmacy...</div>;

  return (
    <div className="hospital-module">
      <div className="module-header">
        <div>
          <h1>💊 Pharmacy</h1>
          <p>Medicine inventory and prescription management</p>
        </div>
        <button className="btn-primary" onClick={() => setShowModal(true)}>
          + Add Medicine
        </button>
      </div>

      <div className="tab-navigation">
        <button
          className={activeTab === 'medicines' ? 'active' : ''}
          onClick={() => setActiveTab('medicines')}
        >
          Medicines Inventory
        </button>
        <button
          className={activeTab === 'prescriptions' ? 'active' : ''}
          onClick={() => setActiveTab('prescriptions')}
        >
          Pending Prescriptions
        </button>
      </div>

      {activeTab === 'medicines' && (
        <>
          <div className="search-bar">
            <input
              type="text"
              placeholder="Search medicines..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <div className="data-table">
            <table>
              <thead>
                <tr>
                  <th>Medicine</th>
                  <th>Generic Name</th>
                  <th>Category</th>
                  <th>Price</th>
                  <th>Stock</th>
                  <th>Expiry</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {medicines.length === 0 ? (
                  <tr><td colSpan={7} className="no-data">No medicines found</td></tr>
                ) : (
                  medicines.map((med) => (
                    <tr key={med.id}>
                      <td>{med.name}</td>
                      <td>{med.generic_name || '-'}</td>
                      <td>{med.category}</td>
                      <td>₹{med.unit_price}</td>
                      <td>{med.stock_quantity}</td>
                      <td>{med.expiry_date?.split('T')[0] || '-'}</td>
                      <td>
                        <span className={`stock-badge ${getStockStatus(med)}`}>
                          {getStockStatus(med).replace('-', ' ')}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </>
      )}

      {activeTab === 'prescriptions' && (
        <div className="prescriptions-list">
          {prescriptions.length === 0 ? (
            <div className="no-data-card">
              <span>✅</span>
              <p>No pending prescriptions</p>
            </div>
          ) : (
            prescriptions.map((rx) => (
              <div key={rx.id} className="prescription-card">
                <div className="rx-header">
                  <span className="rx-id">{rx.prescription_id}</span>
                  <span className="rx-date">{new Date(rx.prescription_date).toLocaleDateString()}</span>
                </div>
                <div className="rx-body">
                  <h4>{rx.patient_name}</h4>
                  <p className="doctor">Prescribed by: Dr. {rx.doctor_name}</p>
                  <div className="rx-items">
                    {rx.items?.map((item, i) => (
                      <div key={i} className="rx-item">
                        <span>{item.medicine_name}</span>
                        <span>Qty: {item.quantity}</span>
                        <span>{item.dosage}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="rx-actions">
                  <button className="btn-primary" onClick={() => dispensePrescription(rx.id)}>
                    Dispense
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {showModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2>Add New Medicine</h2>
              <button className="close-btn" onClick={() => setShowModal(false)}>×</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-grid">
                <div className="form-group">
                  <label>Medicine Name *</label>
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                  />
                </div>
                <div className="form-group">
                  <label>Generic Name</label>
                  <input
                    type="text"
                    value={formData.generic_name}
                    onChange={(e) => setFormData({...formData, generic_name: e.target.value})}
                  />
                </div>
                <div className="form-group">
                  <label>Category</label>
                  <select
                    value={formData.category}
                    onChange={(e) => setFormData({...formData, category: e.target.value})}
                  >
                    <option value="tablet">Tablet</option>
                    <option value="capsule">Capsule</option>
                    <option value="syrup">Syrup</option>
                    <option value="injection">Injection</option>
                    <option value="ointment">Ointment</option>
                    <option value="drops">Drops</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Manufacturer</label>
                  <input
                    type="text"
                    value={formData.manufacturer}
                    onChange={(e) => setFormData({...formData, manufacturer: e.target.value})}
                  />
                </div>
                <div className="form-group">
                  <label>Unit Price *</label>
                  <input
                    type="number"
                    required
                    value={formData.unit_price}
                    onChange={(e) => setFormData({...formData, unit_price: parseFloat(e.target.value)})}
                  />
                </div>
                <div className="form-group">
                  <label>Initial Stock</label>
                  <input
                    type="number"
                    value={formData.stock_quantity}
                    onChange={(e) => setFormData({...formData, stock_quantity: parseInt(e.target.value)})}
                  />
                </div>
                <div className="form-group">
                  <label>Reorder Level</label>
                  <input
                    type="number"
                    value={formData.reorder_level}
                    onChange={(e) => setFormData({...formData, reorder_level: parseInt(e.target.value)})}
                  />
                </div>
                <div className="form-group">
                  <label>Expiry Date</label>
                  <input
                    type="date"
                    value={formData.expiry_date}
                    onChange={(e) => setFormData({...formData, expiry_date: e.target.value})}
                  />
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn-secondary" onClick={() => setShowModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">Add Medicine</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Pharmacy;
