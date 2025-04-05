"""
DeepCAL++ Data Analyzer Module
This module provides functionality to analyze the base data from deeptrack_corex1.csv
"""
import os
import pandas as pd
import numpy as np
import json
from typing import Dict, List, Any, Union, Optional
from .data_loader import get_data_loader

class DeepTrackDataAnalyzer:
    """
    Data analyzer for DeepCAL++ base data
    Provides methods to analyze and extract insights from the deeptrack_corex1.csv data
    """
    
    def __init__(self):
        """Initialize the data analyzer"""
        self.loader = get_data_loader()
        self.data = self.loader.get_data()
    
    def analyze_carrier_performance(self) -> Dict[str, Any]:
        """Analyze performance metrics for all carriers"""
        carriers = {}
        
        # Get unique carriers from the carrier column
        unique_carriers = self.data['carrier'].dropna().unique()
        
        for carrier in unique_carriers:
            carrier_data = self.data[self.data['carrier'] == carrier]
            
            # Skip if no data
            if len(carrier_data) == 0:
                continue
            
            # Calculate performance metrics
            total_shipments = len(carrier_data)
            delivered = carrier_data['delivery_status'] == 'Delivered'
            delivered_shipments = delivered.sum()
            delivery_rate = delivered_shipments / total_shipments if total_shipments > 0 else 0
            
            # Calculate average cost
            avg_cost = carrier_data['carrier_cost'].mean()
            
            # Calculate average delivery time (if data available)
            avg_delivery_time = None
            if 'date_of_collection' in carrier_data.columns and 'date_of_arrival_destination' in carrier_data.columns:
                try:
                    # Convert to datetime if they're strings
                    if carrier_data['date_of_collection'].dtype == 'object':
                        collection_dates = pd.to_datetime(carrier_data['date_of_collection'], errors='coerce')
                    else:
                        collection_dates = carrier_data['date_of_collection']
                        
                    if carrier_data['date_of_arrival_destination'].dtype == 'object':
                        arrival_dates = pd.to_datetime(carrier_data['date_of_arrival_destination'], errors='coerce')
                    else:
                        arrival_dates = carrier_data['date_of_arrival_destination']
                    
                    # Calculate delivery times
                    delivery_times = (arrival_dates - collection_dates).dt.days
                    avg_delivery_time = delivery_times.mean()
                except Exception as e:
                    print(f"Error calculating delivery time for {carrier}: {e}")
            
            carriers[carrier] = {
                "total_shipments": total_shipments,
                "delivered_shipments": int(delivered_shipments),
                "delivery_rate": float(delivery_rate),
                "average_cost": float(avg_cost) if not pd.isna(avg_cost) else None,
                "average_delivery_time_days": float(avg_delivery_time) if avg_delivery_time is not None and not pd.isna(avg_delivery_time) else None
            }
        
        return carriers
    
    def analyze_routes(self) -> Dict[str, Any]:
        """Analyze statistics for all routes"""
        routes = {}
        
        # Get unique routes
        route_pairs = self.data[['origin_country', 'destination_country']].drop_duplicates()
        
        for _, row in route_pairs.iterrows():
            origin = row['origin_country']
            destination = row['destination_country']
            
            route_key = f"{origin} to {destination}"
            
            route_data = self.data[
                (self.data['origin_country'] == origin) & 
                (self.data['destination_country'] == destination)
            ]
            
            # Skip if no data
            if len(route_data) == 0:
                continue
            
            # Calculate route statistics
            total_shipments = len(route_data)
            avg_weight = route_data['weight_kg'].mean()
            avg_volume = route_data['volume_cbm'].mean()
            
            # Get carrier distribution
            carrier_counts = route_data['carrier'].value_counts().to_dict()
            
            # Calculate average costs by carrier
            carrier_costs = {}
            for carrier in carrier_counts.keys():
                carrier_route_data = route_data[route_data['carrier'] == carrier]
                avg_carrier_cost = carrier_route_data['carrier_cost'].mean()
                carrier_costs[carrier] = float(avg_carrier_cost) if not pd.isna(avg_carrier_cost) else None
            
            routes[route_key] = {
                "origin": origin,
                "destination": destination,
                "total_shipments": total_shipments,
                "average_weight_kg": float(avg_weight) if not pd.isna(avg_weight) else None,
                "average_volume_cbm": float(avg_volume) if not pd.isna(avg_volume) else None,
                "carrier_distribution": carrier_counts,
                "average_costs_by_carrier": carrier_costs
            }
        
        return routes
    
    def analyze_item_categories(self) -> Dict[str, Any]:
        """Analyze statistics for item categories"""
        categories = {}
        
        # Get unique item categories
        unique_categories = self.data['item_category'].dropna().unique()
        
        for category in unique_categories:
            category_data = self.data[self.data['item_category'] == category]
            
            # Skip if no data
            if len(category_data) == 0:
                continue
            
            # Calculate category statistics
            total_shipments = len(category_data)
            avg_weight = category_data['weight_kg'].mean()
            avg_volume = category_data['volume_cbm'].mean()
            
            # Get carrier distribution
            carrier_counts = category_data['carrier'].value_counts().to_dict()
            
            # Calculate average costs
            avg_cost = category_data['carrier_cost'].mean()
            
            categories[category] = {
                "total_shipments": total_shipments,
                "average_weight_kg": float(avg_weight) if not pd.isna(avg_weight) else None,
                "average_volume_cbm": float(avg_volume) if not pd.isna(avg_volume) else None,
                "average_cost": float(avg_cost) if not pd.isna(avg_cost) else None,
                "carrier_distribution": carrier_counts
            }
        
        return categories
    
    def generate_carrier_rankings(self) -> Dict[str, Any]:
        """Generate rankings for carriers based on performance metrics"""
        carrier_performance = self.analyze_carrier_performance()
        
        # Create lists for ranking
        carriers = []
        for carrier, metrics in carrier_performance.items():
            # Skip carriers with insufficient data
            if metrics['total_shipments'] < 3:
                continue
                
            carriers.append({
                "name": carrier,
                "delivery_rate": metrics['delivery_rate'],
                "average_cost": metrics['average_cost'] if metrics['average_cost'] is not None else float('inf'),
                "average_delivery_time": metrics['average_delivery_time_days'] if metrics['average_delivery_time_days'] is not None else float('inf'),
                "total_shipments": metrics['total_shipments']
            })
        
        # Sort by different metrics
        delivery_rate_ranking = sorted(carriers, key=lambda x: (-x['delivery_rate'], x['name']))
        cost_ranking = sorted(carriers, key=lambda x: (x['average_cost'], -x['delivery_rate'], x['name']))
        time_ranking = sorted(carriers, key=lambda x: (x['average_delivery_time'], -x['delivery_rate'], x['name']))
        volume_ranking = sorted(carriers, key=lambda x: (-x['total_shipments'], x['name']))
        
        # Assign ranks
        for i, carrier in enumerate(delivery_rate_ranking):
            carrier['reliability_rank'] = i + 1
            
        for i, carrier in enumerate(cost_ranking):
            carrier['cost_rank'] = i + 1
            
        for i, carrier in enumerate(time_ranking):
            carrier['time_rank'] = i + 1
            
        for i, carrier in enumerate(volume_ranking):
            carrier['volume_rank'] = i + 1
        
        # Calculate overall score (lower is better)
        for carrier in carriers:
            # Use weighted average of ranks
            carrier['overall_score'] = (
                0.4 * carrier['reliability_rank'] +
                0.3 * carrier['cost_rank'] +
                0.2 * carrier['time_rank'] +
                0.1 * carrier['volume_rank']
            )
        
        # Sort by overall score
        overall_ranking = sorted(carriers, key=lambda x: (x['overall_score'], x['name']))
        
        # Assign overall ranks
        for i, carrier in enumerate(overall_ranking):
            carrier['overall_rank'] = i + 1
        
        return {
            "rankings": {
                "overall": overall_ranking,
                "reliability": delivery_rate_ranking,
                "cost": cost_ranking,
                "delivery_time": time_ranking,
                "volume": volume_ranking
            },
            "methodology": {
                "description": "Rankings are based on delivery rate, average cost, average delivery time, and shipment volume",
                "weights": {
                    "reliability": 0.4,
                    "cost": 0.3,
                    "delivery_time": 0.2,
                    "volume": 0.1
                }
            }
        }
    
    def generate_route_recommendations(self) -> Dict[str, List[Dict[str, Any]]]:
        """Generate carrier recommendations for each route"""
        route_analysis = self.analyze_routes()
        carrier_performance = self.analyze_carrier_performance()
        
        recommendations = {}
        
        for route_key, route_data in route_analysis.items():
            origin = route_data['origin']
            destination = route_data['destination']
            
            # Get carriers that have served this route
            route_carriers = list(route_data['carrier_distribution'].keys())
            
            # Create carrier evaluations for this route
            carrier_evaluations = []
            
            for carrier in route_carriers:
                # Skip if carrier not in performance data
                if carrier not in carrier_performance:
                    continue
                
                # Get carrier performance metrics
                performance = carrier_performance[carrier]
                
                # Get carrier cost for this route
                route_cost = route_data['average_costs_by_carrier'].get(carrier)
                
                carrier_evaluations.append({
                    "name": carrier,
                    "delivery_rate": performance['delivery_rate'],
                    "average_cost": route_cost if route_cost is not None else performance['average_cost'],
                    "average_delivery_time": performance['average_delivery_time_days'],
                    "shipment_count": route_data['carrier_distribution'].get(carrier, 0),
                    "total_shipments": performance['total_shipments']
                })
            
            # Skip routes with insufficient data
            if len(carrier_evaluations) < 2:
                continue
            
            # Calculate scores for each carrier (higher is better)
            for carrier in carrier_evaluations:
                # Normalize metrics
                reliability_score = carrier['delivery_rate'] * 100  # 0-100 scale
                
                # Cost score (lower cost = higher score)
                if carrier['average_cost'] is not None and carrier['average_cost'] > 0:
                    min_cost = min([c['average_cost'] for c in carrier_evaluations if c['average_cost'] is not None and c['average_cost'] > 0], default=1)
                    cost_score = min_cost / carrier['average_cost'] * 100
                else:
                    cost_score = 50  # Default middle score
                
                # Time score (lower time = higher score)
                if carrier['average_delivery_time'] is not None and carrier['average_delivery_time'] > 0:
                    min_time = min([c['average_delivery_time'] for c in carrier_evaluations if c['average_delivery_time'] is not None and c['average_delivery_time'] > 0], default=1)
                    time_score = min_time / carrier['average_delivery_time'] * 100
                else:
                    time_score = 50  # Default middle score
                
                # Experience score based on number of shipments on this route
                max_count = max([c['shipment_count'] for c in carrier_evaluations], default=1)
                experience_score = carrier['shipment_count'] / max_count * 100
                
                # Calculate weighted score
                carrier['score'] = (
                    0.4 * reliability_score +
                    0.3 * cost_score +
                    0.2 * time_score +
                    0.1 * experience_score
                )
                
                # Store component scores
                carrier['component_scores'] = {
                    "reliability": reliability_score,
                    "cost": cost_score,
                    "time": time_score,
                    "experience": experience_score
                }
            
            # Sort by score (descending)
            ranked_carriers = sorted(carrier_evaluations, key=lambda x: -x['score'])
            
            # Store recommendations
            recommendations[route_key] = ranked_carriers
        
        return recommendations
    
    def export_analysis_to_json(self, filepath: str) -> bool:
        """Export analysis results to JSON file"""
        try:
            analysis = {
                "carrier_performance": self.analyze_carrier_performance(),
                "route_analysis": self.analyze_routes(),
                "item_category_analysis": self.analyze_item_categories(),
                "carrier_rankings": self.generate_carrier_rankings(),
                "route_recommendations": self.generate_route_recommendations()
            }
            
            with open(filepath, 'w') as f:
                json.dump(analysis, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error exporting analysis to JSON: {e}")
            return False

# Create singleton instance
data_analyzer = DeepTrackDataAnalyzer()

def get_data_analyzer() -> DeepTrackDataAnalyzer:
    """Get the data analyzer instance"""
    return data_analyzer

# Example usage
if __name__ == "__main__":
    analyzer = get_data_analyzer()
    
    # Export analysis to JSON
    analyzer.export_analysis_to_json('data_analysis.json')

