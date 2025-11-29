import React, { useState } from 'react';
import axios from 'axios';
import './StaffOptimizer.css';

interface OptimizationResult {
  optimal_schedule: any[];
  efficiency_score: number;
  coverage_percentage: number;
  recommendations: string[];
  cost_savings: number;
}

const StaffOptimizer: React.FC = () => {
  const [department, setDepartment] = useState('');
  const [shiftType, setShiftType] = useState('8-hour');
  const [staffCount, setStaffCount] = useState('');
  const [patientLoad, setPatientLoad] = useState('');
  const [specialtyRequired, setSpecialtyRequired] = useState('');
  const [result, setResult] = useState<OptimizationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const departments = [
    'Emergency', 'ICU', 'Surgery', 'Cardiology', 'Pediatrics', 
    'Oncology', 'Radiology', 'Laboratory', 'Pharmacy', 'General'
  ];

  const specialties = [
    'None', 'RN', 'LPN', 'MD', 'Specialist', 'Technician', 'Therapist'
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post('http://localhost:5000/api/staff/optimize', {
        department,
        shift_type: shiftType,
        staff_count: parseInt(staffCount),
        patient_load: parseInt(patientLoad),
        specialty_required: specialtyRequired === 'None' ? null : specialtyRequired
      });

      setResult(response.data);
    } catch (err) {
      setError('Failed to optimize staff schedule. Please check your inputs and try again.');
      console.error('Staff optimization error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getEfficiencyColor = (score: number) => {
    if (score >= 90) return '#22c55e';
    if (score >= 75) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div className="staff-optimizer">
      <div className="page-header">
        <h1>Staff Optimization</h1>
        <p>Optimize staff scheduling and resource allocation</p>
      </div>

      <div className="optimizer-content">
        <div className="input-section">
          <div className="card">
            <h2>Schedule Optimization</h2>
            <form onSubmit={handleSubmit} className="staff-form">
              <div className="form-group">
                <label htmlFor="department">Department</label>
                <select
                  id="department"
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                  required
                >
                  <option value="">Select Department</option>
                  {departments.map(dept => (
                    <option key={dept} value={dept}>{dept}</option>
                  ))}
                </select>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="shiftType">Shift Type</label>
                  <select
                    id="shiftType"
                    value={shiftType}
                    onChange={(e) => setShiftType(e.target.value)}
                    required
                  >
                    <option value="8-hour">8 Hour</option>
                    <option value="12-hour">12 Hour</option>
                    <option value="flexible">Flexible</option>
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="specialtyRequired">Specialty Required</label>
                  <select
                    id="specialtyRequired"
                    value={specialtyRequired}
                    onChange={(e) => setSpecialtyRequired(e.target.value)}
                    required
                  >
                    <option value="">Select Specialty</option>
                    {specialties.map(specialty => (
                      <option key={specialty} value={specialty}>{specialty}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="staffCount">Available Staff Count</label>
                  <input
                    id="staffCount"
                    type="number"
                    value={staffCount}
                    onChange={(e) => setStaffCount(e.target.value)}
                    placeholder="e.g., 15"
                    min="1"
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="patientLoad">Expected Patient Load</label>
                  <input
                    id="patientLoad"
                    type="number"
                    value={patientLoad}
                    onChange={(e) => setPatientLoad(e.target.value)}
                    placeholder="e.g., 45"
                    min="0"
                    required
                  />
                </div>
              </div>

              <button type="submit" disabled={loading} className="optimize-btn">
                {loading ? 'Optimizing...' : 'Optimize Schedule'}
              </button>
            </form>

            {error && (
              <div className="error-message">
                <span className="error-icon">⚠️</span>
                {error}
              </div>
            )}
          </div>
        </div>

        <div className="results-section">
          {result && (
            <div className="card">
              <h2>Optimization Results</h2>
              
              <div className="metrics-grid">
                <div className="metric-card">
                  <h4>Efficiency Score</h4>
                  <div 
                    className="metric-value"
                    style={{ color: getEfficiencyColor(result.efficiency_score) }}
                  >
                    {result.efficiency_score.toFixed(1)}%
                  </div>
                </div>
                
                <div className="metric-card">
                  <h4>Coverage</h4>
                  <div className="metric-value" style={{ color: '#22c55e' }}>
                    {result.coverage_percentage.toFixed(1)}%
                  </div>
                </div>

                <div className="metric-card">
                  <h4>Cost Savings</h4>
                  <div className="metric-value" style={{ color: '#3b82f6' }}>
                    ${result.cost_savings.toLocaleString()}
                  </div>
                </div>

                <div className="metric-card">
                  <h4>Schedule Items</h4>
                  <div className="metric-value">
                    {result.optimal_schedule.length}
                  </div>
                </div>
              </div>

              <div className="schedule-preview">
                <h4>Schedule Overview</h4>
                <div className="schedule-grid">
                  {result.optimal_schedule.slice(0, 8).map((item, index) => (
                    <div key={index} className="schedule-item">
                      <div className="schedule-time">
                        {item.start_time || `Shift ${index + 1}`}
                      </div>
                      <div className="schedule-staff">
                        {item.staff_assigned || item.staff_id || `Staff-${index + 1}`}
                      </div>
                      <div className="schedule-role">
                        {item.role || item.position || 'General'}
                      </div>
                    </div>
                  ))}
                </div>
                {result.optimal_schedule.length > 8 && (
                  <div className="schedule-more">
                    +{result.optimal_schedule.length - 8} more assignments
                  </div>
                )}
              </div>

              {result.recommendations && result.recommendations.length > 0 && (
                <div className="recommendations">
                  <h4>Optimization Recommendations</h4>
                  <ul>
                    {result.recommendations.map((rec, index) => (
                      <li key={index}>{rec}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {!result && !loading && !error && (
            <div className="card placeholder">
              <div className="placeholder-content">
                <div className="placeholder-icon">📊</div>
                <h3>Ready for Optimization</h3>
                <p>Enter department parameters to optimize staff scheduling and improve efficiency.</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default StaffOptimizer;