import React, { useState } from 'react';
import axios from 'axios';
import './TriageAgent.css';

interface TriageResult {
  patient_id: string;
  priority_level: string;
  urgency_score: number;
  symptoms: string[];
  vitals: {
    heart_rate: number;
    blood_pressure: string;
    temperature: number;
    respiratory_rate: number;
  };
  risk_assessment: string;
  recommended_department: string;
  recommendations: string[];
}

const TriageAgent: React.FC = () => {
  const [patientId, setPatientId] = useState('');
  const [symptoms, setSymptoms] = useState('');
  const [heartRate, setHeartRate] = useState('');
  const [bloodPressure, setBloodPressure] = useState('');
  const [temperature, setTemperature] = useState('');
  const [respiratoryRate, setRespiratoryRate] = useState('');
  const [result, setResult] = useState<TriageResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const commonSymptoms = [
    'Chest Pain', 'Shortness of Breath', 'Severe Headache', 'Dizziness',
    'Abdominal Pain', 'Fever', 'Injury', 'Bleeding', 'Nausea', 'Fatigue'
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post('http://localhost:5000/api/triage/assess', {
        patient_id: patientId || `PAT-${Date.now()}`,
        symptoms: symptoms.split(',').map(s => s.trim()).filter(s => s),
        vitals: {
          heart_rate: parseInt(heartRate) || 75,
          blood_pressure: bloodPressure || '120/80',
          temperature: parseFloat(temperature) || 98.6,
          respiratory_rate: parseInt(respiratoryRate) || 16
        }
      });

      setResult(response.data);
    } catch (err) {
      setError('Failed to perform triage assessment. Please check your inputs and try again.');
      console.error('Triage assessment error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch(priority?.toLowerCase()) {
      case 'critical': return '#e53e3e';
      case 'high': return '#ed8936';
      case 'moderate': return '#f6ad55';
      case 'low': return '#4299e1';
      default: return '#0f4c75';
    }
  };

  return (
    <div className="triage-agent">
      <div className="page-header">
        <h1>Patient Triage</h1>
        <p>Emergency patient assessment and priority classification</p>
      </div>

      <div className="triage-content">
        <div className="input-section">
          <div className="card">
            <h2>Triage Assessment</h2>
            <form onSubmit={handleSubmit} className="triage-form">
              <div className="form-group">
                <label htmlFor="patient-id">Patient ID (Optional)</label>
                <input
                  id="patient-id"
                  type="text"
                  value={patientId}
                  onChange={(e) => setPatientId(e.target.value)}
                  placeholder="Enter patient ID or auto-generate"
                />
              </div>

              <div className="form-group">
                <label htmlFor="symptoms">Reported Symptoms (comma-separated)</label>
                <textarea
                  id="symptoms"
                  value={symptoms}
                  onChange={(e) => setSymptoms(e.target.value)}
                  placeholder="e.g., Chest pain, Shortness of breath, Dizziness"
                  rows={3}
                />
                <div className="quick-select">
                  {commonSymptoms.map(symptom => (
                    <button
                      key={symptom}
                      type="button"
                      className="symptom-tag"
                      onClick={() => setSymptoms(s => s ? `${s}, ${symptom}` : symptom)}
                    >
                      {symptom}
                    </button>
                  ))}
                </div>
              </div>

              <div className="vitals-section">
                <h3>Vital Signs</h3>
                
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="heart-rate">Heart Rate (bpm)</label>
                    <input
                      id="heart-rate"
                      type="number"
                      value={heartRate}
                      onChange={(e) => setHeartRate(e.target.value)}
                      placeholder="60-100"
                      min="0"
                      max="200"
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="blood-pressure">Blood Pressure (mmHg)</label>
                    <input
                      id="blood-pressure"
                      type="text"
                      value={bloodPressure}
                      onChange={(e) => setBloodPressure(e.target.value)}
                      placeholder="120/80"
                    />
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="temperature">Temperature (°F)</label>
                    <input
                      id="temperature"
                      type="number"
                      value={temperature}
                      onChange={(e) => setTemperature(e.target.value)}
                      placeholder="98.6"
                      min="90"
                      max="110"
                      step="0.1"
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="respiratory-rate">Respiratory Rate (breaths/min)</label>
                    <input
                      id="respiratory-rate"
                      type="number"
                      value={respiratoryRate}
                      onChange={(e) => setRespiratoryRate(e.target.value)}
                      placeholder="12-20"
                      min="0"
                      max="50"
                    />
                  </div>
                </div>
              </div>

              <button 
                type="submit" 
                className="assess-btn" 
                disabled={loading}
              >
                {loading ? 'Assessing...' : 'PERFORM TRIAGE'}
              </button>
            </form>
          </div>
        </div>

        <div className="results-section">
          {error && (
            <div className="error-message">
              <p>{error}</p>
            </div>
          )}

          {!result && !error && (
            <div className="card placeholder">
              <div className="placeholder-content">
                <div className="placeholder-icon">🏥</div>
                <h3>Ready for Assessment</h3>
                <p>Enter patient information and vital signs to perform triage assessment and receive priority classification and department recommendations.</p>
              </div>
            </div>
          )}

          {result && (
            <div className="card results-card">
              <div className="priority-badge" style={{ borderColor: getPriorityColor(result.priority_level) }}>
                <div className="priority-label">Priority Level</div>
                <div className="priority-value" style={{ color: getPriorityColor(result.priority_level) }}>
                  {result.priority_level.toUpperCase()}
                </div>
                <div className="urgency-score">Urgency: {Math.round(result.urgency_score * 100)}%</div>
              </div>

              <div className="vitals-display">
                <h3>Vital Signs Recorded</h3>
                <div className="vitals-grid">
                  <div className="vital-item">
                    <span className="vital-label">Heart Rate</span>
                    <span className="vital-value">{result.vitals.heart_rate} bpm</span>
                  </div>
                  <div className="vital-item">
                    <span className="vital-label">Blood Pressure</span>
                    <span className="vital-value">{result.vitals.blood_pressure}</span>
                  </div>
                  <div className="vital-item">
                    <span className="vital-label">Temperature</span>
                    <span className="vital-value">{result.vitals.temperature}°F</span>
                  </div>
                  <div className="vital-item">
                    <span className="vital-label">Respiratory Rate</span>
                    <span className="vital-value">{result.vitals.respiratory_rate} br/m</span>
                  </div>
                </div>
              </div>

              <div className="assessment-section">
                <h3>Risk Assessment</h3>
                <p className="risk-text">{result.risk_assessment}</p>
              </div>

              <div className="department-section">
                <h3>Recommended Department</h3>
                <div className="department-badge">{result.recommended_department}</div>
              </div>

              <div className="recommendations-section">
                <h3>Clinical Recommendations</h3>
                <ul className="recommendations-list">
                  {result.recommendations.map((rec, idx) => (
                    <li key={idx}>
                      <span className="rec-icon">✓</span>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TriageAgent;
