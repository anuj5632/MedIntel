import React from 'react';
import { Link } from 'react-router-dom';
import './Dashboard.css';

const Dashboard: React.FC = () => {
  const agentCards = [
    {
      title: 'Equipment & Utility Monitor',
      description: 'Real-time anomaly detection for medical equipment and utilities',
      icon: '⚙️',
      path: '/equipment',
      status: 'Active',
      metrics: { alerts: 3, uptime: '99.2%' }
    },
    {
      title: 'Staff Optimization',
      description: 'Optimize staff scheduling and resource allocation',
      icon: '👥',
      path: '/staff',
      status: 'Active',
      metrics: { efficiency: '94%', coverage: '100%' }
    },
    {
      title: 'Inventory Forecast',
      description: 'Predictive inventory management and supply chain optimization',
      icon: '📦',
      path: '/inventory',
      status: 'Active',
      metrics: { accuracy: '91%', savings: '15%' }
    },
    {
      title: 'Demand Analysis',
      description: 'Patient demand forecasting and capacity planning',
      icon: '📈',
      path: '/demand',
      status: 'Active',
      metrics: { precision: '88%', coverage: '97%' }
    },
    {
      title: 'Patient Triage',
      description: 'Emergency patient assessment and priority classification',
      icon: '🏥',
      path: '/triage',
      status: 'Active',
      metrics: { assessments: '156', accuracy: '96%' }
    }
  ];

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Medical Operations Dashboard</h1>
        <p>Comprehensive AI-powered medical facility management</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">🏥</div>
          <div className="stat-content">
            <h3>Facility Status</h3>
            <p className="stat-value">Optimal</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">👨‍⚕️</div>
          <div className="stat-content">
            <h3>Staff Utilization</h3>
            <p className="stat-value">94%</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <h3>System Efficiency</h3>
            <p className="stat-value">97%</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🚨</div>
          <div className="stat-content">
            <h3>Active Alerts</h3>
            <p className="stat-value">3</p>
          </div>
        </div>
      </div>

      <div className="agents-grid">
        {agentCards.map((agent) => (
          <Link key={agent.path} to={agent.path} className="agent-card">
            <div className="agent-header">
              <div className="agent-icon">{agent.icon}</div>
              <div className="agent-status">{agent.status}</div>
            </div>
            <h3>{agent.title}</h3>
            <p>{agent.description}</p>
            <div className="agent-metrics">
              {Object.entries(agent.metrics).map(([key, value]) => (
                <div key={key} className="metric">
                  <span className="metric-label">{key}:</span>
                  <span className="metric-value">{value}</span>
                </div>
              ))}
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
};

export default Dashboard;