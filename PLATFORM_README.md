# MEDINTEL Operations Platform

## Overview
MEDINTEL is a comprehensive medical operations intelligence platform that integrates AI-powered agents for medical facility management. The platform provides real-time monitoring, predictive analytics, and optimization capabilities across four core domains:

1. **Equipment & Utility Monitoring** - Anomaly detection for medical equipment
2. **Staff Optimization** - Intelligent staff scheduling and resource allocation
3. **Inventory Forecasting** - Predictive inventory management and supply chain optimization
4. **Demand Analysis** - Patient demand forecasting and capacity planning

## Architecture

### Frontend (React TypeScript)
- **Framework**: React 18 with TypeScript
- **Routing**: React Router DOM for navigation
- **UI Components**: Custom components with responsive design
- **Data Visualization**: Recharts for interactive charts and graphs
- **API Communication**: Axios for HTTP requests
- **Styling**: CSS modules with modern design system

### Backend (Flask Python)
- **Framework**: Flask with Flask-CORS for cross-origin requests
- **Agent Integration**: Unified API gateway connecting to all 4 agents
- **Machine Learning**: Scikit-learn, XGBoost, PyOD for predictive models
- **Data Processing**: Pandas, NumPy for data manipulation
- **Model Management**: Joblib for model serialization

### Agent Architecture
Each agent is a self-contained module with:
- **FastAPI service** for high-performance API endpoints
- **ML models** trained for specific domain tasks
- **Data processors** for input/output handling
- **Model artifacts** (scalers, trained models, calibration metadata)

## Project Structure

```
MEDINTEL/
├── frontend/                    # React TypeScript application
│   ├── src/
│   │   ├── components/         # React components
│   │   │   ├── Dashboard.tsx   # Main dashboard overview
│   │   │   ├── Navigation.tsx  # Navigation menu
│   │   │   ├── EquipmentMonitor.tsx
│   │   │   ├── StaffOptimizer.tsx
│   │   │   ├── InventoryForecast.tsx
│   │   │   └── DemandAnalysis.tsx
│   │   ├── utils/              # Utility functions and API tests
│   │   └── App.tsx             # Main application component
│   └── package.json            # Frontend dependencies
├── backend/                    # Flask API gateway
│   ├── app.py                  # Main Flask application
│   ├── config.py               # Configuration settings
│   └── requirements.txt        # Backend dependencies
├── agents/                     # AI agent modules
│   └── equipment_utility/      # Equipment monitoring agent
│       ├── app/               # FastAPI application
│       ├── models/            # Trained ML models
│       ├── data/              # Training/test data
│       ├── training/          # Training scripts
│       └── tests/             # Unit tests
└── .venv/                     # Python virtual environment
```

## Features

### Equipment & Utility Monitor
- **Real-time anomaly detection** using Isolation Forest algorithm
- **Calibrated risk scoring** with z-score normalization and sigmoid transformation
- **Equipment parameter monitoring**: temperature, pressure, vibration, power consumption
- **Maintenance recommendations** based on anomaly patterns
- **Visual alerts** with color-coded risk levels

### Staff Optimization
- **Intelligent scheduling** for different shift types (8-hour, 12-hour, flexible)
- **Specialty-based allocation** (RN, LPN, MD, Technician, etc.)
- **Efficiency scoring** with coverage percentage calculation
- **Department-specific optimization** for ICU, Emergency, Surgery, etc.
- **Cost savings analysis** and recommendations

### Inventory Forecasting
- **Predictive demand modeling** using time series analysis
- **Reorder point calculation** with safety stock optimization
- **Category-based forecasting** for medications, supplies, equipment
- **Seasonality detection** and pattern analysis
- **Interactive demand charts** with confidence intervals

### Demand Analysis
- **Patient demand forecasting** for capacity planning
- **Peak period identification** for resource allocation
- **Department-specific analysis** with patient type segmentation
- **Seasonality integration** for improved accuracy
- **Capacity recommendations** based on predicted demand

## API Endpoints

### Equipment Prediction
```
POST /api/equipment/predict
Content-Type: application/json

{
  "equipment_id": "string",
  "temperature": float,
  "pressure": float,
  "vibration": float,
  "power_consumption": float
}

Response: {
  "equipment_id": "string",
  "anomaly_score": float,
  "is_anomaly": boolean,
  "calibrated_score": float,
  "recommendations": ["string"]
}
```

