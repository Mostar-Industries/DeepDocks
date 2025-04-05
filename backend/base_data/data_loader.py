"""
DeepCAL++ Data Loader Module
This module provides functionality to load and process the base data from deeptrack_corex1.csv
"""
import os
import pandas as pd
import json
from typing import Dict, List, Any, Union, Optional

# Path to the base data CSV file
BASE_DATA_PATH = os.path.join(os.path.dirname(__file__), 'deeptrack_corex1.csv')

class DeepTrackDataLoader:
    """
    Data loader for DeepCAL++ base data
    Provides methods to access and transform the deeptrack_corex1.csv data
    """
    
    def __init__(self):
        """Initialize the data loader and load the base data"""
        self.data = None
        self.carriers = None
        self.item_categories = None
        self.emergency_grades = None
        self.delivery_statuses = None
        self.shipment_modes = None
        self._load_data()
        self._extract_reference_tables()
    
    def _load_data(self) -> None:
        """Load the base data from CSV file"""
        try:
            self.data = pd.read_csv(BASE_DATA_PATH)
            print(f"Successfully loaded data with {len(self.data)} records")
        except Exception as e:
            print(f"Error loading base data: {e}")
            # Create empty DataFrame with expected columns if file can't be loaded
            self.data = pd.DataFrame(columns=[
                'request_date_from_destination_country', 'request_reference',
                'item_description', 'item_category', 'origin_country',
                'origin_latitude', 'origin_longitude', 'destination_country',
                'destination_latitude', 'destination_longitude', 'carrier',
                'carrier_cost', 'kuehne_nagel', 'scan_global_logistics',
                'dhl_express', 'dhl_global', 'bwosi', 'agl', 'siginon',
                'freight_in_time', 'weight_kg', 'volume_cbm', 'emergency_grade',
                'initial_quote_awarded', 'final_quote_awarded', 'comments',
                'date_of_arrival_destination', 'delivery_status',
                'mode_of_shipment', 'greenlight_date', 'date_of_collection',
                'emergency grade'
            ])
    
    def _extract_reference_tables(self) -> None:
        """Extract reference tables from the base data"""
        # Extract unique carriers
        carrier_columns = [
            'carrier', 'kuehne_nagel', 'scan_global_logistics', 'dhl_express',
            'dhl_global', 'bwosi', 'agl', 'siginon', 'freight_in_time'
        ]
        
        # Get unique carriers from the carrier column
        carriers = self.data['carrier'].dropna().unique().tolist()
        
        # Add carriers from column names
        for col in carrier_columns[1:]:  # Skip 'carrier' as it's already processed
            # Convert column name to proper carrier name
            carrier_name = col.replace('_', ' ').title()
            if carrier_name not in carriers:
                carriers.append(carrier_name)
        
        self.carriers = [
            {"id": f"C{i+1:03d}", "name": carrier, "description": f"Logistics provider: {carrier}"}
            for i, carrier in enumerate(sorted(carriers))
        ]
        
        # Extract unique item categories
        item_categories = self.data['item_category'].dropna().unique().tolist()
        self.item_categories = [
            {"id": f"IC{i+1:03d}", "name": category, "description": f"Item category: {category}"}
            for i, category in enumerate(sorted(item_categories))
        ]
        
        # Extract unique emergency grades
        emergency_grades = []
        if 'emergency_grade' in self.data.columns:
            emergency_grades = self.data['emergency_grade'].dropna().unique().tolist()
        elif 'emergency grade' in self.data.columns:
            emergency_grades = self.data['emergency grade'].dropna().unique().tolist()
        
        self.emergency_grades = [
            {"id": f"EG{i+1:03d}", "name": grade, "description": f"Emergency priority level: {grade}"}
            for i, grade in enumerate(sorted(emergency_grades))
        ]
        
        # Extract unique delivery statuses
        delivery_statuses = self.data['delivery_status'].dropna().unique().tolist()
        self.delivery_statuses = [
            {"id": f"DS{i+1:03d}", "name": status, "description": f"Delivery status: {status}"}
            for i, status in enumerate(sorted(delivery_statuses))
        ]
        
        # Extract unique shipment modes
        shipment_modes = self.data['mode_of_shipment'].dropna().unique().tolist()
        self.shipment_modes = [
            {"id": f"SM{i+1:03d}", "name": mode, "description": f"Shipment transportation mode: {mode}"}
            for i, mode in enumerate(sorted(shipment_modes))
        ]
    
    def get_data(self) -> pd.DataFrame:
        """Get the full dataset"""
        return self.data.copy()
    
    def get_carriers(self) -> List[Dict[str, str]]:
        """Get the list of carriers"""
        return self.carriers
    
    def get_item_categories(self) -> List[Dict[str, str]]:
        """Get the list of item categories"""
        return self.item_categories
    
    def get_emergency_grades(self) -> List[Dict[str, str]]:
        """Get the list of emergency grades"""
        return self.emergency_grades
    
    def get_delivery_statuses(self) -> List[Dict[str, str]]:
        """Get the list of delivery statuses"""
        return self.delivery_statuses
    
    def get_shipment_modes(self) -> List[Dict[str, str]]:
        """Get the list of shipment modes"""
        return self.shipment_modes
    
    def get_origin_countries(self) -> List[str]:
        """Get the list of origin countries"""
        return sorted(self.data['origin_country'].dropna().unique().tolist())
    
    def get_destination_countries(self) -> List[str]:
        """Get the list of destination countries"""
        return sorted(self.data['destination_country'].dropna().unique().tolist())
    
    def get_routes(self) -> List[Dict[str, str]]:
        """Get the list of unique routes"""
        routes = self.data[['origin_country', 'destination_country']].drop_duplicates()
        return [
            {
                "id": f"R{i+1:03d}",
                "origin": row['origin_country'],
                "destination": row['destination_country'],
                "description": f"Route from {row['origin_country']} to {row['destination_country']}"
            }
            for i, row in routes.iterrows()
        ]
    
    def get_carrier_performance(self, carrier_name: str) -> Dict[str, Any]:
        """Get performance metrics for a specific carrier"""
        if carrier_name not in self.data['carrier'].values:
            return {"error": f"Carrier {carrier_name} not found in data"}
        
        carrier_data = self.data[self.data['carrier'] == carrier_name]
        
        # Calculate performance metrics
        total_shipments = len(carrier_data)
        delivered_shipments = len(carrier_data[carrier_data['delivery_status'] == 'Delivered'])
        delivery_rate = delivered_shipments / total_shipments if total_shipments > 0 else 0
        
        # Calculate average cost
        avg_cost = carrier_data['carrier_cost'].mean()
        
        return {
            "carrier": carrier_name,
            "total_shipments": total_shipments,
            "delivered_shipments": delivered_shipments,
            "delivery_rate": delivery_rate,
            "average_cost": avg_cost
        }
    
    def get_route_statistics(self, origin: str, destination: str) -> Dict[str, Any]:
        """Get statistics for a specific route"""
        route_data = self.data[
            (self.data['origin_country'] == origin) & 
            (self.data['destination_country'] == destination)
        ]
        
        if len(route_data) == 0:
            return {"error": f"No data found for route from {origin} to {destination}"}
        
        # Calculate route statistics
        total_shipments = len(route_data)
        avg_weight = route_data['weight_kg'].mean()
        avg_volume = route_data['volume_cbm'].mean()
        
        # Get carrier distribution
        carrier_counts = route_data['carrier'].value_counts().to_dict()
        
        return {
            "origin": origin,
            "destination": destination,
            "total_shipments": total_shipments,
            "average_weight_kg": avg_weight,
            "average_volume_cbm": avg_volume,
            "carrier_distribution": carrier_counts
        }
    
    def get_example_shipments(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get example shipments from the data"""
        if len(self.data) == 0:
            return []
        
        # Select a diverse set of examples
        examples = []
        
        # Try to get examples with different carriers
        for carrier in self.data['carrier'].dropna().unique():
            if len(examples) >= limit:
                break
            
            carrier_data = self.data[self.data['carrier'] == carrier].iloc[0].to_dict()
            examples.append(carrier_data)
        
        # If we still need more examples, add them
        if len(examples) < limit and len(self.data) > len(examples):
            remaining = limit - len(examples)
            additional = self.data.iloc[len(examples):len(examples)+remaining].to_dict('records')
            examples.extend(additional)
        
        return examples
    
    def export_data_definitions(self) -> Dict[str, Any]:
        """Export data definitions based on the CSV structure"""
        # Get a sample row for examples
        sample = self.data.iloc[0].to_dict() if len(self.data) > 0 else {}
        
        # Define data types based on DataFrame dtypes
        dtypes = self.data.dtypes.to_dict()
        
        definitions = {}
        for column in self.data.columns:
            dtype = dtypes.get(column, 'unknown')
            dtype_str = str(dtype)
            
            if 'float' in dtype_str:
                data_type = 'number'
            elif 'int' in dtype_str:
                data_type = 'number'
            elif 'datetime' in dtype_str:
                data_type = 'date'
            else:
                data_type = 'string'
            
            # Get example value
            example = sample.get(column, '')
            
            # Create definition
            definitions[column] = {
                "type": data_type,
                "description": f"Field: {column.replace('_', ' ').title()}",
                "example": example
            }
        
        return {
            "dataDefinitions": definitions,
            "referenceTables": {
                "carriers": self.carriers,
                "itemCategories": self.item_categories,
                "emergencyGrades": self.emergency_grades,
                "deliveryStatuses": self.delivery_statuses,
                "shipmentModes": self.shipment_modes
            }
        }
    
    def export_to_json(self, filepath: str) -> bool:
        """Export data definitions and reference tables to JSON file"""
        try:
            data = self.export_data_definitions()
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error exporting data to JSON: {e}")
            return False

# Create singleton instance
data_loader = DeepTrackDataLoader()

def get_data_loader() -> DeepTrackDataLoader:
    """Get the data loader instance"""
    return data_loader

# Example usage
if __name__ == "__main__":
    loader = get_data_loader()
    print(f"Loaded {len(loader.get_data())} records")
    print(f"Found {len(loader.get_carriers())} carriers")
    print(f"Found {len(loader.get_item_categories())} item categories")
    
    # Export data definitions to JSON
    loader.export_to_json('data_definitions.json')

