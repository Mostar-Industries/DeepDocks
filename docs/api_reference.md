# DeepCAL++ API Reference

This document provides a comprehensive reference for the DeepCAL++ API, including core functions, classes, and their parameters.

## Core Module

### `process_logistics_data(forwarders)`

Processes raw forwarder data into a format suitable for TOPSIS analysis.

**Parameters:**
- `forwarders` (List[Dict]): List of dictionaries containing forwarder data with the following keys:
  - `name` (str): Name of the forwarder
  - `cost` (float): Cost of the service
  - `time` (float): Delivery time in days
  - `reliability` (float): Reliability score (0-100)
  - `tracking` (bool): Whether real-time tracking is provided

**Returns:**
- `pandas.DataFrame`: Processed data frame ready for analysis

**Example:**
```python
from backend.core.deepcal_core import process_logistics_data

forwarders = [
    {
        "name": "AfricaLogistics",
        "cost": 1200,
        "time": 14,
        "reliability": 85,
        "tracking": True
    },
    {
        "name": "GlobalFreight",
        "cost": 950,
        "time": 18,
        "reliability": 78,
        "tracking": False
    }
]

processed_data = process_logistics_data(forwarders)