### Staff Optimization
```
POST /api/staff/optimize
Content-Type: application/json

{
  "department": "string",
  "shift_type": "string",
  "staff_count": int,
  "patient_load": int,
  "specialty_required": "string"
}

Response: {
  "optimal_schedule": [],
  "efficiency_score": float,
  "coverage_percentage": float,
  "recommendations": ["string"],
  "cost_savings": float
}
```

### Inventory Forecasting
```
POST /api/inventory/forecast
Content-Type: application/json

{
  "item_id": "string",
  "category": "string",
  "current_stock": int,
  "lead_time_days": int,
  "seasonality": "string"
}

Response: {
  "item_id": "string",
  "forecast_data": [],
  "reorder_point": int,
  "safety_stock": int,
  "recommendations": ["string"]
}
```

### Demand Forecasting
```
POST /api/forecast/demand
Content-Type: application/json

{
  "department": "string",
  "forecast_days": int,
  "historical_months": int,
  "patient_type": "string",
  "include_seasonality": boolean
}

Response: {
  "forecast_period": "string",
  "forecast_data": [],
  "peak_periods": [],
  "capacity_recommendations": ["string"],
  "seasonality_factors": {}
}
```

## Installation & Setup

### Prerequisites
- Python 3.11+
- Node.js 16+
- Git

### Backend Setup
```bash
# Clone repository
git clone <repository-url>
cd MEDINTEL

# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate  # macOS/Linux

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Start Flask server
python app.py
```

### Frontend Setup
```bash
# Install frontend dependencies
cd frontend
npm install

# Start React development server
npm start
```

## Usage

1. **Access the application** at `http://localhost:3000`
2. **Navigate** using the sidebar menu to different agent dashboards
3. **Input parameters** for analysis in each agent's form
4. **View results** including predictions, visualizations, and recommendations
5. **Monitor equipment** through the Equipment Monitor for anomaly detection
6. **Optimize staff** schedules using the Staff Optimizer
7. **Forecast inventory** needs with the Inventory Forecast module
8. **Analyze demand** patterns with the Demand Analysis tool

## Testing

### Backend API Testing
```bash
# Test equipment prediction
curl -X POST -H "Content-Type: application/json" \
  -d '{"equipment_id":"TEST-001","temperature":25.5,"pressure":1.2,"vibration":0.05,"power_consumption":15.3}' \
  http://localhost:5000/api/equipment/predict
```

### Frontend Integration Testing
```typescript
// Import test utilities
import { runAllTests } from './src/utils/apiTests';

// Run comprehensive API tests
runAllTests();
```

## Technology Stack

### Frontend Technologies
- **React 18** - Modern UI framework with hooks
- **TypeScript** - Type-safe JavaScript development
- **React Router DOM** - Client-side routing
- **Axios** - HTTP client for API communication
- **Recharts** - Declarative charting library
- **CSS Modules** - Scoped styling approach

### Backend Technologies
- **Flask 3.0** - Lightweight Python web framework
- **Flask-CORS** - Cross-origin resource sharing
- **FastAPI** - High-performance API framework for agents
- **Uvicorn** - ASGI server for FastAPI applications

### Machine Learning Stack
- **Scikit-learn** - Machine learning algorithms
- **XGBoost** - Gradient boosting framework
- **PyOD** - Outlier detection toolkit
- **Pandas** - Data manipulation and analysis
- **NumPy** - Numerical computing
- **Joblib** - Model serialization

## Deployment

### Development Environment
- Frontend: `npm start` (http://localhost:3000)
- Backend: `python app.py` (http://localhost:5000)

### Production Considerations
- **Frontend**: Build with `npm run build` and deploy to static hosting
- **Backend**: Use production WSGI server like Gunicorn
- **Environment Variables**: Configure API URLs, database connections
- **SSL/HTTPS**: Enable secure connections for production
- **Database**: Integrate with PostgreSQL/MySQL for persistent data
- **Monitoring**: Add logging, metrics, and health checks

## Contributing

1. Fork the repository
2. Create feature branches: `git checkout -b feature/new-agent`
3. Commit changes: `git commit -am 'Add new forecasting agent'`
4. Push to branch: `git push origin feature/new-agent`
5. Submit pull request

## License

MIT License - see LICENSE file for details

## Support

For questions, issues, or contributions:
- Create issues on GitHub repository
- Review documentation in each agent's README
- Check API tests for integration examples
- Monitor application logs for debugging information