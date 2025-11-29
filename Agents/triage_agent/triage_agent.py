"""
Medical Triage Agent for Emergency Department
Analyzes patient data and provides triage recommendations
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pickle
import os

class TriageAgent:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_columns = [
            'age', 'temperature', 'heart_rate', 'systolic_bp', 'diastolic_bp',
            'respiratory_rate', 'spo2', 'chest_pain', 'shortness_of_breath',
            'altered_consciousness', 'severe_bleeding', 'pain_score',
            'symptom_duration_days', 'comorbidities_count', 'symptom_severity'
        ]
        self.load_or_train_model()
    
    def load_or_train_model(self):
        """Train a new model (skip loading pre-trained model due to compatibility issues)"""
        print("Training new triage model...")
        self.train_model()
    
    def train_model(self):
        """Train the triage model using the dataset"""
        try:
            dataset_path = os.path.join(os.path.dirname(__file__), 'data', 'triage_dataset.csv')
            df = pd.read_csv(dataset_path)
            
            # Prepare features and target
            X = df[self.feature_columns]
            y = df['triage_recommendation']
            
            # Initialize and fit scaler
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
            
            # Train Random Forest model
            self.model = RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                max_depth=10
            )
            self.model.fit(X_scaled, y)
            
            print("Triage model trained successfully")
            
        except Exception as e:
            print(f"Error training model: {e}")
            # Fallback to rule-based system
            self.model = None
    
    def assess_patient(self, patient_data):
        """
        Assess patient and provide triage recommendation
        
        Args:
            patient_data (dict): Patient information including vitals and symptoms
            
        Returns:
            dict: Triage assessment results
        """
        try:
            # Extract features for ML model
            features = self._extract_features(patient_data)
            
            if self.model is not None and self.scaler is not None:
                # Use ML model prediction
                features_array = np.array([features])
                features_scaled = self.scaler.transform(features_array)
                prediction = self.model.predict(features_scaled)[0]
                probabilities = self.model.predict_proba(features_scaled)[0]
                
                # Get confidence score
                max_prob = max(probabilities)
                
            else:
                # Fallback to rule-based assessment
                prediction = self._rule_based_assessment(patient_data)
                max_prob = 0.85  # Default confidence for rule-based
            
            # Calculate urgency score
            urgency_score = self._calculate_urgency_score(patient_data)
            
            # Determine recommended department
            department = self._determine_department(patient_data, prediction)
            
            # Generate risk factors and recommendations
            risk_factors = self._identify_risk_factors(patient_data)
            recommendations = self._generate_recommendations(patient_data, prediction)
            
            return {
                'patient_id': str(patient_data.get('patient_id', 'Unknown')),
                'triage_category': str(prediction),
                'urgency_score': float(min(urgency_score, 1.0)),
                'confidence': float(round(max_prob, 3)),
                'vital_signs': {
                    'temperature': float(patient_data.get('temperature', 0)),
                    'heart_rate': int(patient_data.get('heart_rate', 0)),
                    'blood_pressure': f"{int(patient_data.get('systolic_bp', 0))}/{int(patient_data.get('diastolic_bp', 0))}",
                    'respiratory_rate': int(patient_data.get('respiratory_rate', 0)),
                    'oxygen_saturation': int(patient_data.get('spo2', 0))
                },
                'recommended_department': str(department),
                'risk_factors': [str(f) for f in risk_factors],
                'recommendations': [str(r) for r in recommendations],
                'wait_time_estimate': str(self._estimate_wait_time(prediction))
            }
            
        except Exception as e:
            return self._emergency_fallback(patient_data, str(e))
    
    def _extract_features(self, patient_data):
        """Extract features for ML model"""
        return [
            patient_data.get('age', 50),
            patient_data.get('temperature', 36.5),
            patient_data.get('heart_rate', 80),
            patient_data.get('systolic_bp', 120),
            patient_data.get('diastolic_bp', 80),
            patient_data.get('respiratory_rate', 16),
            patient_data.get('spo2', 98),
            1 if 'chest pain' in patient_data.get('symptoms', '').lower() else 0,
            1 if 'shortness of breath' in patient_data.get('symptoms', '').lower() else 0,
            1 if 'altered consciousness' in patient_data.get('symptoms', '').lower() else 0,
            1 if 'severe bleeding' in patient_data.get('symptoms', '').lower() else 0,
            patient_data.get('pain_score', 5),
            patient_data.get('symptom_duration_days', 1),
            len(patient_data.get('medical_history', [])),
            patient_data.get('symptom_severity', 2)
        ]
    
    def _rule_based_assessment(self, patient_data):
        """Fallback rule-based triage assessment"""
        # Critical conditions
        if (patient_data.get('spo2', 100) < 85 or
            patient_data.get('systolic_bp', 120) < 70 or
            'severe bleeding' in patient_data.get('symptoms', '').lower() or
            'altered consciousness' in patient_data.get('symptoms', '').lower()):
            return 'EMERGENCY'
        
        # High priority conditions
        if (patient_data.get('temperature', 36.5) > 39.0 or
            patient_data.get('heart_rate', 80) > 120 or
            patient_data.get('pain_score', 0) >= 8 or
            'chest pain' in patient_data.get('symptoms', '').lower()):
            return 'EMERGENCY'
        
        # Moderate conditions
        if (patient_data.get('temperature', 36.5) > 38.0 or
            patient_data.get('pain_score', 0) >= 5):
            return 'OPD'
        
        return 'TELEMEDICINE'
    
    def _calculate_urgency_score(self, patient_data):
        """Calculate urgency score based on vital signs and symptoms"""
        score = 0.0
        
        # Vital signs scoring
        temp = patient_data.get('temperature', 36.5)
        if temp > 39.0: score += 0.3
        elif temp > 38.0: score += 0.2
        elif temp < 35.0: score += 0.3
        
        hr = patient_data.get('heart_rate', 80)
        if hr > 120: score += 0.2
        elif hr < 50: score += 0.2
        
        spo2 = patient_data.get('spo2', 98)
        if spo2 < 90: score += 0.3
        elif spo2 < 95: score += 0.2
        
        bp_sys = patient_data.get('systolic_bp', 120)
        if bp_sys > 180 or bp_sys < 80: score += 0.2
        
        # Symptom scoring
        pain_score = patient_data.get('pain_score', 0)
        score += pain_score / 30.0  # Scale 0-10 to 0-0.33
        
        # Critical symptoms
        symptoms = patient_data.get('symptoms', '').lower()
        if 'chest pain' in symptoms: score += 0.2
        if 'shortness of breath' in symptoms: score += 0.2
        if 'severe bleeding' in symptoms: score += 0.4
        if 'altered consciousness' in symptoms: score += 0.4
        
        return min(score, 1.0)
    
    def _determine_department(self, patient_data, triage_category):
        """Determine recommended department"""
        symptoms = patient_data.get('symptoms', '').lower()
        
        if triage_category == 'EMERGENCY':
            if 'chest pain' in symptoms or 'heart' in symptoms:
                return 'Cardiology Emergency'
            elif 'shortness of breath' in symptoms:
                return 'Pulmonology Emergency'
            elif 'altered consciousness' in symptoms:
                return 'Neurology Emergency'
            else:
                return 'Emergency Department'
        elif triage_category == 'OPD':
            return 'Outpatient Department'
        else:
            return 'Telemedicine Consultation'
    
    def _identify_risk_factors(self, patient_data):
        """Identify patient risk factors"""
        risk_factors = []
        
        age = patient_data.get('age', 0)
        if age > 65:
            risk_factors.append('Elderly patient (>65 years)')
        
        if patient_data.get('temperature', 36.5) > 38.5:
            risk_factors.append('High fever')
        
        if patient_data.get('spo2', 98) < 95:
            risk_factors.append('Low oxygen saturation')
        
        if patient_data.get('pain_score', 0) >= 8:
            risk_factors.append('Severe pain')
        
        medical_history = patient_data.get('medical_history', [])
        if len(medical_history) > 2:
            risk_factors.append('Multiple comorbidities')
        
        return risk_factors
    
    def _generate_recommendations(self, patient_data, triage_category):
        """Generate care recommendations"""
        recommendations = []
        
        if triage_category == 'EMERGENCY':
            recommendations.append('Immediate medical attention required')
            recommendations.append('Monitor vital signs continuously')
            if patient_data.get('spo2', 98) < 95:
                recommendations.append('Administer oxygen therapy')
        
        elif triage_category == 'OPD':
            recommendations.append('Schedule outpatient consultation')
            recommendations.append('Monitor symptoms and return if worsening')
        
        else:
            recommendations.append('Telemedicine consultation recommended')
            recommendations.append('Self-monitoring at home')
        
        return recommendations
    
    def _estimate_wait_time(self, triage_category):
        """Estimate wait time based on triage category"""
        wait_times = {
            'EMERGENCY': '0-15 minutes',
            'OPD': '30-60 minutes',
            'TELEMEDICINE': '5-30 minutes'
        }
        return wait_times.get(triage_category, '30-60 minutes')
    
    def _emergency_fallback(self, patient_data, error):
        """Emergency fallback response when system fails"""
        return {
            'patient_id': patient_data.get('patient_id', 'Unknown'),
            'triage_category': 'EMERGENCY',
            'urgency_score': 1.0,
            'confidence': 0.5,
            'vital_signs': patient_data.get('vitals', {}),
            'recommended_department': 'Emergency Department',
            'risk_factors': ['System error - manual assessment required'],
            'recommendations': ['Immediate manual triage assessment required'],
            'wait_time_estimate': '0-15 minutes',
            'system_error': error
        }

# Global instance for the backend
triage_agent = TriageAgent()

def assess_patient(patient_data):
    """Main function to be called from backend"""
    return triage_agent.assess_patient(patient_data)