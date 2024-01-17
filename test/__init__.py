import sys
import os

# Add the project root directory to the Python path so that tests can import modules directly
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../src')
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../test')
