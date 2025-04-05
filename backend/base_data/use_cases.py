"""
DeepCAL++ Use Cases Module
This module provides example use cases for the DeepCAL++ system
"""
import os
import json
from typing import Dict, List, Any, Union, Optional
from .data_loader import get_data_loader
from .data_analyzer import get_data_analyzer

class DeepTrackUseCases:
    """
    Use cases for DeepCAL++ system
    Provides example scenarios and workflows using the deeptrack_corex1.csv data
    """
    
    def __init__(self):
        """Initialize the use cases"""
        self.loader = get_data_loader()
        self.analyzer = get_data_analyzer()
        self.data = self.loader.get_data()
    
    def get_emergency_shipment_recommendation(
        self, 
        origin: str, 
        destination: str,
        weight_kg: float,
        volume_cbm: float,
        item_category: str,
        emergency_grade: str = "Grade 1"
    ) -> Dict[str, Any]:
        """
        Get carrier recommendations for emergency shipments
        
        Args:
            origin: Origin country
            destination: Destination country
            weight_kg: Shipment weight in kg
            volume_cbm: Shipment volume in cubic meters
            item_category: Category of items being shipped
            emergency_grade: Emergency grade (Grade 1-5)
            
        Returns:
            Dictionary with recommendations
        """
        # Get route recommendations
        route_key = f"{origin} to {destination}"
        route_recommendations = self.analyzer.generate_route_recommendations()
        
        # Check if we have recommendations for this route
        if route_key not in route_recommendations:
            return {
                "success": False,
                "error": f"No data available for route from {origin} to {destination}",
                "alternative_routes": list(route_recommendations.keys())
            }
        
        # Get recommendations for this route
        recommendations = route_recommendations[route_key]
        
        # For emergency shipments, prioritize delivery time and reliability
        # Adjust weights based on emergency grade
        if emergency_grade == "Grade 1":
            # Highest emergency - speed is critical
            weights = {"reliability": 0.3, "time": 0.6, "cost": 0.05, "experience": 0.05}
        elif emergency_grade == "Grade 2":
            # High emergency - speed is very important
            weights = {"reliability": 0.4, "time": 0.5, "cost": 0.05, "experience": 0.05}
        elif emergency_grade == "Grade 3":
            # Moderate emergency - balance speed and reliability
            weights = {"reliability": 0.45, "time": 0.4, "cost": 0.1, "experience": 0.05}
        elif emergency_grade == "Grade 4":
            # Low emergency - reliability is more important than speed
            weights = {"reliability": 0.5, "time": 0.3, "cost": 0.15, "experience": 0.05}
        else:
            # No emergency - balanced approach
            weights = {"reliability": 0.4, "time": 0.2, "cost": 0.3, "experience": 0.1}
        
        # Recalculate scores with emergency weights
        for carrier in recommendations:
            carrier['emergency_score'] = (
                weights["reliability"] * carrier['component_scores']["reliability"] +
                weights["time"] * carrier['component_scores']["time"] +
                weights["cost"] * carrier['component_scores']["cost"] +
                weights["experience"] * carrier['component_scores']["experience"]
            )
        
        # Sort by emergency score
        emergency_ranked = sorted(recommendations, key=lambda x: -x['emergency_score'])
        
        # Get top 3 recommendations
        top_recommendations = emergency_ranked[:3]
        
        # Create response
        response = {
            "success": True,
            "origin": origin,
            "destination": destination,
            "emergency_grade": emergency_grade,
            "weight_kg": weight_kg,
            "volume_cbm": volume_cbm,
            "item_category": item_category,
            "recommendations": top_recommendations,
            "weights_used": weights,
            "explanation": f"For {emergency_grade} emergency shipments, we prioritize {list(weights.keys())[0]} and {list(weights.keys())[1]}."
        }
        
        return response
    
    def get_cost_optimized_recommendation(
        self, 
        origin: str, 
        destination: str,
        weight_kg: float,
        volume_cbm: float,
        item_category: str
    ) -> Dict[str, Any]:
        """
        Get carrier recommendations optimized for cost
        
        Args:
            origin: Origin country
            destination: Destination country
            weight_kg: Shipment weight in kg
            volume_cbm: Shipment volume in cubic meters
            item_category: Category of items being shipped
            
        Returns:
            Dictionary with recommendations
        """
        # Get route recommendations
        route_key = f"{origin} to {destination}"
        route_recommendations = self.analyzer.generate_route_recommendations()
        
        # Check if we have recommendations for this route
        if route_key not in route_recommendations:
            return {
                "success": False,
                "error": f"No data available for route from {origin} to {destination}",
                "alternative_routes": list(route_recommendations.keys())
            }
        
        # Get recommendations for this route
        recommendations = route_recommendations[route_key]
        
        # For cost-optimized shipments, prioritize cost
        weights = {"reliability": 0.2, "time": 0.1, "cost": 0.65, "experience": 0.05}
        
        # Recalculate scores with cost-optimized weights
        for carrier in recommendations:
            carrier['cost_optimized_score'] = (
                weights["reliability"] * carrier['component_scores']["reliability"] +
                weights["time"] * carrier['component_scores']["time"] +
                weights["cost"] * carrier['component_scores']["cost"] +
                weights["experience"] * carrier['component_scores']["experience"]
            )
        
        # Sort by cost-optimized score
        cost_ranked = sorted(recommendations, key=lambda x: -x['cost_optimized_score'])
        
        # Get top 3 recommendations
        top_recommendations = cost_ranked[:3]
        
        # Create response
        response = {
            "success": True,
            "origin": origin,
            "destination": destination,
            "weight_kg": weight_kg,
            "volume_cbm": volume_cbm,
            "item_category": item_category,
            "recommendations": top_recommendations,
            "weights_used": weights,
            "explanation": "For cost-optimized shipments, we prioritize carriers with the lowest costs while maintaining acceptable reliability and delivery times."
        }
        
        return response
    
    def get_balanced_recommendation(
        self, 
        origin: str, 
        destination: str,
        weight_kg: float,
        volume_cbm: float,
        item_category: str,
        reliability_importance: float = 0.4,
        time_importance: float = 0.3,
        cost_importance: float = 0.3
    ) -> Dict[str, Any]:
        """
        Get carrier recommendations with custom balance of factors
        
        Args:
            origin: Origin country
            destination: Destination country
            weight_kg: Shipment weight in kg
            volume_cbm: Shipment volume in cubic meters
            item_category: Category of items being shipped
            reliability_importance: Importance of reliability (0-1)
            time_importance: Importance of delivery time (0-1)
            cost_importance: Importance of cost (0-1)
            
        Returns:
            Dictionary with recommendations
        """
        # Normalize importance values
        total = reliability_importance + time_importance + cost_importance
        reliability_weight = reliability_importance / total
        time_weight = time_importance / total
        cost_weight = cost_importance / total
        
        # Get route recommendations
        route_key = f"{origin} to {destination}"
        route_recommendations = self.analyzer.generate_route_recommendations()
        
        # Check if we have recommendations for this route
        if route_key not in route_recommendations:
            return {
                "success": False,
                "error": f"No data available for route from {origin} to {destination}",
                "alternative_routes": list(route_recommendations.keys())
            }
        
        # Get recommendations for this route
        recommendations = route_recommendations[route_key]
        
        # Use custom weights
        weights = {
            "reliability": reliability_weight,
            "time": time_weight,
            "cost": cost_weight,
            "experience": 0.05  # Fixed small weight for experience
        }
        
        # Normalize to ensure weights sum to 1
        total_weight = sum(weights.values())
        for key in weights:
            weights[key] /= total_weight
        
        # Recalculate scores with custom weights
        for carrier in recommendations:
            carrier['custom_score'] = (
                weights["reliability"] * carrier['component_scores']["reliability"] +
                weights["time"] * carrier['component_scores']["time"] +
                weights["cost"] * carrier['component_scores']["cost"] +
                weights["experience"] * carrier['component_scores']["experience"]
            )
        
        # Sort by custom score
        custom_ranked = sorted(recommendations, key=lambda x: -x['custom_score'])
        
        # Get top 3 recommendations
        top_recommendations = custom_ranked[:3]
        
        # Create response
        response = {
            "success": True,
            "origin": origin,
            "destination": destination,
            "weight_kg": weight_kg,
            "volume_cbm": volume_cbm,
            "item_category": item_category,
            "recommendations": top_recommendations,
            "weights_used": weights,
            "explanation": f"Recommendations are based on your custom preferences: {reliability_weight:.1%} reliability, {time_weight:.1%} delivery time, and {cost_weight:.1%} cost."
        }
        
        return response
    
    def get_all_use_cases(self) -> Dict[str, Any]:
        """Get all use case examples"""
        # Get available routes
        route_recommendations = self.analyzer.generate_route_recommendations()
        available_routes = list(route_recommendations.keys())
        
        # If no routes available, return empty use cases
        if not available_routes:
            return {"use_cases": []}
        
        # Select a sample route
        sample_route = available_routes[0]
        origin, destination = sample_route.split(" to ")
        
        # Create use cases
        use_cases = [
            {
                "title": "Emergency Medical Supply Shipment",
                "description": "A humanitarian organization needs to ship emergency medical supplies as quickly as possible",
                "scenario": {
                    "origin": origin,
                    "destination": destination,
                    "weight_kg": 200,
                    "volume_cbm": 1.0,
                    "item_category": "Medical Supplies",
                    "emergency_grade": "Grade 1"
                },
                "recommendation": self.get_emergency_shipment_recommendation(
                    origin, destination, 200, 1.0, "Medical Supplies", "Grade 1"
                )
            },
            {
                "title": "Cost-Optimized Bulk Shipment",
                "description": "A manufacturing company needs to ship non-urgent raw materials at the lowest possible cost",
                "scenario": {
                    "origin": origin,
                    "destination": destination,
                    "weight_kg": 5000,
                    "volume_cbm": 15.0,
                    "item_category": "Raw Materials"
                },
                "recommendation": self.get_cost_optimized_recommendation(
                    origin, destination, 5000, 15.0, "Raw Materials"
                )
            },
            {
                "title": "Balanced Shipment with Custom Preferences",
                "description": "A company needs to ship products with a balance of reliability, time, and cost",
                "scenario": {
                    "origin": origin,
                    "destination": destination,
                    "weight_kg": 800,
                    "volume_cbm": 4.5,
                    "item_category": "Electronics",
                    "reliability_importance": 0.5,
                    "time_importance": 0.3,
                    "cost_importance": 0.2
                },
                "recommendation": self.get_balanced_recommendation(
                    origin, destination, 800, 4.5, "Electronics", 0.5, 0.3, 0.2
                )
            }
        ]
        
        return {"use_cases": use_cases}
    
    def export_use_cases_to_json(self, filepath: str) -> bool:
        """Export use cases to JSON file"""
        try:
            use_cases = self.get_all_use_cases()
            
            with open(filepath, 'w') as f:
                json.dump(use_cases, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error exporting use cases to JSON: {e}")
            return False

# Create singleton instance
use_cases = DeepTrackUseCases()

def get_use_cases() -> DeepTrackUseCases:
    """Get the use cases instance"""
    return use_cases

# Example usage
if __name__ == "__main__":
    uc = get_use_cases()
    
    # Export use cases to JSON
    uc.export_use_cases_to_json('use_cases.json')

