import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import Dashboard from './components/Dashboard';
import EquipmentMonitor from './components/EquipmentMonitor';
import StaffOptimizer from './components/StaffOptimizer';
import InventoryForecast from './components/InventoryForecast';
import DemandAnalysis from './components/DemandAnalysis';
import TriageAgent from './components/TriageAgent';
import PredictiveOutbreak from './components/PredictiveOutbreak';
import SupplyChainResilience from './components/SupplyChainResilience';
import CommunityHealth from './components/CommunityHealth';
import { Login } from './components/Auth';
import { HospitalDashboard, Patients, Appointments, Billing, Pharmacy, Laboratory, IPD } from './components/Hospital';
import Navigation from './components/Navigation';

function App() {
  return (
    <Router>
      <div className="App">
        <Navigation />
        <main className="main-content">
          <Routes>
            <Route path="/login" element={<Login onLogin={() => {}} />} />
            <Route path="/dashboard" element={<HospitalDashboard />} />
            <Route path="/" element={<HospitalDashboard />} />
            {/* Hospital Management Routes */}
            <Route path="/patients" element={<Patients />} />
            <Route path="/appointments" element={<Appointments />} />
            <Route path="/billing" element={<Billing />} />
            <Route path="/pharmacy" element={<Pharmacy />} />
            <Route path="/lab" element={<Laboratory />} />
            <Route path="/ipd" element={<IPD />} />
            {/* AI Agent Routes */}
            <Route path="/equipment" element={<EquipmentMonitor />} />
            <Route path="/staff" element={<StaffOptimizer />} />
            <Route path="/inventory" element={<InventoryForecast />} />
            <Route path="/demand" element={<DemandAnalysis />} />
            <Route path="/triage" element={<TriageAgent />} />
            <Route path="/outbreak" element={<PredictiveOutbreak />} />
            <Route path="/supply-chain" element={<SupplyChainResilience />} />
            <Route path="/community-health" element={<CommunityHealth />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
