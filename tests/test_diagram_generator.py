import unittest
import matplotlib.pyplot as plt
import networkx as nx
from theoris.diagram_generator import generate_diagram

class TestDiagramGenerator(unittest.TestCase):
    def test_generate_diagram(self):
        # Create a sample block structure
        blocks = [
            {
                'name': 'Block A',
                'inputs': [],
                'outputs': ['Block B', 'Block C']
            },
            {
                'name': 'Block B',
                'inputs': ['Block A'],
                'outputs': ['Block D']
            },
            {
                'name': 'Block C',
                'inputs': ['Block A'],
                'outputs': ['Block D']
            },
            {
                'name': 'Block D',
                'inputs': ['Block B', 'Block C'],
                'outputs': []
            }
        ]
        
        # Test that the function runs without errors
        try:
            # Disable actual plotting for the test
            plt.ioff()
            generate_diagram(blocks)
            plt.close()
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"generate_diagram raised an exception: {e}")

if __name__ == '__main__':
    unittest.main()