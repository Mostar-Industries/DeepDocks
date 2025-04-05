"""
DeepCAL++ Predictor Module
This module contains ML-based prediction functionality for logistics performance
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Union, Tuple
from datetime import datetime, timedelta
import os
import json

# Path to training data
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'shipments_cleaned.json')

class DeepCALPredictor:
    """
    ML-based predictor for logistics performance metrics
    """
    def __init__(self):
        """Initialize the predictor with historical data"""
        self.model_ready = False
        self.historical_data = None
        self.region_factors = {
            "West Africa": {
                "delay_factor": 1.15,
                "cost_factor": 1.05,
                "reliability_factor": 0.95
            },
            "East Africa": {
                "delay_factor": 1.10,
                "cost_factor": 1.10,
                "reliability_factor": 0.97
            },
            "North Africa": {
                "delay_factor": 1.05,
                "cost_factor": 1.15,
                "reliability_factor": 0.98
            },
            "Southern Africa": {
                "delay_factor": 1.08,
                "cost_factor": 1.12,
                "reliability_factor": 0.96
            },
            "Central Africa": {
                "delay_factor": 1.20,
                "cost_factor": 1.18,
                "reliability_factor": 0.92
            }
        }
        
        # Load data if available
        self._load_data()
    
    def _load_data(self):
        """Load historical shipment data"""
        try:
            if os.path.exists(DATA_PATH):
                with open(DATA_PATH, 'r') as f:
                    self.historical_data = json.load(f)
                self.model_ready = True
            else:
                # Create dummy data for demonstration
                self._create_dummy_data()
                self.model_ready = True
        except Exception as e:
            print(f"Warning: Could not load predictor data: {e}")
            self._create_dummy_data()
    
    def _create_dummy_data(self):
        """Create dummy historical data for demonstration"""
        self.historical_data = {
            "shipments": []
        }
        
        # Generate 100 random shipments
        forwarders = ["AfricaLogistics", "GlobalFreight", "ExpressShip", 
                      "TransAfrica", "FastCargo", "AfricaLink"]
        
        origins = {
            "Lagos, Nigeria": "West Africa",
            "Nairobi, Kenya": "East Africa",
            "Cairo, Egypt": "North Africa",
            "Johannesburg, South Africa": "Southern Africa",
            "Accra, Ghana": "West Africa",
            "Addis Ababa, Ethiopia": "East Africa",
            "Casablanca, Morocco": "North Africa",
            "Kinshasa, DRC": "Central Africa"
        }
        
        destinations = list(origins.keys())
        cargo_types = ["General Merchandise", "Electronics", "Perishable Goods", 
                       "Hazardous Materials", "Machinery", "Textiles"]
        
        np.random.seed(42)  # For reproducibility
        
        base_date = datetime.now() - timedelta(days=365)
        
        for i in range(100):
            origin = np.random.choice(list(origins.keys()))
            dest = np.random.choice(destinations)
            
            # Ensure origin and destination are different
            while dest == origin:
                dest = np.random.choice(destinations)
            
            forwarder = np.random.choice(forwarders)
            cargo_type = np.random.choice(cargo_types)
            
            # Generate random values
            weight = np.random.uniform(100, 5000)
            value = np.random.uniform(1000, 50000)
            
            # Base metrics with some randomness
            if forwarder == "AfricaLogistics":
                base_cost = 1200
                base_time = 14
                base_reliability = 0.85
            elif forwarder == "GlobalFreight":
                base_cost = 950
                base_time = 18
                base_reliability = 0.78
            elif forwarder == "ExpressShip":
                base_cost = 1450
                base_time = 10
                base_reliability = 0.92
            else:
                base_cost = np.random.uniform(900, 1500)
                base_time = np.random.uniform(8, 20)
                base_reliability = np.random.uniform(0.75, 0.95)
            
            # Apply region factors
            origin_region = origins[origin]
            dest_region = origins[dest]
            
            region_factor = (
                self.region_factors[origin_region]["delay_factor"] * 
                self.region_factors[dest_region]["delay_factor"]
            ) / 2
            
            cost_factor = (
                self.region_factors[origin_region]["cost_factor"] * 
                self.region_factors[dest_region]["cost_factor"]
            ) / 2
            
            reliability_factor = (
                self.region_factors[origin_region]["reliability_factor"] * 
                self.region_factors[dest_region]["reliability_factor"]
            ) / 2
            
            # Calculate final metrics with some randomness
            cost = base_cost * cost_factor * (weight / 1000) * np.random.uniform(0.9, 1.1)
            time = base_time * region_factor * np.random.uniform(0.9, 1.1)
            reliability = base_reliability * reliability_factor * np.random.uniform(0.95, 1.05)
            reliability = min(reliability, 0.99)  # Cap at 0.99
            
            # Generate dates
            ship_date = base_date + timedelta(days=i)
            expected_delivery = ship_date + timedelta(days=int(time))
            
            # Add randomness to actual delivery (50% on time, 40% late, 10% early)
            rand_val = np.random.random()
            if rand_val < 0.5:  # On time
                actual_delivery = expected_delivery
                on_time = True
            elif rand_val < 0.9:  # Late
                delay = np.random.randint(1, 5)
                actual_delivery = expected_delivery + timedelta(days=delay)
                on_time = False
            else:  # Early
                early = np.random.randint(1, 3)
                actual_delivery = expected_delivery - timedelta(days=early)
                on_time = True
            
            self.historical_data["shipments"].append({
                "id": f"SHP{i+1000}",
                "forwarder": forwarder,
                "origin": origin,
                "destination": dest,
                "cargo_type": cargo_type,
                "weight_kg": float(weight),
                "value_usd": float(value),
                "cost_usd": float(cost),
                "expected_delivery_days": float(time),
                "ship_date": ship_date.strftime("%Y-%m-%d"),
                "expected_delivery_date": expected_delivery.strftime("%Y-%m-%d"),
                "actual_delivery_date": actual_delivery.strftime("%Y-%m-%d"),
                "on_time": on_time,
                "tracking_provided": np.random.random() > 0.3  # 70% have tracking
            })
    
    def predict_delivery_time(
        self, 
        origin: str, 
        destination: str, 
        forwarder: str, 
        weight: float, 
        cargo_type: str
    ) -> Dict[str, Any]:
        """
        Predict delivery time for a given shipment
        
        Args:
            origin: Origin location
            destination: Destination location
            forwarder: Logistics forwarder name
            weight: Shipment weight in kg
            cargo_type: Type of cargo
            
        Returns:
            Dictionary with predicted delivery time and confidence
        """
        if not self.model_ready or not self.historical_data:
            return {
                "predicted_days": None,
                "confidence": 0,
                "range_low": None,
                "range_high": None,
                "error": "Predictor not ready or missing data"
            }
        
        # Find similar shipments
        similar_shipments = self._find_similar_shipments(
            origin, destination, forwarder, weight, cargo_type)
        
        if not similar_shipments:
            # Fall back to baseline prediction
            return self._baseline_prediction(origin, destination, forwarder, weight)
        
        # Calculate statistics
        delivery_times = [s.get("expected_delivery_days", 0) for s in similar_shipments]
        actual_vs_expected = []
        
        for s in similar_shipments:
            if all(k in s for k in ["actual_delivery_date", "expected_delivery_date"]):
                expected = datetime.strptime(s["expected_delivery_date"], "%Y-%m-%d")
                actual = datetime.strptime(s["actual_delivery_date"], "%Y-%m-%d")
                days_diff = (actual - expected).days
                actual_vs_expected.append(days_diff)
        
        # Calculate prediction
        if delivery_times:
            mean_time = np.mean(delivery_times)
            std_time = np.std(delivery_times) if len(delivery_times) > 1 else 2
            
            # Adjust for historical accuracy
            if actual_vs_expected:
                mean_diff = np.mean(actual_vs_expected)
                adjusted_time = mean_time + mean_diff
            else:
                adjusted_time = mean_time
            
            # Calculate confidence (inverse of coefficient of variation)
            if mean_time > 0 and std_time > 0:
                cv = std_time / mean_time
                confidence = max(0, min(1, 1 - cv))
            else:
                confidence = 0.5
            
            return {
                "predicted_days": round(adjusted_time, 1),
                "confidence": round(confidence, 2),
                "range_low": round(max(1, adjusted_time - std_time), 1),
                "range_high": round(adjusted_time + std_time, 1),
                "sample_size": len(delivery_times)
            }
        else:
            return self._baseline_prediction(origin, destination, forwarder, weight)
    
    def predict_reliability(
        self, 
        forwarder: str, 
        origin: str, 
        destination: str
    ) -> Dict[str, Any]:
        """
        Predict reliability score for a given forwarder and route
        
        Args:
            forwarder: Logistics forwarder name
            origin: Origin location
            destination: Destination location
            
        Returns:
            Dictionary with predicted reliability and confidence
        """
        if not self.model_ready or not self.historical_data:
            return {
                "reliability_score": 0.8,  # Default
                "confidence": 0,
                "error": "Predictor not ready or missing data"
            }
        
        # Find shipments by this forwarder on this route
        relevant_shipments = []
        
        for shipment in self.historical_data.get("shipments", []):
            if (shipment.get("forwarder") == forwarder and
                shipment.get("origin") == origin and
                shipment.get("destination") == destination):
                relevant_shipments.append(shipment)
        
        # If we have enough data, calculate reliability
        if len(relevant_shipments) >= 3:
            on_time_count = sum(1 for s in relevant_shipments if s.get("on_time", False))
            reliability = on_time_count / len(relevant_shipments)
            
            # Confidence based on sample size
            confidence = min(0.95, 0.5 + 0.05 * len(relevant_shipments))
            
            return {
                "reliability_score": round(reliability, 2),
                "confidence": round(confidence, 2),
                "sample_size": len(relevant_shipments)
            }
        
        # Fall back to forwarder-wide data
        forwarder_shipments = [s for s in self.historical_data.get("shipments", []) 
                              if s.get("forwarder") == forwarder]
        
        if forwarder_shipments:
            on_time_count = sum(1 for s in forwarder_shipments if s.get("on_time", False))
            reliability = on_time_count / len(forwarder_shipments)
            
            # Lower confidence due to less route specificity
            confidence = min(0.7, 0.3 + 0.02 * len(forwarder_shipments))
            
            return {
                "reliability_score": round(reliability, 2),
                "confidence": round(confidence, 2),
                "sample_size": len(forwarder_shipments),
                "note": "Based on forwarder's overall performance (limited route-specific data)"
            }
        
        # Last resort: baseline prediction
        return {
            "reliability_score": 0.8,
            "confidence": 0.3,
            "note": "Based on general market averages (no historical data)"
        }
    
    def _find_similar_shipments(
        self, 
        origin: str, 
        destination: str, 
        forwarder: str, 
        weight: float, 
        cargo_type: str
    ) -> List[Dict[str, Any]]:
        """Find similar shipments in historical data"""
        if not self.historical_data:
            return []
        
        similar_shipments = []
        
        for shipment in self.historical_data.get("shipments", []):
            # Route match is most important
            if (shipment.get("origin") == origin and 
                shipment.get("destination") == destination):
                
                # Exact forwarder match
                if shipment.get("forwarder") == forwarder:
                    similar_shipments.append(shipment)
            
            # Secondary match: same forwarder, similar route
            elif (shipment.get("forwarder") == forwarder and 
                  (shipment.get("origin") == origin or 
                   shipment.get("destination") == destination)):
                similar_shipments.append(shipment)
        
        return similar_shipments
    
    def _baseline_prediction(
        self, 
        origin: str, 
        destination: str, 
        forwarder: str, 
        weight: float
    ) -> Dict[str, Any]:
        """
        Generate baseline prediction when no historical data is available
        
        Args:
            origin: Origin location
            destination: Destination location
            forwarder: Forwarder name
            weight: Shipment weight in kg
            
        Returns:
            Baseline prediction
        """
        # Estimate distance factor based on locations
        # This is a simplified approach for demonstration
        regions = {
            "Lagos, Nigeria": "West Africa",
            "Nairobi, Kenya": "East Africa",
            "Cairo, Egypt": "North Africa",
            "Johannesburg, South Africa": "Southern Africa",
            "Accra, Ghana": "West Africa",
            "Addis Ababa, Ethiopia": "East Africa",
            "Casablanca, Morocco": "North Africa",
            "Kinshasa, DRC": "Central Africa",
            "Dar es Salaam, Tanzania": "East Africa",
            "Dakar, Senegal": "West Africa",
            "Khartoum, Sudan": "North Africa",
            "Algiers, Algeria": "North Africa",
            "Tunis, Tunisia": "North Africa",
            "Lusaka, Zambia": "Southern Africa"
        }
        
        # Default to region if location not in dictionary
        origin_region = "Unknown Region"
        dest_region = "Unknown Region"
        
        for location, region in regions.items():
            if location in origin:
                origin_region = region
            if location in destination:
                dest_region = region
        
        # Base delivery times by forwarder
        forwarder_base_times = {
            "AfricaLogistics": 14,
            "GlobalFreight": 18,
            "ExpressShip": 10,
            "TransAfrica": 15,
            "FastCargo": 12,
            "AfricaLink": 16
        }
        
        # Default if forwarder not known
        base_time = forwarder_base_times.get(forwarder, 15)
        
        # Adjust for regions
        if origin_region == dest_region:
            region_factor = 0.8  # Same region is faster
        elif (origin_region in ["North Africa", "West Africa"] and 
              dest_region in ["North Africa", "West Africa"]):
            region_factor = 0.9  # Neighboring regions
        elif (origin_region in ["East Africa", "Southern Africa"] and 
              dest_region in ["East Africa", "Southern Africa"]):
            region_factor = 0.9  # Neighboring regions
        else:
            region_factor = 1.2  # Cross-continental
        
        # Adjust for weight
        weight_factor = 1.0
        if weight > 1000:
            weight_factor = 1.1
        if weight > 3000:
            weight_factor = 1.2
        
        # Calculate estimated delivery time
        delivery_time = base_time * region_factor * weight_factor
        
        return {
            "predicted_days": round(delivery_time, 1),
            "confidence": 0.5,  # Lower confidence for baseline prediction
            "range_low": round(delivery_time * 0.8, 1),
            "range_high": round(delivery_time * 1.2, 1),
            "note": "Based on general estimates (no historical data)"
        }

# Create singleton instance
predictor = DeepCALPredictor()

def predict_delivery(
    origin: str, 
    destination: str, 
    forwarder: str, 
    weight: float, 
    cargo_type: str = "General Merchandise"
) -> Dict[str, Any]:
    """
    Predict delivery time for a shipment
    
    Args:
        origin: Origin location
        destination: Destination location
        forwarder: Logistics forwarder
        weight: Shipment weight in kg
        cargo_type: Type of cargo
        
    Returns:
        Prediction results
    """
    return predictor.predict_delivery_time(
        origin, destination, forwarder, weight, cargo_type)

def predict_forwarder_reliability(
    forwarder: str, 
    origin: str, 
    destination: str
) -> Dict[str, Any]:
    """
    Predict reliability for a forwarder on a specific route
    
    Args:
        forwarder: Logistics forwarder
        origin: Origin location
        destination: Destination location
        
    Returns:
        Reliability prediction
    """
    return predictor.predict_reliability(forwarder, origin, destination)

