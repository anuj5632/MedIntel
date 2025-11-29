import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import './Navigation.css';

const Navigation: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [expandedSection, setExpandedSection] = useState<string | null>('hospital');

  const hospitalItems = [
    { path: '/', label: 'Dashboard' },
    { path: '/patients', label: 'Patients' },
    { path: '/appointments', label: 'Appointments' },
    { path: '/billing', label: 'Billing' },
    { path: '/pharmacy', label: 'Pharmacy' },
    { path: '/lab', label: 'Laboratory' },
    { path: '/ipd', label: 'In-Patient' },
  ];

  const analyticsItems = [
    { path: '/triage', label: 'Patient Triage' },
    { path: '/community-health', label: 'Community Health' },
    { path: '/outbreak', label: 'Outbreak Prediction' },
    { path: '/staff', label: 'Staff Optimization' },
    { path: '/equipment', label: 'Equipment Monitoring' },
    { path: '/inventory', label: 'Inventory Forecast' },
    { path: '/demand', label: 'Demand Analysis' },
    { path: '/supply-chain', label: 'Supply Chain Analytics' },
  ];

  const toggleSection = (section: string) => {
    setExpandedSection(expandedSection === section ? null : section);
  };

  const handleNavClick = (path: string) => {
    navigate(path);
  };

  return (
    <nav className="navigation">
      <div className="nav-header">
        <div className="logo">MEDINTEL</div>
        <p>Hospital Management System</p>
      </div>
      
      {/* Hospital Management Section */}
      <div className="nav-section">
        <div 
          className={`nav-section-header ${expandedSection === 'hospital' ? 'expanded' : ''}`}
          onClick={() => toggleSection('hospital')}
        >
          <span>Hospital Management</span>
          <span className="expand-icon">{expandedSection === 'hospital' ? '−' : '+'}</span>
        </div>
        {expandedSection === 'hospital' && (
          <ul className="nav-menu">
            {hospitalItems.map((item) => (
              <li key={item.path} className="nav-item">
                <div 
                  onClick={() => handleNavClick(item.path)}
                  className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
                >
                  <span className="nav-label">{item.label}</span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Analyzing Tools Section */}
      <div className="nav-section">
        <div 
          className={`nav-section-header ${expandedSection === 'ai' ? 'expanded' : ''}`}
          onClick={() => toggleSection('ai')}
        >
          <span>Analyzing Tools</span>
          <span className="expand-icon">{expandedSection === 'ai' ? '−' : '+'}</span>
        </div>
        {expandedSection === 'ai' && (
          <ul className="nav-menu">
            {analyticsItems.map((item) => (
              <li key={item.path} className="nav-item">
                <div 
                  onClick={() => handleNavClick(item.path)}
                  className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
                >
                  <span className="nav-label">{item.label}</span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* User Section */}
      <div className="nav-footer">
        <div onClick={() => handleNavClick('/login')} className="nav-link login-link">
          <span className="nav-label">Sign In</span>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;