import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './HospitalDashboard.css';

interface DashboardStats {
  patients: {
    total: number;
    new_today: number;
    new_this_month: number;
  };
  appointments: {
    today: number;
    completed: number;
    pending: number;
  };
  ipd: {
    current_admissions: number;
    admissions_today: number;
    discharges_today: number;
  };
  revenue: {
    today: number;
    this_month: number;
    pending_bills: number;
  };
  lab: {
    pending_tests: number;
    tests_today: number;
  };
  pharmacy: {
    low_stock_alerts: number;
  };
  staff: {
    doctors: number;
    nurses: number;
    total: number;
  };
}

const HospitalDashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5000/api/reports/dashboard', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setStats(data);
      } else {
        setStats({
          patients: { total: 1250, new_today: 15, new_this_month: 180 },
          appointments: { today: 45, completed: 28, pending: 17 },
          ipd: { current_admissions: 32, admissions_today: 5, discharges_today: 3 },
          revenue: { today: 125000, this_month: 2850000, pending_bills: 42 },
          lab: { pending_tests: 18, tests_today: 65 },
          pharmacy: { low_stock_alerts: 8 },
          staff: { doctors: 25, nurses: 48, total: 120 },
        });
      }
    } catch {
      setStats({
        patients: { total: 1250, new_today: 15, new_this_month: 180 },
        appointments: { today: 45, completed: 28, pending: 17 },
        ipd: { current_admissions: 32, admissions_today: 5, discharges_today: 3 },
        revenue: { today: 125000, this_month: 2850000, pending_bills: 42 },
        lab: { pending_tests: 18, tests_today: 65 },
        pharmacy: { low_stock_alerts: 8 },
        staff: { doctors: 25, nurses: 48, total: 120 },
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading-spinner">Loading dashboard...</div>;
  }

  return (
    <div className="hospital-dashboard">
      <div className="dashboard-header">
        <div className="header-content">
          <h1>Hospital Dashboard</h1>
          <p>Real-time overview of hospital operations</p>
        </div>
        <div className="header-actions">
          <button className="action-btn primary" onClick={() => navigate('/patients')}>
            + New Patient
          </button>
          <button className="action-btn" onClick={() => navigate('/appointments')}>
            + Appointment
          </button>
        </div>
      </div>

      {/* Quick Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card patients" onClick={() => navigate('/patients')}>
          <div className="stat-icon-box">
            <svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24">
              <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/>
            </svg>
          </div>
          <div className="stat-content">
            <h3>Total Patients</h3>
            <div className="stat-value">{stats?.patients.total.toLocaleString()}</div>
            <div className="stat-detail">+{stats?.patients.new_today} today</div>
          </div>
        </div>

        <div className="stat-card appointments" onClick={() => navigate('/appointments')}>
          <div className="stat-icon-box">
            <svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24">
              <path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM9 10H7v2h2v-2zm4 0h-2v2h2v-2zm4 0h-2v2h2v-2zm-8 4H7v2h2v-2zm4 0h-2v2h2v-2zm4 0h-2v2h2v-2z"/>
            </svg>
          </div>
          <div className="stat-content">
            <h3>Today's Appointments</h3>
            <div className="stat-value">{stats?.appointments.today}</div>
            <div className="stat-detail">
              {stats?.appointments.completed} completed, {stats?.appointments.pending} pending
            </div>
          </div>
        </div>

        <div className="stat-card ipd" onClick={() => navigate('/ipd')}>
          <div className="stat-icon-box">
            <svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24">
              <path d="M7 13c1.66 0 3-1.34 3-3S8.66 7 7 7s-3 1.34-3 3 1.34 3 3 3zm12-6h-8v7H3V7H1v10h22v-6c0-2.21-1.79-4-4-4z"/>
            </svg>
          </div>
          <div className="stat-content">
            <h3>IPD Admissions</h3>
            <div className="stat-value">{stats?.ipd.current_admissions}</div>
            <div className="stat-detail">
              {stats?.ipd.admissions_today} in, {stats?.ipd.discharges_today} out today
            </div>
          </div>
        </div>

        <div className="stat-card revenue" onClick={() => navigate('/billing')}>
          <div className="stat-icon-box">
            <svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24">
              <path d="M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z"/>
            </svg>
          </div>
          <div className="stat-content">
            <h3>Today's Revenue</h3>
            <div className="stat-value">₹{stats?.revenue.today.toLocaleString()}</div>
            <div className="stat-detail">{stats?.revenue.pending_bills} pending bills</div>
          </div>
        </div>
      </div>

      {/* Module Cards */}
      <div className="modules-section">
        <h2>Hospital Modules</h2>
        <div className="modules-grid">
          <div className="module-card" onClick={() => navigate('/patients')}>
            <div className="module-icon-box">
              <svg viewBox="0 0 24 24" fill="currentColor" width="28" height="28">
                <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
              </svg>
            </div>
            <h3>Patient Management</h3>
            <p>Registration, EMR, Medical Records</p>
            <span className="module-badge">{stats?.patients.total} patients</span>
          </div>

          <div className="module-card" onClick={() => navigate('/appointments')}>
            <div className="module-icon-box">
              <svg viewBox="0 0 24 24" fill="currentColor" width="28" height="28">
                <path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM9 10H7v2h2v-2zm4 0h-2v2h2v-2zm4 0h-2v2h2v-2z"/>
              </svg>
            </div>
            <h3>Appointments</h3>
            <p>Scheduling & Queue Management</p>
            <span className="module-badge">{stats?.appointments.today} today</span>
          </div>

          <div className="module-card" onClick={() => navigate('/billing')}>
            <div className="module-icon-box">
              <svg viewBox="0 0 24 24" fill="currentColor" width="28" height="28">
                <path d="M20 4H4c-1.11 0-1.99.89-1.99 2L2 18c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V6c0-1.11-.89-2-2-2zm0 14H4v-6h16v6zm0-10H4V6h16v2z"/>
              </svg>
            </div>
            <h3>Billing</h3>
            <p>OPD/IPD Billing & Payments</p>
            <span className="module-badge">{stats?.revenue.pending_bills} pending</span>
          </div>

          <div className="module-card" onClick={() => navigate('/pharmacy')}>
            <div className="module-icon-box">
              <svg viewBox="0 0 24 24" fill="currentColor" width="28" height="28">
                <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 14h-2v-4H6v-2h4V7h2v4h4v2h-4v4z"/>
              </svg>
            </div>
            <h3>Pharmacy</h3>
            <p>Medicine Inventory & Dispensing</p>
            <span className="module-badge warning">{stats?.pharmacy.low_stock_alerts} alerts</span>
          </div>

          <div className="module-card" onClick={() => navigate('/lab')}>
            <div className="module-icon-box">
              <svg viewBox="0 0 24 24" fill="currentColor" width="28" height="28">
                <path d="M7 2v2h1v14c0 2.21 1.79 4 4 4s4-1.79 4-4V4h1V2H7zm6 16c0 1.1-.9 2-2 2s-2-.9-2-2V4h4v14z"/>
              </svg>
            </div>
            <h3>Laboratory</h3>
            <p>Test Orders & Results</p>
            <span className="module-badge">{stats?.lab.pending_tests} pending</span>
          </div>

          <div className="module-card" onClick={() => navigate('/ipd')}>
            <div className="module-icon-box">
              <svg viewBox="0 0 24 24" fill="currentColor" width="28" height="28">
                <path d="M7 13c1.66 0 3-1.34 3-3S8.66 7 7 7s-3 1.34-3 3 1.34 3 3 3zm12-6h-8v7H3V7H1v10h22v-6c0-2.21-1.79-4-4-4z"/>
              </svg>
            </div>
            <h3>In-Patient (IPD)</h3>
            <p>Admissions & Bed Management</p>
            <span className="module-badge">{stats?.ipd.current_admissions} admitted</span>
          </div>

          <div className="module-card" onClick={() => navigate('/inventory')}>
            <div className="module-icon-box">
              <svg viewBox="0 0 24 24" fill="currentColor" width="28" height="28">
                <path d="M20 2H4c-1 0-2 .9-2 2v3.01c0 .72.43 1.34 1 1.69V20c0 1.1 1.1 2 2 2h14c.9 0 2-.9 2-2V8.7c.57-.35 1-.97 1-1.69V4c0-1.1-1-2-2-2zm-5 12H9v-2h6v2zm5-7H4V4h16v3z"/>
              </svg>
            </div>
            <h3>Inventory</h3>
            <p>Stock & Equipment Management</p>
            <span className="module-badge">Active</span>
          </div>

          <div className="module-card" onClick={() => navigate('/demand')}>
            <div className="module-icon-box">
              <svg viewBox="0 0 24 24" fill="currentColor" width="28" height="28">
                <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/>
              </svg>
            </div>
            <h3>Reports & Analytics</h3>
            <p>Insights & Predictions</p>
            <span className="module-badge analytics">Analytics</span>
          </div>
        </div>
      </div>

      {/* Analyzing Tools Section */}
      <div className="analytics-section">
        <h2>Analyzing Tools</h2>
        <div className="analytics-grid">
          <div className="analytics-card" onClick={() => navigate('/triage')}>
            <span className="status-indicator active"></span>
            <h4>Triage Analysis</h4>
            <p>Patient priority assessment</p>
          </div>
          <div className="analytics-card" onClick={() => navigate('/community-health')}>
            <span className="status-indicator active"></span>
            <h4>Community Health</h4>
            <p>Public health advisories</p>
          </div>
          <div className="analytics-card" onClick={() => navigate('/outbreak')}>
            <span className="status-indicator active"></span>
            <h4>Outbreak Prediction</h4>
            <p>Disease outbreak alerts</p>
          </div>
          <div className="analytics-card" onClick={() => navigate('/staff')}>
            <span className="status-indicator active"></span>
            <h4>Staff Optimization</h4>
            <p>Smart scheduling</p>
          </div>
          <div className="analytics-card" onClick={() => navigate('/demand')}>
            <span className="status-indicator active"></span>
            <h4>Demand Forecasting</h4>
            <p>Resource prediction</p>
          </div>
          <div className="analytics-card" onClick={() => navigate('/inventory')}>
            <span className="status-indicator active"></span>
            <h4>Inventory Analysis</h4>
            <p>Stock optimization</p>
          </div>
          <div className="analytics-card" onClick={() => navigate('/equipment')}>
            <span className="status-indicator active"></span>
            <h4>Equipment Monitoring</h4>
            <p>Maintenance prediction</p>
          </div>
          <div className="analytics-card" onClick={() => navigate('/supply-chain')}>
            <span className="status-indicator active"></span>
            <h4>Supply Chain</h4>
            <p>Vendor resilience</p>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <h2>Quick Actions</h2>
        <div className="actions-grid">
          <button className="quick-action-btn" onClick={() => navigate('/patients')}>
            Register Patient
          </button>
          <button className="quick-action-btn" onClick={() => navigate('/appointments')}>
            Book Appointment
          </button>
          <button className="quick-action-btn" onClick={() => navigate('/lab')}>
            Order Lab Test
          </button>
          <button className="quick-action-btn" onClick={() => navigate('/pharmacy')}>
            Prescribe Medicine
          </button>
          <button className="quick-action-btn" onClick={() => navigate('/ipd')}>
            Admit Patient
          </button>
          <button className="quick-action-btn" onClick={() => navigate('/billing')}>
            Generate Bill
          </button>
        </div>
      </div>
    </div>
  );
};

export default HospitalDashboard;
