import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart } from 'recharts';
import { Activity, Users, Package, AlertTriangle, TrendingUp, Calendar, Wind, Stethoscope, Truck, MessageSquare } from 'lucide-react';

// Simulated Multi-Agent System
class Agent {
  constructor(name, role) {
    this.name = name;
    this.role = role;
    this.status = 'active';
    this.lastAction = null;
  }

  process(data) {
    this.lastAction = new Date().toISOString();
    return this.analyze(data);
  }

  analyze(data) {
    return {};
  }
}

class ForecastingAgent extends Agent {
  constructor() {
    super('Forecasting Agent', 'Patient Inflow Prediction');
  }

  analyze(data) {
    const { historicalData, aqi, festival, weather } = data;
    let basePrediction = 120;
    
    // Festival impact
    if (festival?.upcoming) basePrediction *= 1.4;
    
    // AQI impact
    if (aqi > 300) basePrediction *= 1.3;
    else if (aqi > 200) basePrediction *= 1.15;
    
    // Weather impact
    if (weather?.temp > 38) basePrediction *= 1.1;
    
    return {
      predictedInflow: Math.round(basePrediction),
      confidence: 0.87,
      peakHours: ['10:00-12:00', '18:00-20:00'],
      surge: basePrediction > 150
    };
  }
}

class StaffOptimizationAgent extends Agent {
  constructor() {
    super('Staff Optimization Agent', 'Shift Scheduling');
  }

  analyze(data) {
    const { predictedInflow } = data;
    const baseStaff = 45;
    const requiredStaff = Math.ceil(baseStaff * (predictedInflow / 120));
    
    return {
      currentStaff: baseStaff,
      requiredStaff,
      shortfall: Math.max(0, requiredStaff - baseStaff),
      recommendation: requiredStaff > baseStaff ? 'Call additional staff' : 'Normal staffing',
      shiftPlan: [
        { shift: 'Morning', doctors: Math.ceil(requiredStaff * 0.35), nurses: Math.ceil(requiredStaff * 0.65) },
        { shift: 'Evening', doctors: Math.ceil(requiredStaff * 0.40), nurses: Math.ceil(requiredStaff * 0.60) },
        { shift: 'Night', doctors: Math.ceil(requiredStaff * 0.25), nurses: Math.ceil(requiredStaff * 0.75) }
      ]
    };
  }
}

class InventoryAgent extends Agent {
  constructor() {
    super('Medical Supply Agent', 'Inventory Management');
  }

  analyze(data) {
    const { predictedInflow, currentInventory } = data;
    const consumptionRate = predictedInflow / 100;
    
    return {
      alerts: [
        { item: 'N95 Masks', current: 450, required: 800, status: 'critical', reorder: 500 },
        { item: 'Oxygen Cylinders', current: 28, required: 35, status: 'warning', reorder: 15 },
        { item: 'IV Fluids', current: 320, required: 250, status: 'good', reorder: 0 },
        { item: 'Antibiotics', current: 180, required: 200, status: 'warning', reorder: 100 }
      ],
      estimatedRunout: '3 days',
      autoReorderTriggered: true
    };
  }
}

class EquipmentAgent extends Agent {
  constructor() {
    super('Equipment Agent', 'Predictive Maintenance');
  }

  analyze(data) {
    return {
      equipment: [
        { name: 'Ventilator-A3', status: 'operational', nextMaintenance: '5 days', utilization: 85 },
        { name: 'Ventilator-B7', status: 'maintenance_due', nextMaintenance: 'overdue', utilization: 92 },
        { name: 'CT Scanner', status: 'operational', nextMaintenance: '12 days', utilization: 68 },
        { name: 'X-Ray Machine 2', status: 'warning', nextMaintenance: '2 days', utilization: 78 }
      ],
      criticalAlerts: 1
    };
  }
}

class OutbreakAgent extends Agent {
  constructor() {
    super('Outbreak Detection Agent', 'Epidemic Monitoring');
  }

  analyze(data) {
    const { aqi, recentCases } = data;
    
    return {
      riskLevel: aqi > 300 ? 'high' : aqi > 200 ? 'moderate' : 'low',
      detectedPatterns: [
        { condition: 'Respiratory Infections', trend: 'increasing', cases: 34, change: '+28%' },
        { condition: 'Asthma Attacks', trend: 'increasing', cases: 22, change: '+45%' },
        { condition: 'Cardiac Issues', trend: 'stable', cases: 12, change: '+5%' }
      ],
      recommendation: 'Prepare respiratory care units'
    };
  }
}

class TelemedicineAgent extends Agent {
  constructor() {
    super('Telemedicine Agent', 'Remote Triage');
  }

