import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000';

// Test Equipment Prediction
export const testEquipmentPrediction = async () => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/equipment/predict`, {
      equipment_id: 'TEST-MRI-001',
      temperature: 23.5,
      pressure: 1.2,
      vibration: 0.05,
      power_consumption: 15.3
    });
    console.log('Equipment Prediction Test:', response.data);
    return response.data;
  } catch (error) {
    console.error('Equipment Test Error:', error);
    throw error;
  }
};

// Test Staff Optimization
export const testStaffOptimization = async () => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/staff/optimize`, {
      department: 'ICU',
      shift_type: '12-hour',
      staff_count: 15,
      patient_load: 45,
      specialty_required: 'RN'
    });
    console.log('Staff Optimization Test:', response.data);
    return response.data;
  } catch (error) {
    console.error('Staff Test Error:', error);
    throw error;
  }
};

// Test Inventory Forecast
export const testInventoryForecast = async () => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/inventory/forecast`, {
      item_id: 'MED-001',
      category: 'Medications',
      current_stock: 150,
      lead_time_days: 7,
      seasonality: 'weekly'
    });
    console.log('Inventory Forecast Test:', response.data);
    return response.data;
  } catch (error) {
    console.error('Inventory Test Error:', error);
    throw error;
  }
};

// Test Demand Forecast
export const testDemandForecast = async () => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/forecast/demand`, {
      department: 'Emergency',
      forecast_days: 30,
      historical_months: 12,
      patient_type: 'Emergency',
      include_seasonality: true
    });
    console.log('Demand Forecast Test:', response.data);
    return response.data;
  } catch (error) {
    console.error('Demand Test Error:', error);
    throw error;
  }
};

// Run all tests
export const runAllTests = async () => {
  console.log('Running API Integration Tests...');
  
  try {
    await testEquipmentPrediction();
    await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second
    
    await testStaffOptimization();
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    await testInventoryForecast();
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    await testDemandForecast();
    
    console.log('All tests completed successfully!');
  } catch (error) {
    console.error('Test suite failed:', error);
  }
};