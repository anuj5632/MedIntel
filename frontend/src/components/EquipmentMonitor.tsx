import React, { useState } from 'react';
import axios from 'axios';
import './EquipmentMonitor.css';

interface AnomalyResult {
  equipment_id: string;
  anomaly_score: number;
  is_anomaly: boolean;
  calibrated_score: number;
  recommendations: string[];
}

const EquipmentMonitor: React.FC = () => {
  const [equipmentId, setEquipmentId] = useState('');
  const [temperature, setTemperature] = useState('');
  const [pressure, setPressure] = useState('');
  const [vibration, setVibration] = useState('');
  const [powerConsumption, setPowerConsumption] = useState('');
  const [result, setResult] = useState<AnomalyResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post('http://localhost:5000/api/equipment/predict', {
        equipment_id: equipmentId,
        temperature: parseFloat(temperature),
        pressure: parseFloat(pressure),
        vibration: parseFloat(vibration),
        power_consumption: parseFloat(powerConsumption)
      });

      setResult(response.data);
    } catch (err) {
      setError('Failed to analyze equipment. Please check your inputs and try again.');
      console.error('Equipment analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.7) return '#ef4444'; // Red for high anomaly
    if (score >= 0.5) return '#f59e0b'; // Orange for medium anomaly
    return '#22c55e'; // Green for normal
  };

  const getScoreLabel = (score: number) => {
    if (score >= 0.7) return 'High Risk';
    if (score >= 0.5) return 'Medium Risk';
    return 'Normal';
  };

  return (
    <div className="equipment-monitor">
      <div className="page-header">
        <h1>Equipment & Utility Monitor</h1>
        <p>Real-time anomaly detection for medical equipment</p>
      </div>

      <div className="monitor-content">
        <div className="input-section">
          <div className="card">
            <h2>Equipment Analysis</h2>
            <form onSubmit={handleSubmit} className="equipment-form">
              <div className="form-group">
                <label htmlFor="equipmentId">Equipment ID</label>
                <input
                  id="equipmentId"
                  type="text"
                  value={equipmentId}
                  onChange={(e) => setEquipmentId(e.target.value)}
                  placeholder="e.g., MRI-001, VENT-005"
                  required
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="temperature">Temperature (°C)</label>
                  <input
                    id="temperature"
                    type="number"
                    step="0.1"
                    value={temperature}
                    onChange={(e) => setTemperature(e.target.value)}
                    placeholder="e.g., 23.5"
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="pressure">Pressure (bar)</label>
                  <input
                    id="pressure"
                    type="number"
                    step="0.1"
                    value={pressure}
                    onChange={(e) => setPressure(e.target.value)}
                    placeholder="e.g., 1.2"
                    required
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="vibration">Vibration (Hz)</label>
                  <input
                    id="vibration"
                    type="number"
                    step="0.01"
                    value={vibration}
                    onChange={(e) => setVibration(e.target.value)}
                    placeholder="e.g., 0.05"
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="powerConsumption">Power Consumption (kW)</label>
                  <input
                    id="powerConsumption"
                    type="number"
                    step="0.1"
                    value={powerConsumption}
                    onChange={(e) => setPowerConsumption(e.target.value)}
                    placeholder="e.g., 15.3"
                    required
                  />
                </div>
              </div>

              <button type="submit" disabled={loading} className="analyze-btn">
                {loading ? 'Analyzing...' : 'Analyze Equipment'}
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
              <h2>Analysis Results</h2>
              
              <div className="result-header">
                <h3>Equipment: {result.equipment_id}</h3>
                <div className={`status-badge ${result.is_anomaly ? 'anomaly' : 'normal'}`}>
                  {result.is_anomaly ? 'Anomaly Detected' : 'Normal Operation'}
                </div>
              </div>

              <div className="scores-container">
                <div className="score-card">
                  <h4>Raw Anomaly Score</h4>
                  <div className="score-value">{result.anomaly_score.toFixed(3)}</div>
                </div>
                
                <div className="score-card">
                  <h4>Calibrated Risk Score</h4>
                  <div 
                    className="score-value"
                    style={{ color: getScoreColor(result.calibrated_score) }}
                  >
                    {(result.calibrated_score * 100).toFixed(1)}%
                  </div>
                  <div className="score-label" style={{ color: getScoreColor(result.calibrated_score) }}>
                    {getScoreLabel(result.calibrated_score)}
                  </div>
                </div>
              </div>

              {result.recommendations && result.recommendations.length > 0 && (
                <div className="recommendations">
                  <h4>Recommendations</h4>
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
                <div className="placeholder-icon">🔍</div>
                <h3>Ready for Analysis</h3>
                <p>Enter equipment parameters to detect potential anomalies and maintenance needs.</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default EquipmentMonitor;