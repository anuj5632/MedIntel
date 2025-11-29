import React, { useState } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import './DemandAnalysis.css';

interface DemandResult {
  forecast_period: string;
  forecast_data: Array<{
    date: string;
    predicted_demand: number;
    confidence_interval: [number, number];
    department?: string;
  }>;
  peak_periods: Array<{
    period: string;
    estimated_demand: number;
  }>;
  capacity_recommendations: string[];
  seasonality_factors: any;
}

const DemandAnalysis: React.FC = () => {
  const [department, setDepartment] = useState('');
  const [forecastPeriod, setForecastPeriod] = useState('30');
  const [historicalData, setHistoricalData] = useState('');
  const [patientType, setPatientType] = useState('');
  const [includeSeasonality, setIncludeSeasonality] = useState(true);
  const [result, setResult] = useState<DemandResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const departments = [
    'Emergency', 'ICU', 'Surgery', 'Outpatient', 'Cardiology', 
    'Pediatrics', 'Oncology', 'Radiology', 'Laboratory', 'General'
  ];

  const patientTypes = [
    'All Patients', 'Emergency', 'Elective', 'Critical Care', 
    'Outpatient', 'Inpatient', 'Pediatric', 'Geriatric'
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post('http://localhost:5000/api/forecast/demand', {
        department: department || null,
        forecast_days: parseInt(forecastPeriod),
        historical_months: historicalData ? parseInt(historicalData) : 12,
        patient_type: patientType === 'All Patients' ? null : patientType,
        include_seasonality: includeSeasonality
      });

      setResult(response.data);
    } catch (err) {
      setError('Failed to generate demand forecast. Please check your inputs and try again.');
      console.error('Demand forecast error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getTotalPredictedDemand = () => {
    if (!result?.forecast_data) return 0;
    return result.forecast_data.reduce((sum, item) => sum + item.predicted_demand, 0);
  };

  const getAverageDailyDemand = () => {
    if (!result?.forecast_data || result.forecast_data.length === 0) return 0;
    return getTotalPredictedDemand() / result.forecast_data.length;
  };

  const getPeakDemand = () => {
    if (!result?.forecast_data) return 0;
    return Math.max(...result.forecast_data.map(item => item.predicted_demand));
  };

  return (
    <div className="demand-analysis">
      <div className="page-header">
        <h1>Demand Analysis</h1>
        <p>Patient demand forecasting and capacity planning</p>
      </div>

      <div className="analysis-content">
        <div className="input-section">
          <div className="card">
            <h2>Demand Forecast</h2>
            <form onSubmit={handleSubmit} className="demand-form">
              <div className="form-group">
                <label htmlFor="department">Department (Optional)</label>
                <select
                  id="department"
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                >
                  <option value="">All Departments</option>
                  {departments.map(dept => (
                    <option key={dept} value={dept}>{dept}</option>
                  ))}
                </select>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="forecastPeriod">Forecast Period (days)</label>
                  <select
                    id="forecastPeriod"
                    value={forecastPeriod}
                    onChange={(e) => setForecastPeriod(e.target.value)}
                    required
                  >
                    <option value="7">1 Week</option>
                    <option value="14">2 Weeks</option>
                    <option value="30">1 Month</option>
                    <option value="90">3 Months</option>
                    <option value="180">6 Months</option>
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="historicalData">Historical Data (months)</label>
                  <select
                    id="historicalData"
                    value={historicalData}
                    onChange={(e) => setHistoricalData(e.target.value)}
                  >
                    <option value="">Default (12 months)</option>
                    <option value="6">6 Months</option>
                    <option value="12">12 Months</option>
                    <option value="24">24 Months</option>
                    <option value="36">36 Months</option>
                  </select>
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="patientType">Patient Type</label>
                  <select
                    id="patientType"
                    value={patientType}
                    onChange={(e) => setPatientType(e.target.value)}
                    required
                  >
                    <option value="">Select Patient Type</option>
                    {patientTypes.map(type => (
                      <option key={type} value={type}>{type}</option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <div className="checkbox-group">
                    <label htmlFor="includeSeasonality" className="checkbox-label">
                      <input
                        id="includeSeasonality"
                        type="checkbox"
                        checked={includeSeasonality}
                        onChange={(e) => setIncludeSeasonality(e.target.checked)}
                      />
                      Include Seasonality Analysis
                    </label>
                  </div>
                </div>
              </div>

              <button type="submit" disabled={loading} className="analyze-btn">
                {loading ? 'Analyzing Demand...' : 'Analyze Demand'}
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
              <h2>Demand Forecast Results</h2>
              
              <div className="forecast-header">
                <h3>Forecast Period: {result.forecast_period || `${forecastPeriod} days`}</h3>
                <div className="period-info">
                  {department && <span>Department: {department}</span>}
                  {patientType && <span>Patient Type: {patientType}</span>}
                </div>
              </div>

              <div className="metrics-grid">
                <div className="metric-card">
                  <h4>Total Predicted Demand</h4>
                  <div className="metric-value">{Math.round(getTotalPredictedDemand())}</div>
                  <div className="metric-label">Patients</div>
                </div>
                
                <div className="metric-card">
                  <h4>Average Daily Demand</h4>
                  <div className="metric-value">{Math.round(getAverageDailyDemand())}</div>
                  <div className="metric-label">Patients/day</div>
                </div>

                <div className="metric-card">
                  <h4>Peak Demand</h4>
                  <div className="metric-value">{Math.round(getPeakDemand())}</div>
                  <div className="metric-label">Patients/day</div>
                </div>

                <div className="metric-card">
                  <h4>Peak Periods</h4>
                  <div className="metric-value">{result.peak_periods?.length || 0}</div>
                  <div className="metric-label">Identified</div>
                </div>
              </div>

              {result.forecast_data && result.forecast_data.length > 0 && (
                <div className="chart-container">
                  <h4>Demand Forecast Trend</h4>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={result.forecast_data}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Line 
                        type="monotone" 
                        dataKey="predicted_demand" 
                        stroke="#667eea" 
                        strokeWidth={2}
                        name="Predicted Demand"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}

              {result.peak_periods && result.peak_periods.length > 0 && (
                <div className="peak-periods">
                  <h4>Peak Demand Periods</h4>
                  <div className="peaks-grid">
                    {result.peak_periods.slice(0, 6).map((peak, index) => (
                      <div key={index} className="peak-card">
                        <div className="peak-period">{peak.period}</div>
                        <div className="peak-demand">{Math.round(peak.estimated_demand)} patients</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {result.capacity_recommendations && result.capacity_recommendations.length > 0 && (
                <div className="recommendations">
                  <h4>Capacity Recommendations</h4>
                  <ul>
                    {result.capacity_recommendations.map((rec, index) => (
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
                <div className="placeholder-icon">📈</div>
                <h3>Ready for Analysis</h3>
                <p>Configure forecast parameters to analyze patient demand patterns and optimize capacity planning.</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DemandAnalysis;