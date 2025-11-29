import React, { useState } from 'react';
import axios from 'axios';
import './PredictiveOutbreak.css';

interface OutbreakResult {
  risk_index: number;
  risk_level: string;
  cluster_label: number;
  reason: string;
  latest_metrics: {
    date: string;
    cases: number;
    aqi?: number;
    growth_7d?: number;
    residual_zscore: number;
    recent_peak: boolean;
  };
  time_series: {
    dates: string[];
    cases: number[];
    baseline: number[];
    residuals: number[];
    peaks_idx: number[];
  };
}

const PredictiveOutbreak: React.FC = () => {
  const [casesData, setCasesData] = useState<string>('');
  const [aqiData, setAqiData] = useState<string>('');
  const [forecastHorizon, setForecastHorizon] = useState('7');
  const [windowDays, setWindowDays] = useState('7');
  const [nClusters, setNClusters] = useState('3');
  const [result, setResult] = useState<OutbreakResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dataFormat, setDataFormat] = useState<'csv' | 'manual'>('manual');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Parse input data
      let cases_data = [];

      if (dataFormat === 'manual') {
        // Manual entry format: one date-case pair per line (date,cases)
        const lines = casesData.trim().split('\n').filter(line => line.trim());
        cases_data = lines.map((line, idx) => {
          const parts = line.split(',').map(p => p.trim());
          if (parts.length < 2) {
            throw new Error(`Invalid format on line ${idx + 1}. Expected: date,cases`);
          }
          const date = parts[0];
          const cases = parseInt(parts[1]);
          const aqi = aqiData ? parseInt(aqiData.split('\n')[idx]?.split(',')[1] || '0') : undefined;
          return { date, cases, ...(aqi !== undefined && { aqi }) };
        });
      } else {
        // CSV format: paste full CSV content
        const lines = casesData.trim().split('\n');
        if (lines.length < 2) {
          throw new Error('CSV must have at least a header and one data row');
        }
        const headers = lines[0].split(',').map(h => h.trim().toLowerCase());
        const dateIdx = headers.indexOf('date');
        const casesIdx = headers.indexOf('cases');
        const aqiIdx = headers.indexOf('aqi');

        if (dateIdx === -1 || casesIdx === -1) {
          throw new Error('CSV must contain "date" and "cases" columns');
        }

        cases_data = lines.slice(1).map(line => {
          const parts = line.split(',').map(p => p.trim());
          const entry: any = {
            date: parts[dateIdx],
            cases: parseInt(parts[casesIdx])
          };
          if (aqiIdx !== -1) {
            entry.aqi = parseFloat(parts[aqiIdx]);
          }
          return entry;
        });
      }

      if (cases_data.length < 14) {
        throw new Error('Need at least 14 days of data for outbreak analysis');
      }

      const response = await axios.post('http://localhost:5000/api/outbreak/assess', {
        cases_data,
        forecast_horizon: parseInt(forecastHorizon),
        window_days: parseInt(windowDays),
        n_clusters: parseInt(nClusters)
      });

      setResult(response.data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Failed to assess outbreak risk. Please check your data and try again.'
      );
      console.error('Outbreak assessment error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (index: number) => {
    const colors = ['#22863a', '#28a745', '#ffc107', '#fd7e14', '#dc3545', '#721c24'];
    return colors[Math.min(index, 5)];
  };

  const getRiskTextColor = (index: number) => {
    return index >= 3 ? '#ffffff' : '#000000';
  };

  const loadSampleData = () => {
    const sampleData = `2025-08-01,45
2025-08-02,48
2025-08-03,52
2025-08-04,49
2025-08-05,51
2025-08-06,55
2025-08-07,58
2025-08-08,62
2025-08-09,59
2025-08-10,64
2025-08-11,67
2025-08-12,71
2025-08-13,76
2025-08-14,82
2025-08-15,88
2025-08-16,95
2025-08-17,103
2025-08-18,112
2025-08-19,121
2025-08-20,132`;
    setCasesData(sampleData);
  };

  return (
    <div className="predictive-outbreak">
      <div className="page-header">
        <h1>Outbreak Risk Prediction</h1>
        <p>Advanced disease outbreak detection and forecasting using ML</p>
      </div>

      <div className="outbreak-content">
        <div className="input-section">
          <div className="card">
            <h2>📊 Disease Case Analysis</h2>
            
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Data Format</label>
                <div className="format-toggle">
                  <button
                    type="button"
                    className={`toggle-btn ${dataFormat === 'manual' ? 'active' : ''}`}
                    onClick={() => setDataFormat('manual')}
                  >
                    Manual Entry
                  </button>
                  <button
                    type="button"
                    className={`toggle-btn ${dataFormat === 'csv' ? 'active' : ''}`}
                    onClick={() => setDataFormat('csv')}
                  >
                    CSV Paste
                  </button>
                </div>
              </div>

              <div className="form-group">
                <label>
                  {dataFormat === 'manual'
                    ? 'Case Data (date,cases per line)'
                    : 'CSV Data (with date,cases columns)'}
                </label>
                <textarea
                  value={casesData}
                  onChange={(e) => setCasesData(e.target.value)}
                  placeholder={
                    dataFormat === 'manual'
                      ? '2025-08-01,45\n2025-08-02,48\n2025-08-03,52'
                      : 'date,cases,aqi\n2025-08-01,45,120\n2025-08-02,48,125'
                  }
                  rows={8}
                  required
                />
                <small>Enter dates in YYYY-MM-DD format with corresponding case counts</small>
                <button type="button" className="helper-btn" onClick={loadSampleData}>
                  📋 Load Sample Data
                </button>
              </div>

              {dataFormat === 'manual' && (
                <div className="form-group">
                  <label>AQI Data (Optional)</label>
                  <textarea
                    value={aqiData}
                    onChange={(e) => setAqiData(e.target.value)}
                    placeholder="120\n125\n130"
                    rows={4}
                  />
                  <small>One AQI value per line, matching your case data entries</small>
                </div>
              )}

              <div className="form-row">
                <div className="form-group">
                  <label>Forecast Horizon (days)</label>
                  <input
                    type="number"
                    value={forecastHorizon}
                    onChange={(e) => setForecastHorizon(e.target.value)}
                    min="1"
                    max="30"
                  />
                </div>

                <div className="form-group">
                  <label>Analysis Window (days)</label>
                  <input
                    type="number"
                    value={windowDays}
                    onChange={(e) => setWindowDays(e.target.value)}
                    min="1"
                    max="30"
                  />
                </div>

                <div className="form-group">
                  <label>Risk Clusters</label>
                  <input
                    type="number"
                    value={nClusters}
                    onChange={(e) => setNClusters(e.target.value)}
                    min="2"
                    max="5"
                  />
                </div>
              </div>

              {error && <div className="error-box">{error}</div>}

              <button type="submit" className="submit-btn" disabled={loading}>
                {loading ? '🔄 Analyzing...' : '🚀 Assess Outbreak Risk'}
              </button>
            </form>
          </div>
        </div>

        <div className="results-section">
          {!result && (
            <div className="card placeholder">
              <div className="placeholder-content">
                <div className="placeholder-icon">🦠</div>
                <h3>Ready for Analysis</h3>
                <p>Enter disease case data to assess outbreak risk and receive detailed analysis with metrics and recommendations.</p>
              </div>
            </div>
          )}
          {result && (
            <div>
              <div className="risk-card" style={{ backgroundColor: getRiskColor(result.risk_index) }}>
                <div className="risk-header">
                <h3 style={{ color: getRiskTextColor(result.risk_index) }}>Risk Level</h3>
                <div
                  className="risk-badge"
                  style={{
                    backgroundColor: getRiskTextColor(result.risk_index),
                    color: getRiskColor(result.risk_index)
                  }}
                >
                  {result.risk_index}/5
                </div>
              </div>
              <div className="risk-label" style={{ color: getRiskTextColor(result.risk_index) }}>
                {result.risk_level}
              </div>
              <div className="risk-description" style={{ color: getRiskTextColor(result.risk_index) }}>
                {result.reason}
              </div>
            </div>

            <div className="metrics-grid">
              <div className="metric-card">
                <div className="metric-icon">📅</div>
                <div className="metric-label">Latest Date</div>
                <div className="metric-value">{result.latest_metrics.date}</div>
              </div>

              <div className="metric-card">
                <div className="metric-icon">🦠</div>
                <div className="metric-label">Current Cases</div>
                <div className="metric-value">{result.latest_metrics.cases}</div>
              </div>

              <div className="metric-card">
                <div className="metric-icon">📈</div>
                <div className="metric-label">7-Day Growth</div>
                <div className="metric-value">
                  {result.latest_metrics.growth_7d !== null && result.latest_metrics.growth_7d !== undefined
                    ? `${(result.latest_metrics.growth_7d * 100).toFixed(1)}%`
                    : 'N/A'}
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-icon">🌡️</div>
                <div className="metric-label">Z-Score</div>
                <div className="metric-value">{result.latest_metrics.residual_zscore.toFixed(2)}</div>
              </div>

              {result.latest_metrics.aqi !== null && result.latest_metrics.aqi !== undefined && (
                <div className="metric-card">
                  <div className="metric-icon">💨</div>
                  <div className="metric-label">Air Quality Index</div>
                  <div className="metric-value">{typeof result.latest_metrics.aqi === 'number' ? result.latest_metrics.aqi.toFixed(1) : 'N/A'}</div>
                </div>
              )}

              <div className="metric-card">
                <div className="metric-icon">{result.latest_metrics.recent_peak ? '⚠️' : '✓'}</div>
                <div className="metric-label">Recent Peak</div>
                <div className="metric-value">{result.latest_metrics.recent_peak ? 'Yes' : 'No'}</div>
              </div>
            </div>

            <div className="timeseries-section">
              <h3>📊 Time Series Analysis</h3>
              <div className="timeseries-info">
                <p>Data points analyzed: {result.time_series.dates.length}</p>
                <p>
                  Case range: {Math.min(...result.time_series.cases)} -{' '}
                  {Math.max(...result.time_series.cases)}
                </p>
                {result.time_series.peaks_idx.length > 0 && (
                  <p>Detected peaks: {result.time_series.peaks_idx.length}</p>
                )}
              </div>
            </div>

            <div className="info-card">
              <h4>📌 Cluster Assignment</h4>
              <p>This data pattern belongs to cluster {result.cluster_label}</p>
              <p className="small-text">
                Clusters represent similar outbreak patterns learned from historical data
              </p>
            </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PredictiveOutbreak;
