"""
DeepCAL++ Data Mirroring Module
This module handles mirroring data between Supabase and local base data
"""
import os
import json
import time
import logging
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("data_mirror")

# Base data paths
BASE_DATA_DIR = os.path.join(os.path.dirname(__file__), 'base_data')
TRAINING_DATA_DIR = os.path.join(os.path.dirname(__file__), 'training_data')
MIRROR_CACHE_PATH = os.path.join(BASE_DATA_DIR, 'mirror_cache.json')
LAST_SYNC_PATH = os.path.join(BASE_DATA_DIR, 'last_sync.json')

# Ensure directories exist
os.makedirs(BASE_DATA_DIR, exist_ok=True)
os.makedirs(TRAINING_DATA_DIR, exist_ok=True)

class DataMirror:
    """
    Handles mirroring between Supabase and local base data
    """
    def __init__(self):
        """Initialize the data mirror"""
        self.last_sync_time = self._load_last_sync_time()
        self.mirror_cache = self._load_mirror_cache()
        
    def _load_last_sync_time(self) -> float:
        """Load the timestamp of the last synchronization"""
        try:
            if os.path.exists(LAST_SYNC_PATH):
                with open(LAST_SYNC_PATH, 'r') as f:
                    data = json.load(f)
                return data.get('timestamp', 0)
            return 0
        except Exception as e:
            logger.error(f"Error loading last sync time: {e}")
            return 0
    
    def _save_last_sync_time(self):
        """Save the current time as the last synchronization timestamp"""
        try:
            with open(LAST_SYNC_PATH, 'w') as f:
                json.dump({'timestamp': time.time()}, f)
        except Exception as e:
            logger.error(f"Error saving last sync time: {e}")
    
    def _load_mirror_cache(self) -> Dict[str, Any]:
        """Load the mirror cache containing the last mirrored data"""
        try:
            if os.path.exists(MIRROR_CACHE_PATH):
                with open(MIRROR_CACHE_PATH, 'r') as f:
                    return json.load(f)
            return {
                'forwarders': [],
                'routes': [],
                'rate_cards': [],
                'shipments': []
            }
        except Exception as e:
            logger.error(f"Error loading mirror cache: {e}")
            return {
                'forwarders': [],
                'routes': [],
                'rate_cards': [],
                'shipments': []
            }
    
    def _save_mirror_cache(self):
        """Save the current mirror cache"""
        try:
            with open(MIRROR_CACHE_PATH, 'w') as f:
                json.dump(self.mirror_cache, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving mirror cache: {e}")
    
    def mirror_supabase_data(self, supabase_data: Dict[str, List[Dict[str, Any]]]) -> bool:
        """
        Mirror data from Supabase to local base data
        
        Args:
            supabase_data: Dictionary containing data from Supabase
            
        Returns:
            True if mirroring was successful, False otherwise
        """
        try:
            # Update mirror cache with new data
            for key, data in supabase_data.items():
                if key in self.mirror_cache:
                    # Merge new data with existing data
                    self._merge_data(key, data)
                else:
                    self.mirror_cache[key] = data
            
            # Save updated mirror cache
            self._save_mirror_cache()
            
            # Update base data files
            self._update_base_data_files()
            
            # Update last sync time
            self._save_last_sync_time()
            
            logger.info(f"Successfully mirrored data from Supabase")
            return True
        except Exception as e:
            logger.error(f"Error mirroring data: {e}")
            return False
    
    def _merge_data(self, key: str, new_data: List[Dict[str, Any]]):
        """
        Merge new data with existing data in the mirror cache
        
        Args:
            key: Data category key
            new_data: New data to merge
        """
        # Create a dictionary of existing data by ID for easy lookup
        existing_data_dict = {item.get('id', f"item_{i}"): item 
                             for i, item in enumerate(self.mirror_cache[key])}
        
        # Update existing items and add new ones
        for item in new_data:
            item_id = item.get('id')
            if item_id and item_id in existing_data_dict:
                # Update existing item
                existing_data_dict[item_id].update(item)
            else:
                # Add new item
                existing_data_dict[item_id if item_id else f"item_{len(existing_data_dict)}"] = item
        
        # Update mirror cache with merged data
        self.mirror_cache[key] = list(existing_data_dict.values())
    
    def _update_base_data_files(self):
        """Update base data files with mirrored data"""
        # Update forwarders.json
        if 'forwarders' in self.mirror_cache:
            self._save_base_data('forwarders.json', self.mirror_cache['forwarders'])
        
        # Update routes.json
        if 'routes' in self.mirror_cache:
            self._save_base_data('routes.json', self.mirror_cache['routes'])
        
        # Update rate_cards.json
        if 'rate_cards' in self.mirror_cache:
            self._save_base_data('rate_cards.json', self.mirror_cache['rate_cards'])
        
        # Update shipments.json
        if 'shipments' in self.mirror_cache:
            self._save_base_data('shipments.json', self.mirror_cache['shipments'])
    
    def _save_base_data(self, filename: str, data: List[Dict[str, Any]]):
        """
        Save data to a base data file
        
        Args:
            filename: Name of the file
            data: Data to save
        """
        try:
            filepath = os.path.join(BASE_DATA_DIR, filename)
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Updated base data file: {filename}")
        except Exception as e:
            logger.error(f"Error saving base data file {filename}: {e}")
    
    def get_base_data(self, category: str) -> List[Dict[str, Any]]:
        """
        Get base data for a specific category
        
        Args:
            category: Data category (forwarders, routes, etc.)
            
        Returns:
            List of data items for the category
        """
        try:
            filepath = os.path.join(BASE_DATA_DIR, f"{category}.json")
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    return json.load(f)
            return self.mirror_cache.get(category, [])
        except Exception as e:
            logger.error(f"Error loading base data for {category}: {e}")
            return self.mirror_cache.get(category, [])
    
    def get_training_data(self) -> Dict[str, Any]:
        """
        Get training data
        
        Returns:
            Dictionary containing training data
        """
        try:
            training_data = {}
            
            # Load all JSON files in the training data directory
            for filename in os.listdir(TRAINING_DATA_DIR):
                if filename.endswith('.json'):
                    filepath = os.path.join(TRAINING_DATA_DIR, filename)
                    with open(filepath, 'r') as f:
                        key = filename.split('.')[0]
                        training_data[key] = json.load(f)
            
            return training_data
        except Exception as e:
            logger.error(f"Error loading training data: {e}")
            return {}

# Create singleton instance
data_mirror = DataMirror()

def get_data_mirror() -> DataMirror:
    """Get the data mirror instance"""
    return data_mirror

def mirror_data_from_supabase(supabase_data: Dict[str, List[Dict[str, Any]]]) -> bool:
    """
    Mirror data from Supabase to local base data
    
    Args:
        supabase_data: Dictionary containing data from Supabase
        
    Returns:
        True if mirroring was successful, False otherwise
    """
    return data_mirror.mirror_data_from_supabase(supabase_data)

def get_base_forwarders() -> List[Dict[str, Any]]:
    """Get forwarders from base data"""
    return data_mirror.get_base_data('forwarders')

def get_base_routes() -> List[Dict[str, Any]]:
    """Get routes from base data"""
    return data_mirror.get_base_data('routes')

def get_base_rate_cards() -> List[Dict[str, Any]]:
    """Get rate cards from base data"""
    return data_mirror.get_base_data('rate_cards')

def get_base_shipments() -> List[Dict[str, Any]]:
    """Get shipments from base data"""
    return data_mirror.get_base_data('shipments')

def get_training_data() -> Dict[str, Any]:
    """Get training data"""
    return data_mirror.get_training_data()

