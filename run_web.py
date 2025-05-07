#!/usr/bin/env python3
"""
InsightForge Web Interface Launcher

This script is a simplified version of the web interface launcher
that avoids advanced import dependencies for troubleshooting.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add the project root to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("insightforge.web")

try:
    from flask import Flask, render_template, render_template_string
except ImportError:
    print("Error: Flask is not installed. Please run 'pip install flask'.")
    sys.exit(1)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>InsightForge - Web UI</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-5">
                <div class="row justify-content-center">
                    <div class="col-md-8">
                        <div class="card">
                            <div class="card-header bg-primary text-white">
                                <h2 class="mb-0">InsightForge Web UI</h2>
                            </div>
                            <div class="card-body">
                                <h3>Configuration Management</h3>
                                <p>This is a simplified version of the InsightForge web interface.</p>
                                <p>The full interface could not be loaded due to import issues, but Flask is working!</p>
                                
                                <h4 class="mt-4">Available Features:</h4>
                                <ul>
                                    <li>LLM Provider Configuration</li>
                                    <li>Jira Integration</li>
                                    <li>GitHub Integration</li>
                                    <li>Project Settings</li>
                                </ul>
                                
                                <div class="alert alert-info mt-4">
                                    <strong>Development Status:</strong> To use the full interface, please resolve the import issues with advanced configuration modules.
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
    """)

def main():
    """Start the Flask application."""
    parser = argparse.ArgumentParser(description="InsightForge Web Interface")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=5000, help="Port to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    # Print startup message
    logger.info("=" * 60)
    logger.info("Starting InsightForge Web Interface (Simplified Version)")
    logger.info(f"URL: http://{args.host}:{args.port}")
    logger.info("=" * 60)
    
    # Run the app
    app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == "__main__":
    main()