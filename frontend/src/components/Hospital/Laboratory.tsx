import React, { useState, useEffect } from 'react';
import './Hospital.css';

interface LabTest {
  id: number;
  test_code: string;
  name: string;
  category: string;
  price: number;
  turnaround_time: string;
  is_active: boolean;
}

interface LabOrder {
  id: number;
  order_id: string;
  patient_name: string;
  doctor_name: string;
  test_name: string;
  status: string;
  priority: string;
  ordered_at: string;
  completed_at: string;
  result: string;
}

const Laboratory: React.FC = () => {
  const [activeTab, setActiveTab] = useState('orders');
  const [orders, setOrders] = useState<LabOrder[]>([]);
  const [tests, setTests] = useState<LabTest[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [showResultModal, setShowResultModal] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState<LabOrder | null>(null);
  const [filter, setFilter] = useState('pending');
  const [resultData, setResultData] = useState('');

  const API_URL = 'http://localhost:5000/api';

  useEffect(() => {
    if (activeTab === 'orders') {
      fetchOrders();
    } else {
      fetchTests();
    }
  }, [activeTab, filter]);

  const getToken = () => localStorage.getItem('token');

  const fetchOrders = async () => {
    try {
      const response = await fetch(`${API_URL}/lab/orders?status=${filter}`, {
        headers: { 'Authorization': `Bearer ${getToken()}` },
      });
      if (response.ok) {
        const data = await response.json();
        setOrders(data.orders || []);
      }
    } catch (err) {
      console.error('Error fetching orders:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchTests = async () => {
    try {
      const response = await fetch(`${API_URL}/lab/tests`, {
        headers: { 'Authorization': `Bearer ${getToken()}` },
      });
      if (response.ok) {
        const data = await response.json();
        setTests(data.tests || []);
      }
    } catch (err) {
      console.error('Error fetching tests:', err);
    } finally {
      setLoading(false);
    }
  };

  const updateOrderStatus = async (id: number, status: string) => {
    try {
      await fetch(`${API_URL}/lab/orders/${id}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getToken()}`,
        },
        body: JSON.stringify({ status }),
      });
      fetchOrders();
    } catch (err) {
      console.error('Error updating order:', err);
    }
  };

  const submitResult = async () => {
    if (!selectedOrder) return;
    try {
      await fetch(`${API_URL}/lab/orders/${selectedOrder.id}/result`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getToken()}`,
        },
        body: JSON.stringify({ result: resultData }),
      });
      setShowResultModal(false);
      setSelectedOrder(null);
      setResultData('');
      fetchOrders();
    } catch (err) {
      console.error('Error submitting result:', err);
    }
  };

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'orange',
      'sample-collected': 'blue',
      'in-progress': 'purple',
      completed: 'green',
      cancelled: 'red',
    };
    return <span className={`status-badge ${colors[status] || 'gray'}`}>{status}</span>;
  };

  const getPriorityBadge = (priority: string) => {
    const colors: Record<string, string> = {
      normal: 'gray',
      urgent: 'orange',
      critical: 'red',
    };
    return <span className={`priority-badge ${colors[priority] || 'gray'}`}>{priority}</span>;
  };

  if (loading) return <div className="loading">Loading laboratory...</div>;

  return (
    <div className="hospital-module">
      <div className="module-header">
        <div>
          <h1>🔬 Laboratory</h1>
          <p>Manage lab tests and results</p>
        </div>
        <button className="btn-primary" onClick={() => setShowModal(true)}>
          + New Test Order
        </button>
      </div>

      <div className="tab-navigation">
        <button
          className={activeTab === 'orders' ? 'active' : ''}
          onClick={() => setActiveTab('orders')}
        >
          Test Orders
        </button>
        <button
          className={activeTab === 'tests' ? 'active' : ''}
          onClick={() => setActiveTab('tests')}
        >
          Available Tests
        </button>
      </div>

      {activeTab === 'orders' && (
        <>
          <div className="filter-tabs">
            {['pending', 'sample-collected', 'in-progress', 'completed'].map((f) => (
              <button
                key={f}
                className={filter === f ? 'active' : ''}
                onClick={() => setFilter(f)}
              >
                {f.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </button>
            ))}
          </div>

          <div className="orders-grid">
            {orders.length === 0 ? (
              <div className="no-data-card">
                <span>🔬</span>
                <p>No {filter} orders found</p>
              </div>
            ) : (
              orders.map((order) => (
                <div key={order.id} className="lab-order-card">
                  <div className="order-header">
                    <span className="order-id">{order.order_id}</span>
                    <div className="order-badges">
                      {getPriorityBadge(order.priority)}
                      {getStatusBadge(order.status)}
                    </div>
                  </div>
                  <div className="order-body">
                    <h4>{order.test_name}</h4>
                    <p className="patient">Patient: {order.patient_name}</p>
                    <p className="doctor">Ordered by: Dr. {order.doctor_name}</p>
                    <p className="date">{new Date(order.ordered_at).toLocaleString()}</p>
                  </div>
                  <div className="order-actions">
                    {order.status === 'pending' && (
                      <button onClick={() => updateOrderStatus(order.id, 'sample-collected')}>
                        Collect Sample
                      </button>
                    )}
                    {order.status === 'sample-collected' && (
                      <button onClick={() => updateOrderStatus(order.id, 'in-progress')}>
                        Start Processing
                      </button>
                    )}
                    {order.status === 'in-progress' && (
                      <button onClick={() => {
                        setSelectedOrder(order);
                        setShowResultModal(true);
                      }}>
                        Enter Result
                      </button>
                    )}
                    {order.status === 'completed' && order.result && (
                      <button className="view">View Result</button>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </>
      )}

      {activeTab === 'tests' && (
        <div className="data-table">
          <table>
            <thead>
              <tr>
                <th>Code</th>
                <th>Test Name</th>
                <th>Category</th>
                <th>Price</th>
                <th>TAT</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {tests.length === 0 ? (
                <tr><td colSpan={6} className="no-data">No tests configured</td></tr>
              ) : (
                tests.map((test) => (
                  <tr key={test.id}>
                    <td>{test.test_code}</td>
                    <td>{test.name}</td>
                    <td>{test.category}</td>
                    <td>₹{test.price}</td>
                    <td>{test.turnaround_time}</td>
                    <td>
                      <span className={`status ${test.is_active ? 'active' : 'inactive'}`}>
                        {test.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Result Entry Modal */}
      {showResultModal && selectedOrder && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2>Enter Test Result</h2>
              <button className="close-btn" onClick={() => setShowResultModal(false)}>×</button>
            </div>
            <div className="result-info">
              <p><strong>Order:</strong> {selectedOrder.order_id}</p>
              <p><strong>Test:</strong> {selectedOrder.test_name}</p>
              <p><strong>Patient:</strong> {selectedOrder.patient_name}</p>
            </div>
            <div className="form-group">
              <label>Test Result *</label>
              <textarea
                rows={6}
                value={resultData}
                onChange={(e) => setResultData(e.target.value)}
                placeholder="Enter test results, observations, and findings..."
              />
            </div>
            <div className="modal-footer">
              <button className="btn-secondary" onClick={() => setShowResultModal(false)}>
                Cancel
              </button>
              <button className="btn-primary" onClick={submitResult}>
                Submit Result
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Laboratory;