  analyze(data) {
    return {
      triageStats: {
        totalConsultations: 87,
        remote: 52,
        inPerson: 35,
        diversionRate: 60
      },
      categories: [
        { severity: 'Mild', count: 45, action: 'Telemedicine' },
        { severity: 'Moderate', count: 28, action: 'Schedule Visit' },
        { severity: 'Severe', count: 14, action: 'Immediate ER' }
      ]
    };
  }
}

class EmergencyAgent extends Agent {
  constructor() {
    super('Emergency Readiness Agent', 'Surge Protocol');
  }

  analyze(data) {
    const { predictedInflow } = data;
    const surgeActivated = predictedInflow > 150;
    
    return {
      surgeProtocol: surgeActivated,
      icuAvailability: { total: 24, occupied: 18, available: 6 },
      erStatus: 'Code Yellow',
      recommendations: surgeActivated ? [
        'Activate overflow ward',
        'Call on-call physicians',
        'Expedite discharge processes'
      ] : ['Monitor situation']
    };
  }
}

class CoordinationAgent extends Agent {
  constructor() {
    super('Coordination Agent', 'Inter-department Sync');
  }

  analyze(data) {
    return {
      departmentStatus: [
        { dept: 'Emergency', load: 85, status: 'high' },
        { dept: 'ICU', load: 75, status: 'moderate' },
        { dept: 'General Ward', load: 60, status: 'normal' },
        { dept: 'Outpatient', load: 70, status: 'moderate' }
      ],
      ambulanceQueue: 4,
      interDepartmentTransfers: 7
    };
  }
}

class SupplyChainAgent extends Agent {
  constructor() {
    super('Supply Chain Agent', 'Vendor Management');
  }

  analyze(data) {
    return {
      vendorStatus: [
        { vendor: 'MedSupply Co.', status: 'on-time', reliability: 95 },
        { vendor: 'Pharma Direct', status: 'delayed', reliability: 78, delay: '2 days' },
        { vendor: 'Equipment Plus', status: 'on-time', reliability: 92 }
      ],
      alternateSourcesRecommended: ['Pharma Direct'],
      estimatedDelay: '48 hours'
    };
  }
}

class CommunityHealthAgent extends Agent {
  constructor() {
    super('Community Health Agent', 'Public Advisories');
  }

  analyze(data) {
    const { aqi } = data;
    
    return {
      alertsSent: 1247,
      languages: ['Hindi', 'Marathi', 'English'],
      currentAdvisory: aqi > 300 ? 
        'Severe air pollution. Wear N95 masks. Limit outdoor activity.' :
        'Moderate pollution levels. Take precautions if sensitive.',
      engagement: 82
    };
  }
}

