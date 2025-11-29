#!/usr/bin/env python3
"""
Test script for the Triage API endpoint
"""

import requests
import json

def test_triage_endpoint():
    """Test the triage assessment endpoint"""
    url = "http://127.0.0.1:5000/api/triage/assess"
    
    # Test patient data
    test_data = {
        "patient_id": "P001",
        "age": 45,
        "chief_complaint": "chest pain",
        "vitals": {
            "systolic_bp": 140,
            "diastolic_bp": 90,
            "heart_rate": 95,
            "temperature": 98.6,
            "respiratory_rate": 18,
            "oxygen_saturation": 97
        },
        "symptoms": {
            "chest_pain": True,
            "shortness_of_breath": True,
            "altered_consciousness": False,
            "severe_bleeding": False
        },
        "pain_score": 7,
        "symptom_duration_days": 1,
        "comorbidities_count": 2,
        "priority": "high"
    }
    
    try:
        print("Testing Triage API endpoint...")
        print(f"URL: {url}")
        print(f"Patient data: {json.dumps(test_data, indent=2)}")
        print("\n" + "="*50)
        
        response = requests.post(url, json=test_data, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ SUCCESS! Triage agent response:")
            print(json.dumps(result, indent=2))
            
            # Check if this looks like real ML output vs mock data
            if "triage_recommendation" in result and "confidence" in result:
                print("\n🎯 This appears to be REAL triage agent output!")
                print(f"Triage: {result['triage_recommendation']}")
                print(f"Confidence: {result['confidence']}%")
                if "ml_prediction" in result:
                    print("✅ ML model prediction is being used")
                if "rule_based_recommendation" in result:
                    print("✅ Rule-based fallback is also available")
            else:
                print("\n⚠️ Response format might be mock data")
        else:
            print(f"\n❌ ERROR: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to Flask server on port 5000")
        print("Make sure the Flask backend is running")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_triage_endpoint()