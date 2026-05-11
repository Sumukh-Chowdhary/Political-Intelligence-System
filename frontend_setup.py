"""
React Frontend Setup Guide for Political Intelligence System
"""

import os
import json

# Create frontend structure
def setup_react_frontend():
    """Generate React frontend structure"""
    
    frontend_dir = "frontend"
    
    # Create package.json
    package_json = {
        "name": "political-intelligence-frontend",
        "version": "1.0.0",
        "private": True,
        "dependencies": {
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "react-router-dom": "^6.20.0",
            "axios": "^1.6.0",
            "plotly.js": "^2.26.0",
            "react-plotly.js": "^2.2.0",
            "chart.js": "^4.4.0",
            "react-chartjs-2": "^5.2.0"
        },
        "scripts": {
            "start": "react-scripts start",
            "build": "react-scripts build",
            "test": "react-scripts test",
            "eject": "react-scripts eject"
        },
        "eslintConfig": {
            "extends": ["react-app"]
        },
        "browserslist": {
            "production": ["> 0.2%", "not dead", "not op_mini all"],
            "development": ["last 1 chrome version", "last 1 firefox version"]
        }
    }
    
    return {
        "package.json": package_json,
        "setup_instructions": {
            "1_create_app": "npx create-react-app frontend",
            "2_install_deps": "cd frontend && npm install",
            "3_start_dev": "npm start"
        }
    }

if __name__ == "__main__":
    setup = setup_react_frontend()
    print(json.dumps(setup, indent=2))