// Main Dashboard Component
const MedIntelDashboard = () => {
  const [agents, setAgents] = useState([]);
  const [predictions, setPredictions] = useState(null);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [simulationData, setSimulationData] = useState({
    aqi: 285,
    festival: { upcoming: true, name: 'Diwali', days: 3 },
    weather: { temp: 32, humidity: 65 },
    currentTime: new Date()
  });

  useEffect(() => {
    initializeAgents();
    runSimulation();
  }, []);

  const initializeAgents = () => {
    const agentInstances = [
      new ForecastingAgent(),
      new StaffOptimizationAgent(),
      new InventoryAgent(),
      new EquipmentAgent(),
      new OutbreakAgent(),
      new TelemedicineAgent(),
      new EmergencyAgent(),
      new CoordinationAgent(),
      new SupplyChainAgent(),
      new CommunityHealthAgent()
    ];
    setAgents(agentInstances);
  };

  const runSimulation = () => {
    const forecast = new ForecastingAgent().analyze(simulationData);
    const staff = new StaffOptimizationAgent().analyze({ predictedInflow: forecast.predictedInflow });
    const inventory = new InventoryAgent().analyze({ predictedInflow: forecast.predictedInflow });
    const equipment = new EquipmentAgent().analyze({});
    const outbreak = new OutbreakAgent().analyze({ aqi: simulationData.aqi });
    const telemedicine = new TelemedicineAgent().analyze({});
    const emergency = new EmergencyAgent().analyze({ predictedInflow: forecast.predictedInflow });
    const coordination = new CoordinationAgent().analyze({});
    const supply = new SupplyChainAgent().analyze({});
    const community = new CommunityHealthAgent().analyze({ aqi: simulationData.aqi });

    setPredictions({
      forecast,
      staff,
      inventory,
      equipment,
      outbreak,
      telemedicine,
      emergency,
      coordination,
      supply,
      community
    });
  };

  const historicalData = [
    { date: 'Oct 14', actual: 95, predicted: 92 },
    { date: 'Oct 15', actual: 108, predicted: 105 },
    { date: 'Oct 16', actual: 122, predicted: 118 },
    { date: 'Oct 17', actual: 134, predicted: 138 },
    { date: 'Oct 18', actual: 145, predicted: 142 },
    { date: 'Oct 19', actual: 152, predicted: 155 },
    { date: 'Oct 20', predicted: 168 }
  ];

  const aqiData = [
    { time: '6 AM', aqi: 245 },
    { time: '9 AM', aqi: 268 },
    { time: '12 PM', aqi: 285 },
    { time: '3 PM', aqi: 292 },
    { time: '6 PM', aqi: 310 },
    { time: '9 PM', aqi: 298 }
  ];

  if (!predictions) return <div className="flex items-center justify-center h-screen">Loading MedIntel System...</div>;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-800 flex items-center gap-3">
                <Activity className="text-blue-600" size={36} />
                MedIntel – Predictive Hospital Management
              </h1>
              <p className="text-gray-600 mt-2">From Crisis Response to Predictive Readiness</p>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-500">Current Time</div>
              <div className="text-lg font-semibold">{new Date().toLocaleTimeString()}</div>
              <div className="text-sm text-gray-600">{new Date().toLocaleDateString()}</div>
            </div>
          </div>
        </div>

        {/* Critical Alerts */}
        {predictions.forecast.surge && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6 rounded-lg">
            <div className="flex items-center">
              <AlertTriangle className="text-red-600 mr-3" size={24} />
              <div>
                <h3 className="font-bold text-red-800">SURGE ALERT ACTIVATED</h3>
                <p className="text-red-700">Predicted patient inflow: {predictions.forecast.predictedInflow} (40% above normal). Emergency protocols engaged.</p>
              </div>
            </div>
          </div>
        )}

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Predicted Inflow</p>
                <p className="text-3xl font-bold text-blue-600">{predictions.forecast.predictedInflow}</p>
                <p className="text-xs text-green-600 mt-1">87% confidence</p>
              </div>
              <TrendingUp className="text-blue-600" size={32} />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Staff Required</p>
                <p className="text-3xl font-bold text-purple-600">{predictions.staff.requiredStaff}</p>
                <p className="text-xs text-orange-600 mt-1">+{predictions.staff.shortfall} needed</p>
              </div>
              <Users className="text-purple-600" size={32} />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Critical Alerts</p>
                <p className="text-3xl font-bold text-red-600">{predictions.inventory.alerts.filter(a => a.status === 'critical').length}</p>
                <p className="text-xs text-gray-600 mt-1">Inventory issues</p>
              </div>
              <Package className="text-red-600" size={32} />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">AQI Level</p>
                <p className="text-3xl font-bold text-orange-600">{simulationData.aqi}</p>
                <p className="text-xs text-red-600 mt-1">Severe pollution</p>
              </div>
              <Wind className="text-orange-600" size={32} />
            </div>
          </div>
        </div>

        {/* Main Charts */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
              <TrendingUp size={20} className="text-blue-600" />
              Patient Inflow Forecast (7-Day)
            </h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={historicalData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="actual" stroke="#3b82f6" strokeWidth={2} name="Actual" />
                <Line type="monotone" dataKey="predicted" stroke="#8b5cf6" strokeWidth={2} strokeDasharray="5 5" name="Predicted" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
              <Wind size={20} className="text-orange-600" />
              Air Quality Index (AQI) Trend
            </h3>
            <ResponsiveContainer width="100%" height={250}>
              <AreaChart data={aqiData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Area type="monotone" dataKey="aqi" stroke="#f97316" fill="#fed7aa" name="AQI Level" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Agent Status Grid */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h3 className="text-lg font-bold mb-4">Multi-Agent System Status</h3>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            {agents.map((agent, idx) => (
              <div
                key={idx}
                onClick={() => setSelectedAgent(agent)}
                className="border-2 border-gray-200 rounded-lg p-3 cursor-pointer hover:border-blue-500 hover:shadow-md transition-all"
              >
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-xs font-semibold text-gray-700">{agent.name}</span>
                </div>
                <p className="text-xs text-gray-500">{agent.role}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Detailed Insights */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          {/* Inventory Alerts */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
              <Package size={20} className="text-blue-600" />
              Critical Inventory Alerts
            </h3>
            <div className="space-y-3">
              {predictions.inventory.alerts.map((alert, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-semibold text-sm">{alert.item}</p>
                    <p className="text-xs text-gray-600">Current: {alert.current} | Required: {alert.required}</p>
                  </div>
                  <div className="text-right">
                    <span className={`px-2 py-1 rounded text-xs font-bold ${
                      alert.status === 'critical' ? 'bg-red-100 text-red-700' :
                      alert.status === 'warning' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-green-100 text-green-700'
                    }`}>
                      {alert.status.toUpperCase()}
                    </span>
                    {alert.reorder > 0 && (
                      <p className="text-xs text-blue-600 mt-1">Reorder: {alert.reorder}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Outbreak Detection */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
              <Stethoscope size={20} className="text-red-600" />
              Outbreak Detection & Patterns
            </h3>
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-semibold">Risk Level</span>
                <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                  predictions.outbreak.riskLevel === 'high' ? 'bg-red-100 text-red-700' :
                  predictions.outbreak.riskLevel === 'moderate' ? 'bg-yellow-100 text-yellow-700' :
                  'bg-green-100 text-green-700'
                }`}>
                  {predictions.outbreak.riskLevel.toUpperCase()}
                </span>
              </div>
            </div>
            <div className="space-y-2">
              {predictions.outbreak.detectedPatterns.map((pattern, idx) => (
                <div key={idx} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <div>
                    <p className="text-sm font-semibold">{pattern.condition}</p>
                    <p className="text-xs text-gray-600">{pattern.cases} cases</p>
                  </div>
                  <span className={`text-xs font-bold ${
                    pattern.trend === 'increasing' ? 'text-red-600' : 'text-green-600'
                  }`}>
                    {pattern.change}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Staff Scheduling */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
              <Users size={20} className="text-purple-600" />
              Optimized Shift Schedule
            </h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={predictions.staff.shiftPlan}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="shift" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="doctors" fill="#8b5cf6" name="Doctors" />
                <Bar dataKey="nurses" fill="#06b6d4" name="Nurses" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
              <MessageSquare size={20} className="text-green-600" />
              Telemedicine Triage Stats
            </h3>
            <div className="mb-4">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm">Diversion Rate</span>
                <span className="text-2xl font-bold text-green-600">{predictions.telemedicine.triageStats.diversionRate}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div className="bg-green-500 h-3 rounded-full" style={{ width: `${predictions.telemedicine.triageStats.diversionRate}%` }}></div>
              </div>
            </div>
            <div className="space-y-2">
              {predictions.telemedicine.categories.map((cat, idx) => (
                <div key={idx} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                  <div>
                    <p className="text-sm font-semibold">{cat.severity}</p>
                    <p className="text-xs text-gray-600">{cat.action}</p>
                  </div>
                  <span className="text-lg font-bold text-blue-600">{cat.count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Emergency & Community */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
              <AlertTriangle size={20} className="text-red-600" />
              Emergency Readiness
            </h3>
            <div className="mb-4">
              <div className="flex justify-between mb-2">
                <span className="text-sm font-semibold">ICU Availability</span>
                <span className="text-sm">{predictions.emergency.icuAvailability.available} / {predictions.emergency.icuAvailability.total}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div className="bg-blue-500 h-3 rounded-full" style={{ width: `${(predictions.emergency.icuAvailability.occupied / predictions.emergency.icuAvailability.total) * 100}%` }}></div>
              </div>
            </div>
            <div className="space-y-2">
              <div className="p-3 bg-yellow-50 border border-yellow-200 rounded">
                <p className="text-sm font-bold text-yellow-800">ER Status: {predictions.emergency.erStatus}</p>
              </div>
              {predictions.emergency.recommendations.map((rec, idx) => (
                <div key={idx} className="p-2 bg-gray-50 rounded text-sm">
                  • {rec}
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
              <MessageSquare size={20} className="text-blue-600" />
              Community Health Alerts
            </h3>
            <div className="space-y-4">
              <div className="p-4 bg-blue-50 border-l-4 border-blue-500 rounded">
                <p className="text-sm font-bold text-blue-800">Current Advisory</p>
                <p className="text-sm text-blue-700 mt-1">{predictions.community.currentAdvisory}</p>
              </div>
              <div className="grid grid-cols-3 gap-3">
                <div className="text-center p-3 bg-gray-50 rounded">
                  <p className="text-2xl font-bold text-blue-600">{predictions.community.alertsSent}</p>
                  <p className="text-xs text-gray-600">Alerts Sent</p>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded">
                  <p className="text-2xl font-bold text-green-600">{predictions.community.engagement}%</p>
                  <p className="text-xs text-gray-600">Engagement</p>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded">
                  <p className="text-2xl font-bold text-purple-600">{predictions.community.languages.length}</p>
                  <p className="text-xs text-gray-600">Languages</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MedIntelDashboard;