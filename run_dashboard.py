import streamlit as st
import sys
import os

# Add the project root directory to Python path
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, root_dir)

from src.frontend.dashboard import Dashboard

if __name__ == "__main__":
    dashboard = Dashboard()
    dashboard.run()
