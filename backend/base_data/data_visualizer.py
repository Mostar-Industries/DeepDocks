"""
DeepCAL++ Data Visualizer Module
This module provides functionality to create visualizations from the base data
"""
import os
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Union, Optional, Tuple
from .data_loader import get_data_loader
from .data_analyzer import get_data_analyzer

class DeepTrackDataVisualizer:
    """
    Data visualizer for DeepCAL++ base data
    Provides methods to create visualizations from the deeptrack_corex1.csv data
    """
    
    def __init__(self):
        """Initialize the data visualizer"""
        self.loader = get_data_loader()
        self.analyzer = get_data_analyzer()
        self.data = self.loader.get_data()
        
        # Set default style
        sns.set_style("whitegrid")
    
    def plot_carrier_performance(self, save_path: Optional[str] = None) -> plt.Figure:
        """Plot performance metrics for carriers"""
        carrier_performance = self.analyzer.analyze_carrier_performance()
        
        # Extract data for plotting
        carriers = list(carrier_performance.keys())
        delivery_rates = [metrics['delivery_rate'] for metrics in carrier_performance.values()]
        avg_costs = [metrics['average_cost'] if metrics['average_cost'] is not None else 0 
                    for metrics in carrier_performance.values()]
        
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Plot delivery rates
        bars1 = ax1.bar(carriers, delivery_rates, color='skyblue')
        ax1.set_title('Carrier Delivery Rates')
        ax1.set_xlabel('Carrier')
        ax1.set_ylabel('Delivery Rate')
        ax1.set_ylim(0, 1.0)
        ax1.tick_params(axis='x', rotation=45)
        
        # Add value labels
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}',
                    ha='center', va='bottom')
        
        # Plot average costs
        bars2 = ax2.bar(carriers, avg_costs, color='lightgreen')
        ax2.set_title('Carrier Average Costs')
        ax2.set_xlabel('Carrier')
        ax2.set_ylabel('Average Cost (USD)')
        ax2.tick_params(axis='x', rotation=45)
        
        # Add value labels
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}',
                    ha='center', va='bottom')
        
        plt.tight_layout()
        
        # Save if path provided
        if save_path:
            plt.savefig(save_path)
        
        return fig
    
    def plot_route_map(self, save_path: Optional[str] = None) -> plt.Figure:
        """Plot a map of routes with shipment volumes"""
        # This is a simplified version - a real implementation would use a mapping library
        # like Folium, GeoPandas, or Plotly for interactive maps
        
        # Get unique routes
        routes = self.data[['origin_country', 'destination_country']].drop_duplicates()
         = self.data[['origin_country', 'destination_country']].drop_duplicates()
        
        # Get coordinates for each country
        # In a real implementation, we would use a geocoding service or a country coordinates database
        # For this example, we'll use the average coordinates from the data
        
        country_coords = {}
        
        # Get origin coordinates
        origin_coords = self.data.groupby('origin_country')[['origin_latitude', 'origin_longitude']].mean()
        for country, row in origin_coords.iterrows():
            country_coords[country] = (row['origin_latitude'], row['origin_longitude'])
        
        # Get destination coordinates
        dest_coords = self.data.groupby('destination_country')[['destination_latitude', 'destination_longitude']].mean()
        for country, row in dest_coords.iterrows():
            if country not in country_coords:
                country_coords[country] = (row['destination_latitude'], row['destination_longitude'])
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Plot countries as points
        for country, (lat, lon) in country_coords.items():
            ax.scatter(lon, lat, s=100, alpha=0.7, label=country)
            ax.text(lon, lat, country, fontsize=8)
        
        # Plot routes as lines
        for _, row in routes.iterrows():
            origin = row['origin_country']
            destination = row['destination_country']
            
            if origin in country_coords and destination in country_coords:
                o_lat, o_lon = country_coords[origin]
                d_lat, d_lon = country_coords[destination]
                
                # Count shipments on this route
                route_count = len(self.data[
                    (self.data['origin_country'] == origin) & 
                    (self.data['destination_country'] == destination)
                ])
                
                # Line width based on shipment count
                line_width = 0.5 + (route_count / 10)
                
                # Draw line
                ax.plot([o_lon, d_lon], [o_lat, d_lat], 'r-', alpha=0.5, linewidth=line_width)
        
        ax.set_title('Shipment Routes Map')
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        
        plt.tight_layout()
        
        # Save if path provided
        if save_path:
            plt.savefig(save_path)
        
        return fig
    
    def plot_carrier_rankings(self, save_path: Optional[str] = None) -> plt.Figure:
        """Plot carrier rankings based on different metrics"""
        rankings = self.analyzer.generate_carrier_rankings()
        
        # Extract overall rankings
        overall_rankings = rankings['rankings']['overall']
        
        # Extract data for plotting
        carriers = [r['name'] for r in overall_rankings]
        overall_ranks = [r['overall_rank'] for r in overall_rankings]
        reliability_ranks = [r['reliability_rank'] for r in overall_rankings]
        cost_ranks = [r['cost_rank'] for r in overall_rankings]
        time_ranks = [r['time_rank'] for r in overall_rankings]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Set width of bars
        bar_width = 0.2
        
        # Set positions of bars on X axis
        r1 = np.arange(len(carriers))
        r2 = [x + bar_width for x in r1]
        r3 = [x + bar_width for x in r2]
        r4 = [x + bar_width for x in r3]
        
        # Create bars
        ax.bar(r1, overall_ranks, width=bar_width, label='Overall', color='blue')
        ax.bar(r2, reliability_ranks, width=bar_width, label='Reliability', color='green')
        ax.bar(r3, cost_ranks, width=bar_width, label='Cost', color='red')
        ax.bar(r4, time_ranks, width=bar_width, label='Time', color='purple')
        
        # Add labels and title
        ax.set_xlabel('Carrier')
        ax.set_ylabel('Rank (lower is better)')
        ax.set_title('Carrier Rankings by Different Metrics')
        ax.set_xticks([r + bar_width*1.5 for r in range(len(carriers))])
        ax.set_xticklabels(carriers, rotation=45, ha='right')
        
        # Add legend
        ax.legend()
        
        # Add grid
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        
        # Save if path provided
        if save_path:
            plt.savefig(save_path)
        
        return fig
    
    def plot_item_category_distribution(self, save_path: Optional[str] = None) -> plt.Figure:
        """Plot distribution of item categories"""
        # Get item category counts
        category_counts = self.data['item_category'].value_counts()
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Create pie chart
        ax.pie(category_counts, labels=category_counts.index, autopct='%1.1f%%',
              shadow=True, startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        
        plt.title('Distribution of Item Categories')
        
        # Save if path provided
        if save_path:
            plt.savefig(save_path)
        
        return fig
    
    def plot_delivery_status_distribution(self, save_path: Optional[str] = None) -> plt.Figure:
        """Plot distribution of delivery statuses"""
        # Get delivery status counts
        status_counts = self.data['delivery_status'].value_counts()
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Create bar chart
        bars = ax.bar(status_counts.index, status_counts.values, color='skyblue')
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height}',
                   ha='center', va='bottom')
        
        ax.set_title('Distribution of Delivery Statuses')
        ax.set_xlabel('Delivery Status')
        ax.set_ylabel('Count')
        ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        # Save if path provided
        if save_path:
            plt.savefig(save_path)
        
        return fig
    
    def generate_dashboard_data(self) -> Dict[str, Any]:
        """Generate data for a dashboard"""
        # Get basic statistics
        total_shipments = len(self.data)
        unique_origins = self.data['origin_country'].nunique()
        unique_destinations = self.data['destination_country'].nunique()
        unique_carriers = self.data['carrier'].nunique()
        
        # Get delivery status counts
        delivery_statuses = self.data['delivery_status'].value_counts().to_dict()
        
        # Get carrier performance
        carrier_performance = self.analyzer.analyze_carrier_performance()
        
        # Get top routes by volume
        route_counts = self.data.groupby(['origin_country', 'destination_country']).size()
        top_routes = route_counts.sort_values(ascending=False).head(5).reset_index()
        top_routes.columns = ['origin', 'destination', 'count']
        top_routes_list = top_routes.to_dict('records')
        
        # Get item category distribution
        category_distribution = self.data['item_category'].value_counts().to_dict()
        
        return {
            "summary": {
                "total_shipments": total_shipments,
                "unique_origins": unique_origins,
                "unique_destinations": unique_destinations,
                "unique_carriers": unique_carriers
            },
            "delivery_statuses": delivery_statuses,
            "carrier_performance": carrier_performance,
            "top_routes": top_routes_list,
            "category_distribution": category_distribution
        }
    
    def export_visualization_data(self, filepath: str) -> bool:
        """Export visualization data to JSON file"""
        try:
            visualization_data = self.generate_dashboard_data()
            
            with open(filepath, 'w') as f:
                json.dump(visualization_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error exporting visualization data to JSON: {e}")
            return False

# Create singleton instance
data_visualizer = DeepTrackDataVisualizer()

def get_data_visualizer() -> DeepTrackDataVisualizer:
    """Get the data visualizer instance"""
    return data_visualizer

# Example usage
if __name__ == "__main__":
    visualizer = get_data_visualizer()
    
    # Export visualization data to JSON
    visualizer.export_visualization_data('visualization_data.json')
    
    # Generate and save plots
    visualizer.plot_carrier_performance('carrier_performance.png')
    visualizer.plot_route_map('route_map.png')
    visualizer.plot_carrier_rankings('carrier_rankings.png')
    visualizer.plot_item_category_distribution('item_categories.png')
    visualizer.plot_delivery_status_distribution('delivery_statuses.png')

