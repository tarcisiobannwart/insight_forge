#!/usr/bin/env python3
"""
InsightForge Web Interface Launcher

This script launches the InsightForge web interface.
"""

import os
import sys
import argparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("insightforge.web")

# Add project root to path if running as script
script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if script_dir not in sys.path:
    sys.path.insert(0, os.path.dirname(script_dir))

def main():
    """Run the web application."""
    from insightforge.web.app import app, init_managers
    
    parser = argparse.ArgumentParser(description="InsightForge Web Interface")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=5000, help="Port to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    # Initialize configuration managers
    init_managers(args.config)
    
    # Print startup message
    logger.info("=" * 60)
    logger.info("Starting InsightForge Web Interface")
    logger.info(f"Configuration: {args.config or 'Using default config path'}")
    logger.info(f"URL: http://{args.host}:{args.port}")
    logger.info("=" * 60)
    
    # Run the app
    app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == "__main__":
    main()