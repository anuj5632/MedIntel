import React, { useState } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import './InventoryForecast.css';

interface ForecastResult {
  item_id: string;
  forecast_data: Array<{
    date: string;
    predicted_demand: number;
    confidence_interval: [number, number];
  }>;
  reorder_point: number;
  safety_stock: number;
  recommendations: string[];
}

const InventoryForecast: React.FC = () => {
  const [itemId, setItemId] = useState('');
  const [category, setCategory] = useState('');
  const [currentStock, setCurrentStock] = useState('');
  const [leadTime, setLeadTime] = useState('');
  const [seasonality, setSeasonality] = useState('none');
  const [result, setResult] = useState<ForecastResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const categories = [
    'Medications', 'Surgical Supplies', 'PPE', 'Medical Devices', 
    'Laboratory Supplies', 'Consumables', 'Maintenance', 'Other'
  ];

  const seasonalities = [
    { value: 'none', label: 'No Seasonality' },
    { value: 'weekly', label: 'Weekly Pattern' },
    { value: 'monthly', label: 'Monthly Pattern' },
    { value: 'seasonal', label: 'Seasonal Pattern' }
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post('http://localhost:5000/api/inventory/forecast', {
        item_id: itemId,
        category,
        current_stock: parseInt(currentStock),
        lead_time_days: parseInt(leadTime),
        seasonality: seasonality === 'none' ? null : seasonality
      });

      setResult(response.data);
    } catch (err) {
      setError('Failed to generate inventory forecast. Please check your inputs and try again.');
      console.error('Inventory forecast error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStockStatus = (current: number, reorder: number, safety: number) => {
    if (current <= safety) return { status: 'Critical', color: '#ef4444' };
    if (current <= reorder) return { status: 'Low', color: '#f59e0b' };
    if (current <= reorder * 1.5) return { status: 'Good', color: '#22c55e' };
    return { status: 'High', color: '#3b82f6' };
  };

  return (
    <div className="inventory-forecast">
      <div className="page-header">
        <h1>Inventory Forecast</h1>
        <p>Predictive inventory management and supply chain optimization</p>
      </div>

      <div className="forecast-content">
        <div className="input-section">
          <div className="card">
            <h2>Inventory Analysis</h2>
            <form onSubmit={handleSubmit} className="inventory-form">
              <div className="form-group">
                <label htmlFor="itemId">Item ID / Name</label>
                <input
                  id="itemId"
                  type="text"
                  value={itemId}
                  onChange={(e) => setItemId(e.target.value)}
                  placeholder="e.g., MED-001, Surgical Gloves"
                  required
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="category">Category</label>
                  <select
                    id="category"
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    required
                  >
                    <option value="">Select Category</option>
                    {categories.map(cat => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="seasonality">Seasonality</label>
                  <select
                    id="seasonality"
                    value={seasonality}
                    onChange={(e) => setSeasonality(e.target.value)}
                    required
                  >
                    {seasonalities.map(season => (
                      <option key={season.value} value={season.value}>{season.label}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="currentStock">Current Stock Level</label>
                  <input
                    id="currentStock"
                    type="number"
                    value={currentStock}
                    onChange={(e) => setCurrentStock(e.target.value)}
                    placeholder="e.g., 150"
                    min="0"
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="leadTime">Lead Time (days)</label>
                  <input
                    id="leadTime"
                    type="number"
                    value={leadTime}
                    onChange={(e) => setLeadTime(e.target.value)}
                    placeholder="e.g., 7"
                    min="1"
                    required
                  />
                </div>
              </div>

              <button type="submit" disabled={loading} className="forecast-btn">
                {loading ? 'Generating Forecast...' : 'Generate Forecast'}
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
              <h2>Forecast Results</h2>
              
              <div className="inventory-header">
                <h3>Item: {result.item_id}</h3>
                {currentStock && (
                  <div className="stock-status">
                    <span className="status-label">Status:</span>
                    <span 
                      className="status-value"
                      style={{ 
                        color: getStockStatus(
                          parseInt(currentStock), 
                          result.reorder_point, 
                          result.safety_stock
                        ).color 
                      }}
                    >
                      {getStockStatus(parseInt(currentStock), result.reorder_point, result.safety_stock).status}
                    </span>
                  </div>
                )}
              </div>

              <div className="metrics-grid">
                <div className="metric-card">
                  <h4>Reorder Point</h4>
                  <div className="metric-value">{result.reorder_point}</div>
                  <div className="metric-label">Units</div>
                </div>
                
                <div className="metric-card">
                  <h4>Safety Stock</h4>
                  <div className="metric-value">{result.safety_stock}</div>
                  <div className="metric-label">Units</div>
                </div>

                <div className="metric-card">
                  <h4>Current Stock</h4>
                  <div className="metric-value">{currentStock}</div>
                  <div className="metric-label">Units</div>
                </div>

                <div className="metric-card">
                  <h4>Lead Time</h4>
                  <div className="metric-value">{leadTime}</div>
                  <div className="metric-label">Days</div>
                </div>
              </div>

              {result.forecast_data && result.forecast_data.length > 0 && (
                <div className="chart-container">
                  <h4>Demand Forecast</h4>
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

              {result.recommendations && result.recommendations.length > 0 && (
                <div className="recommendations">
                  <h4>Inventory Recommendations</h4>
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
                <div className="placeholder-icon">📦</div>
                <h3>Ready for Forecast</h3>
                <p>Enter inventory parameters to generate demand forecasts and optimize stock levels.</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default InventoryForecast;