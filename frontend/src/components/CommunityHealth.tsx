import React, { useState } from 'react';
import axios from 'axios';
import './CommunityHealth.css';

interface CommunityHealthResult {
  severity: string;
  reasons: string[];
  recommended_channels: string[];
  messages: { [key: string]: string };
  location: string;
  timestamp: string;
  _field_names?: {
    severity: string;
    risk_factors: string;
    recommended_channels: string;
    public_health_messages: string;
  };
}

const CommunityHealth: React.FC = () => {
  const [locationName, setLocationName] = useState('');
  const [languages, setLanguages] = useState('en');
  const [pollutionAqi, setPollutionAqi] = useState('');
  const [respCaseTrend, setRespCaseTrend] = useState('stable');
  const [outbreakRisk, setOutbreakRisk] = useState('');
  const [outbreakType, setOutbreakType] = useState('');
  const [heatIndex, setHeatIndex] = useState('');
  const [floodRisk, setFloodRisk] = useState('');
  const [notes, setNotes] = useState('');
  const [result, setResult] = useState<CommunityHealthResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Validate required fields
      if (!locationName.trim()) {
        throw new Error('Location name is required');
      }

      // Parse numeric fields
      const context: any = {
        location_name: locationName,
        languages: languages.split(',').map((l: string) => l.trim()).filter((l: string) => l),
        resp_case_trend: respCaseTrend,
      };

      // Add optional numeric fields if provided
      if (pollutionAqi) {
        context.pollution_aqi = parseInt(pollutionAqi);
      }
      if (outbreakRisk) {
        context.outbreak_risk = parseFloat(outbreakRisk);
      }
      if (outbreakType) {
        context.outbreak_type = outbreakType;
      }
      if (heatIndex) {
        context.heat_index = parseFloat(heatIndex);
      }
      if (floodRisk) {
        context.flood_risk = parseFloat(floodRisk);
      }
      if (notes) {
        context.notes = notes;
      }

      const response = await axios.post('http://localhost:5000/api/community-health/assess', context);
      setResult(response.data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Failed to generate health advisory. Please check your inputs and try again.'
      );
      console.error('Community health assessment error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    const colors: { [key: string]: string } = {
      'INFO': '#3282b8',
      'ADVISORY': '#ffc107',
      'ALERT': '#fd7e14',
      'EMERGENCY': '#dc3545'
    };
    return colors[severity] || '#3282b8';
  };

  const getSeverityTextColor = (severity: string) => {
    return severity === 'INFO' ? '#ffffff' : '#ffffff';
  };

  const getSeverityIcon = (severity: string) => {
    const icons: { [key: string]: string } = {
      'INFO': 'ℹ️',
      'ADVISORY': '⚠️',
      'ALERT': '🚨',
      'EMERGENCY': '🚨🚨'
    };
    return icons[severity] || 'ℹ️';
  };

  const loadSampleData = () => {
    setLocationName('Nagpur');
    setPollutionAqi('210');
    setRespCaseTrend('rising');
    setOutbreakRisk('0.65');
    setOutbreakType('dengue');
    setHeatIndex('41');
    setFloodRisk('0.2');
    setNotes('School exams ongoing, avoid panic messaging');
  };

  return (
    <div className="community-health">
      <div className="page-header">
        <h1>Community Health Advisory</h1>
        <p>Generate public health advisories based on community health indicators</p>
      </div>

      <div className="health-content">
        <div className="input-section">
          <div className="card">
            <h2>🏥 Community Health Assessment</h2>

            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Location Name *</label>
                <input
                  type="text"
                  value={locationName}
                  onChange={(e) => setLocationName(e.target.value)}
                  placeholder="Enter community/city name"
                  required
                />
              </div>

              <div className="form-group">
                <label>Languages (comma-separated)</label>
                <input
                  type="text"
                  value={languages}
                  onChange={(e) => setLanguages(e.target.value)}
                  placeholder="en, hi, es"
                />
                <small>Use language codes: en (English), hi (Hindi), es (Spanish), etc.</small>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Air Quality Index (AQI)</label>
                  <input
                    type="number"
                    value={pollutionAqi}
                    onChange={(e) => setPollutionAqi(e.target.value)}
                    min="0"
                    placeholder="e.g., 210"
                  />
                  <small>0-50 (Good), 51-100 (Moderate), 150+ (Poor)</small>
                </div>

                <div className="form-group">
                  <label>Respiratory Case Trend</label>
                  <select value={respCaseTrend} onChange={(e) => setRespCaseTrend(e.target.value)}>
                    <option value="stable">Stable</option>
                    <option value="rising">Rising</option>
                    <option value="falling">Falling</option>
                  </select>
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Outbreak Risk (0.0-1.0)</label>
                  <input
                    type="number"
                    value={outbreakRisk}
                    onChange={(e) => setOutbreakRisk(e.target.value)}
                    min="0"
                    max="1"
                    step="0.01"
                    placeholder="e.g., 0.65"
                  />
                  <small>Risk score from 0 (no risk) to 1 (maximum risk)</small>
                </div>

                <div className="form-group">
                  <label>Outbreak Type</label>
                  <input
                    type="text"
                    value={outbreakType}
                    onChange={(e) => setOutbreakType(e.target.value)}
                    placeholder="e.g., dengue, cholera"
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Heat Index (°C)</label>
                  <input
                    type="number"
                    value={heatIndex}
                    onChange={(e) => setHeatIndex(e.target.value)}
                    min="0"
                    placeholder="e.g., 41"
                    step="0.1"
                  />
                  <small>38+ (Advisory), 42+ (Alert), 45+ (Emergency)</small>
                </div>

                <div className="form-group">
                  <label>Flood Risk (0.0-1.0)</label>
                  <input
                    type="number"
                    value={floodRisk}
                    onChange={(e) => setFloodRisk(e.target.value)}
                    min="0"
                    max="1"
                    step="0.01"
                    placeholder="e.g., 0.2"
                  />
                  <small>0.3+ (Advisory), 0.6+ (Alert), 0.85+ (Emergency)</small>
                </div>
              </div>

              <div className="form-group">
                <label>Additional Notes</label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Any additional context for the advisory..."
                  rows={3}
                />
              </div>

              {error && <div className="error-box">{error}</div>}

              <div className="button-group">
                <button type="submit" className="submit-btn" disabled={loading}>
                  {loading ? '🔄 Generating...' : '🚀 Generate Advisory'}
                </button>
                <button type="button" className="helper-btn" onClick={loadSampleData}>
                  📋 Load Sample Data
                </button>
              </div>
            </form>
          </div>
        </div>

        <div className="results-section">
          {!result && (
            <div className="card placeholder">
              <div className="placeholder-content">
                <div className="placeholder-icon">🏛️</div>
                <h3>Ready for Assessment</h3>
                <p>Enter community health indicators to generate multilingual public health advisories and recommendations.</p>
              </div>
            </div>
          )}
          {result && (
            <div>
              <div className="severity-card" style={{ backgroundColor: getSeverityColor(result.severity) }}>
                <div className="severity-header">
                  <h3 style={{ color: getSeverityTextColor(result.severity) }}>
                    {getSeverityIcon(result.severity)} {result.severity}
                  </h3>
                </div>
                <div className="location-info" style={{ color: getSeverityTextColor(result.severity) }}>
                  {result.location}
                </div>
              </div>

            <div className="reasons-section">
              <h3>📋 {result._field_names?.risk_factors || 'Risk Factors'}</h3>
              <div className="reasons-list">
                {result.reasons.map((reason, idx) => (
                  <div key={idx} className="reason-item">
                    <span className="reason-bullet">•</span>
                    <span>{reason}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="channels-section">
              <h3>📡 {result._field_names?.recommended_channels || 'Recommended Communication Channels'}</h3>
              <div className="channels-grid">
                {result.recommended_channels.map((channel, idx) => (
                  <div key={idx} className="channel-badge">
                    {channel}
                  </div>
                ))}
              </div>
            </div>

            <div className="messages-section">
              <h3>💬 {result._field_names?.public_health_messages || 'Public Health Messages'}</h3>
              <div className="messages-container">
                {Object.entries(result.messages).map(([lang, message]) => (
                  <div key={lang} className="message-box">
                    <div className="message-lang">
                      {lang.toUpperCase()}
                    </div>
                    <div className="message-text">
                      {message}
                    </div>
                  </div>
                ))}
              </div>
            </div>

              <div className="info-card">
                <h4>⏰ Assessment Timestamp</h4>
                <p>{new Date(result.timestamp).toLocaleString()}</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CommunityHealth;
