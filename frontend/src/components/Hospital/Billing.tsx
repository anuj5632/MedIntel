import React, { useState, useEffect } from 'react';
import './Hospital.css';

interface Bill {
  id: number;
  bill_number: string;
  patient_id: number;
  patient_name: string;
  bill_type: string;
  total_amount: number;
  discount: number;
  tax: number;
  final_amount: number;
  paid_amount: number;
  balance: number;
  payment_status: string;
  created_at: string;
}

const Billing: React.FC = () => {
  const [bills, setBills] = useState<Bill[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [selectedBill, setSelectedBill] = useState<Bill | null>(null);
  const [filter, setFilter] = useState('all');
  const [formData, setFormData] = useState({
    patient_id: '',
    bill_type: 'opd',
    items: [{ description: '', quantity: 1, unit_price: 0 }],
    discount: 0,
  });
  const [paymentAmount, setPaymentAmount] = useState(0);
  const [paymentMethod, setPaymentMethod] = useState('cash');

  const API_URL = 'http://localhost:5000/api';

  useEffect(() => {
    fetchBills();
  }, [filter]);

  const getToken = () => localStorage.getItem('token');

  const fetchBills = async () => {
    try {
      const url = filter === 'all' 
        ? `${API_URL}/billing`
        : `${API_URL}/billing?status=${filter}`;
      const response = await fetch(url, {
        headers: { 'Authorization': `Bearer ${getToken()}` },
      });
      if (response.ok) {
        const data = await response.json();
        setBills(data.bills || []);
      }
    } catch (err) {
      console.error('Error fetching bills:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API_URL}/billing`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getToken()}`,
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        setShowModal(false);
        fetchBills();
      }
    } catch (err) {
      console.error('Error creating bill:', err);
    }
  };

  const handlePayment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedBill) return;
    
    try {
      const response = await fetch(`${API_URL}/billing/${selectedBill.id}/payment`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getToken()}`,
        },
        body: JSON.stringify({ 
          amount: paymentAmount, 
          payment_method: paymentMethod 
        }),
      });

      if (response.ok) {
        setShowPaymentModal(false);
        setSelectedBill(null);
        fetchBills();
      }
    } catch (err) {
      console.error('Error processing payment:', err);
    }
  };

  const addItem = () => {
    setFormData({
      ...formData,
      items: [...formData.items, { description: '', quantity: 1, unit_price: 0 }],
    });
  };

  const updateItem = (index: number, field: string, value: string | number) => {
    const newItems = [...formData.items];
    newItems[index] = { ...newItems[index], [field]: value };
    setFormData({ ...formData, items: newItems });
  };

  const calculateTotal = () => {
    return formData.items.reduce((sum, item) => sum + (item.quantity * item.unit_price), 0);
  };

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      paid: 'green',
      pending: 'orange',
      partial: 'blue',
      cancelled: 'red',
    };
    return <span className={`status-badge ${colors[status] || 'gray'}`}>{status}</span>;
  };

  if (loading) return <div className="loading">Loading bills...</div>;

  return (
    <div className="hospital-module">
      <div className="module-header">
        <div>
          <h1>💳 Billing</h1>
          <p>Manage patient bills and payments</p>
        </div>
        <button className="btn-primary" onClick={() => setShowModal(true)}>
          + Create Bill
        </button>
      </div>

      <div className="filter-tabs">
        {['all', 'pending', 'partial', 'paid'].map((f) => (
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
              <th>Bill #</th>
              <th>Patient</th>
              <th>Type</th>
              <th>Amount</th>
              <th>Paid</th>
              <th>Balance</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {bills.length === 0 ? (
              <tr><td colSpan={8} className="no-data">No bills found</td></tr>
            ) : (
              bills.map((bill) => (
                <tr key={bill.id}>
                  <td>{bill.bill_number}</td>
                  <td>{bill.patient_name}</td>
                  <td>{bill.bill_type.toUpperCase()}</td>
                  <td>₹{bill.final_amount?.toLocaleString()}</td>
                  <td>₹{bill.paid_amount?.toLocaleString()}</td>
                  <td>₹{bill.balance?.toLocaleString()}</td>
                  <td>{getStatusBadge(bill.payment_status)}</td>
                  <td>
                    {bill.payment_status !== 'paid' && (
                      <button 
                        className="btn-sm"
                        onClick={() => {
                          setSelectedBill(bill);
                          setPaymentAmount(bill.balance);
                          setShowPaymentModal(true);
                        }}
                      >
                        Pay
                      </button>
                    )}
                    <button className="btn-sm view">Print</button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Create Bill Modal */}
      {showModal && (
        <div className="modal-overlay">
          <div className="modal large">
            <div className="modal-header">
              <h2>Create New Bill</h2>
              <button className="close-btn" onClick={() => setShowModal(false)}>×</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-grid">
                <div className="form-group">
                  <label>Patient ID *</label>
                  <input
                    type="text"
                    required
                    value={formData.patient_id}
                    onChange={(e) => setFormData({...formData, patient_id: e.target.value})}
                  />
                </div>
                <div className="form-group">
                  <label>Bill Type</label>
                  <select
                    value={formData.bill_type}
                    onChange={(e) => setFormData({...formData, bill_type: e.target.value})}
                  >
                    <option value="opd">OPD</option>
                    <option value="ipd">IPD</option>
                    <option value="pharmacy">Pharmacy</option>
                    <option value="lab">Laboratory</option>
                  </select>
                </div>
              </div>

              <div className="items-section">
                <h3>Bill Items</h3>
                {formData.items.map((item, index) => (
                  <div key={index} className="item-row">
                    <input
                      type="text"
                      placeholder="Description"
                      value={item.description}
                      onChange={(e) => updateItem(index, 'description', e.target.value)}
                    />
                    <input
                      type="number"
                      placeholder="Qty"
                      value={item.quantity}
                      onChange={(e) => updateItem(index, 'quantity', parseInt(e.target.value))}
                    />
                    <input
                      type="number"
                      placeholder="Price"
                      value={item.unit_price}
                      onChange={(e) => updateItem(index, 'unit_price', parseFloat(e.target.value))}
                    />
                    <span className="item-total">₹{(item.quantity * item.unit_price).toLocaleString()}</span>
                  </div>
                ))}
                <button type="button" className="btn-secondary" onClick={addItem}>
                  + Add Item
                </button>
              </div>

              <div className="bill-summary">
                <div className="summary-row">
                  <span>Subtotal:</span>
                  <span>₹{calculateTotal().toLocaleString()}</span>
                </div>
                <div className="summary-row">
                  <span>Discount:</span>
                  <input
                    type="number"
                    value={formData.discount}
                    onChange={(e) => setFormData({...formData, discount: parseFloat(e.target.value)})}
                  />
                </div>
                <div className="summary-row total">
                  <span>Total:</span>
                  <span>₹{(calculateTotal() - formData.discount).toLocaleString()}</span>
                </div>
              </div>

              <div className="modal-footer">
                <button type="button" className="btn-secondary" onClick={() => setShowModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">Generate Bill</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Payment Modal */}
      {showPaymentModal && selectedBill && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2>Record Payment</h2>
              <button className="close-btn" onClick={() => setShowPaymentModal(false)}>×</button>
            </div>
            <form onSubmit={handlePayment}>
              <div className="payment-info">
                <p>Bill: <strong>{selectedBill.bill_number}</strong></p>
                <p>Balance: <strong>₹{selectedBill.balance.toLocaleString()}</strong></p>
              </div>
              <div className="form-group">
                <label>Amount *</label>
                <input
                  type="number"
                  required
                  value={paymentAmount}
                  max={selectedBill.balance}
                  onChange={(e) => setPaymentAmount(parseFloat(e.target.value))}
                />
              </div>
              <div className="form-group">
                <label>Payment Method</label>
                <select value={paymentMethod} onChange={(e) => setPaymentMethod(e.target.value)}>
                  <option value="cash">Cash</option>
                  <option value="card">Card</option>
                  <option value="upi">UPI</option>
                  <option value="bank_transfer">Bank Transfer</option>
                  <option value="insurance">Insurance</option>
                </select>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn-secondary" onClick={() => setShowPaymentModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">Record Payment</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Billing;
