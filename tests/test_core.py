"""
Test suite for DeepCAL++ core functionality
"""
import os
import sys
import unittest
import numpy as np
import pandas as pd

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import modules to test
from backend.core.deepcal_core import (
    process_logistics_data,
    run_topsis_analysis,
    normalize_decision_matrix,
    determine_ideal_solutions
)

class TestDeepCalCore(unittest.TestCase):
    """Test cases for DeepCAL++ core functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.test_forwarders = [
            {
                "name": "TestForwarder1",
                "cost": 1000,
                "time": 10,
                "reliability": 90,
                "tracking": True
            },
            {
                "name": "TestForwarder2",
                "cost": 800,
                "time": 15,
                "reliability": 80,
                "tracking": False
            },
            {
                "name": "TestForwarder3",
                "cost": 1200,
                "time": 8,
                "reliability": 95,
                "tracking": True
            }
        ]
    
    def test_process_logistics_data(self):
        """Test the data processing function"""
        df = process_logistics_data(self.test_forwarders)
        
        # Check that DataFrame has the correct shape
        self.assertEqual(df.shape, (3, 5))
        
        # Check that columns were converted to the correct types
        self.assertTrue(np.issubdtype(df['cost'].dtype, np.number))
        self.assertTrue(np.issubdtype(df['time'].dtype, np.number))
        self.assertTrue(np.issubdtype(df['reliability'].dtype, np.number))
        self.assertTrue(np.issubdtype(df['tracking'].dtype, np.number))
        
        # Check that the names are preserved
        self.assertEqual(list(df['name']), ["TestForwarder1", "TestForwarder2", "TestForwarder3"])
        
        # Check that boolean was converted to int
        self.assertEqual(list(df['tracking']), [1, 0, 1])
    
    def test_normalize_decision_matrix(self):
        """Test the normalization function"""
        # Create a simple test matrix
        matrix = np.array([
            [1000, 10, 90, 1],
            [800, 15, 80, 0],
            [1200, 8, 95, 1]
        ])
        
        normalized = normalize_decision_matrix(matrix)
        
        # Check shape
        self.assertEqual(normalized.shape, (3, 4))
        
        # Check that the columns are normalized (Euclidean norm = 1)
        for col in range(normalized.shape[1]):
            col_norm = np.sqrt(np.sum(normalized[:, col]**2))
            self.assertAlmostEqual(col_norm, 1.0, places=6)
    
    def test_determine_ideal_solutions(self):
        """Test the ideal solution determination function"""
        # Create a normalized matrix
        matrix = np.array([
            [0.6, 0.5, 0.6, 0.7],
            [0.4, 0.7, 0.5, 0.0],
            [0.7, 0.5, 0.6, 0.7]
        ])
        
        # Define criteria types (cost, cost, benefit, benefit)
        criteria = ['cost', 'cost', 'benefit', 'benefit']
        
        ideal, negative_ideal = determine_ideal_solutions(matrix, criteria)
        
        # For cost criteria, ideal is min and negative ideal is max
        self.assertEqual(ideal[0], 0.4)  # min of first column (cost)
        self.assertEqual(ideal[1], 0.5)  # min of second column (cost)
        
        # For benefit criteria, ideal is max and negative ideal is min
        self.assertEqual(ideal[2], 0.6)  # max of third column (benefit)
        self.assertEqual(ideal[3], 0.7)  # max of fourth column (benefit)
        
        # Check negative ideal values
        self.assertEqual(negative_ideal[0], 0.7)  # max of first column (cost)
        self.assertEqual(negative_ideal[1], 0.7)  # max of second column (cost)
        self.assertEqual(negative_ideal[2], 0.5)  # min of third column (benefit)
        self.assertEqual(negative_ideal[3], 0.0)  # min of fourth column (benefit)
    
    def test_run_topsis_analysis(self):
        """Test the complete TOPSIS analysis"""
        df = process_logistics_data(self.test_forwarders)
        results = run_topsis_analysis(df)
        
        # Check that we have 3 results
        self.assertEqual(len(results), 3)
        
        # Check that results have required fields
        self.assertTrue('name' in results[0])
        self.assertTrue('rank' in results[0])
        self.assertTrue('score' in results[0])
        
        # Check that ranks are 1, 2, 3
        ranks = [r['rank'] for r in results]
        self.assertEqual(sorted(ranks), [1, 2, 3])
        
        # Check that scores are between 0 and 1
        for result in results:
            self.assertTrue(0 <= result['score'] <= 1)
        
        # Verify that the result with rank 1 has the highest score
        rank1_result = next(r for r in results if r['rank'] == 1)
        self.assertEqual(rank1_result['score'], max(r['score'] for r in results))

if __name__ == '__main__':
    unittest.main()

