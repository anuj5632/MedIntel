import React, { useState } from 'react';
import axios from 'axios';
import './SupplyChainResilience.css';

interface Vendor {
  name: string;
  lead_times: number[];
}

interface VendorResult {
  vendor_name: string;
  score: number;
  recommendation: string;
}

interface SupplyChainResult {
  vendors: VendorResult[];
  overall_resilience_score: number;
  vendors_to_switch: number;
  total_vendors: number;
  weights: {
    delay_weight: number;
    reliability_weight: number;
  };
  threshold: number;
  timestamp: string;
}

const SupplyChainResilience: React.FC = () => {
  const [vendors, setVendors] = useState<Vendor[]>([
    { name: 'MedSupply Labs', lead_times: [11, 12, 12, 13, 14, 15] },
    { name: 'HealthPro Distributors', lead_times: [22, 3, 25, 26, 27, 28] },
    { name: 'RapidMed Logistics', lead_times: [78, 58, 98, 79, 98, 100] },
    { name: 'CareChain Global', lead_times: [28, 30, 31, 33, 34] },
    { name: 'VitaSource Pharma', lead_times: [95, 15, 16, 87, 18] }
  ]);

  const [threshold, setThreshold] = useState('40');
  const [result, setResult] = useState<SupplyChainResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [newVendor, setNewVendor] = useState({ name: '', lead_times: '' });

  const handleAddVendor = () => {
    if (!newVendor.name.trim()) {
      setError('Vendor name is required');
      return;
    }

    const leadTimesArray = newVendor.lead_times
      .split(',')
      .map((lt) => {
        const parsed = parseInt(lt.trim());
        if (isNaN(parsed)) throw new Error(`Invalid lead time: ${lt}`);
        return parsed;
      });

    if (leadTimesArray.length === 0) {
      setError('At least one lead time is required');
      return;
    }

    setVendors([...vendors, { name: newVendor.name, lead_times: leadTimesArray }]);
    setNewVendor({ name: '', lead_times: '' });
    setError(null);
  };

  const handleRemoveVendor = (index: number) => {
    setVendors(vendors.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post('http://localhost:5000/api/supply-chain/analyze', {
        vendors,
        threshold: parseInt(threshold)
      });

      setResult(response.data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Failed to analyze supply chain. Please check your data and try again.'
      );
      console.error('Supply chain analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 70) return '#22863a';
    if (score >= 50) return '#28a745';
    if (score >= 30) return '#ffc107';
    return '#dc3545';
  };

  const getRecommendationBadge = (recommendation: string) => {
    return recommendation === 'KEEP_VENDOR'
      ? { color: '#22863a', label: '✓ Keep' }
      : { color: '#dc3545', label: '⚠ Switch' };
  };

  return (
    <div className="supply-chain-resilience">
      <div className="page-header">
        <h1>Supply Chain Resilience</h1>
        <p>Vendor analysis and supply chain optimization</p>
      </div>

      <div className="supply-content">
        <div className="input-section">
          <div className="card">
            <h2>🏭 Vendor Management</h2>

            <form onSubmit={handleSubmit}>
              <div className="vendor-list">
                <h3>Current Vendors ({vendors.length})</h3>
                <div className="vendors-table">
                  {vendors.map((vendor, index) => (
                    <div key={index} className="vendor-row">
                      <div className="vendor-info">
                        <div className="vendor-name">{vendor.name}</div>
                        <div className="vendor-lead-times">
                          Lead times: {vendor.lead_times.join(', ')} days
                        </div>
                      </div>
                      <button
                        type="button"
                        className="remove-btn"
                        onClick={() => handleRemoveVendor(index)}
                      >
                        ✕
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              <div className="add-vendor-section">
                <h3>Add New Vendor</h3>
                <div className="form-group">
                  <label>Vendor Name</label>
                  <input
                    type="text"
                    value={newVendor.name}
                    onChange={(e) => setNewVendor({ ...newVendor, name: e.target.value })}
                    placeholder="e.g., MedSupply Labs"
                  />
                </div>

                <div className="form-group">
                  <label>Lead Times (comma-separated)</label>
                  <input
                    type="text"
                    value={newVendor.lead_times}
                    onChange={(e) => setNewVendor({ ...newVendor, lead_times: e.target.value })}
                    placeholder="e.g., 10,12,11,13,12"
                  />
                  <small>Enter lead times in days, separated by commas</small>
                </div>

                <button type="button" className="add-btn" onClick={handleAddVendor}>
                  + Add Vendor
                </button>
              </div>

              <div className="form-group">
                <label>Risk Threshold</label>
                <input
                  type="number"
                  value={threshold}
                  onChange={(e) => setThreshold(e.target.value)}
                  min="0"
                  max="100"
                />
                <small>Scores below this threshold trigger a "SWITCH_VENDOR" recommendation</small>
              </div>

              {error && <div className="error-box">{error}</div>}

              <button type="submit" className="submit-btn" disabled={loading}>
                {loading ? '🔄 Analyzing...' : '🚀 Analyze Supply Chain'}
              </button>
            </form>
          </div>
        </div>

        <div className="results-section">
          {!result && (
            <div className="card placeholder">
              <div className="placeholder-content">
                <div className="placeholder-icon">🏭</div>
                <h3>Ready for Analysis</h3>
                <p>Add vendors and set thresholds to analyze supply chain resilience and receive vendor recommendations.</p>
              </div>
            </div>
          )}

          {result && (
            <div>
              <div className="overview-cards">
              <div className="overview-card">
                <div className="card-icon">📊</div>
                <div className="card-label">Overall Resilience</div>
                <div className="card-value">{result.overall_resilience_score.toFixed(2)}</div>
              </div>

              <div className="overview-card">
                <div className="card-icon">✓</div>
                <div className="card-label">Vendors to Keep</div>
                <div className="card-value">{result.total_vendors - result.vendors_to_switch}</div>
              </div>

              <div className="overview-card">
                <div className="card-icon">⚠️</div>
                <div className="card-label">Vendors to Switch</div>
                <div className="card-value">{result.vendors_to_switch}</div>
              </div>

              <div className="overview-card">
                <div className="card-icon">🎯</div>
                <div className="card-label">Risk Threshold</div>
                <div className="card-value">{result.threshold.toFixed(1)}</div>
              </div>
            </div>

            <div className="vendors-analysis">
              <h3>📋 Vendor Analysis</h3>
              <div className="vendors-grid">
                {result.vendors.map((vendor, index) => {
                  const badge = getRecommendationBadge(vendor.recommendation);
                  const scoreColor = getScoreColor(vendor.score);
                  return (
                    <div
                      key={index}
                      className="vendor-card"
                      style={{ borderLeftColor: scoreColor }}
                    >
                      <div className="vendor-header">
                        <div className="vendor-title">{vendor.vendor_name}</div>
                        <div
                          className="recommendation-badge"
                          style={{ backgroundColor: badge.color }}
                        >
                          {badge.label}
                        </div>
                      </div>

                      <div className="vendor-score" style={{ color: scoreColor }}>
                        <span className="score-label">Resilience Score</span>
                        <span className="score-value">{vendor.score.toFixed(2)}</span>
                      </div>

                      <div className="score-bar">
                        <div
                          className="score-bar-fill"
                          style={{
                            width: `${Math.min((vendor.score / 100) * 100, 100)}%`,
                            backgroundColor: scoreColor
                          }}
                        />
                      </div>

                      <div className="score-range">
                        <span>0</span>
                        <span>100</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="weights-section">
              <h3>📈 Model Weights</h3>
              <div className="weights-info">
                <div className="weight-item">
                  <div className="weight-label">Delay Weight</div>
                  <div className="weight-value">{(result.weights.delay_weight * 100).toFixed(1)}%</div>
                </div>
                <div className="weight-item">
                  <div className="weight-label">Reliability Weight</div>
                  <div className="weight-value">{(result.weights.reliability_weight * 100).toFixed(1)}%</div>
                </div>
              </div>
              <p className="small-text">
                These weights determine how delay and reliability impact the resilience score
              </p>
            </div>

            <div className="timestamp">
              <small>Analysis completed: {new Date(result.timestamp).toLocaleString()}</small>
            </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SupplyChainResilience;
