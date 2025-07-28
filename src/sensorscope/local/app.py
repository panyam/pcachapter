#!/usr/bin/env python3
"""
Local Flask application for development and testing.

This serves as the reference implementation and development environment
for Sita's sensor redundancy analysis before cloud deployment.

Usage:
    python app.py
    
Then test with:
    curl -X POST http://localhost:8000/pca -H "Content-Type: application/json" -d '{"use_sample_data": true}'
"""

import sys
import os
from flask import Flask, request, jsonify
import logging
from typing import Dict, Any

# Add shared modules to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

try:
    from pca_core import process_pca_request
    from data_validation import generate_sample_data, validate_input_data, create_coffee_shop_sample
    from response_formatter import format_response, format_health_response
except ImportError as e:
    print(f"Error importing shared modules: {e}")
    print("Make sure you're running from the correct directory and have installed requirements.txt")
    sys.exit(1)

# Configure Flask application
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False  # Preserve response key order

# Configure logging for development
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/pca', methods=['POST'])
def pca_analysis():
    """
    Main PCA analysis endpoint.
    
    Accepts JSON request with sensor data or sample data generation parameters,
    performs PCA analysis, and returns formatted results with business insights.
    
    Request format:
        {
            "use_sample_data": boolean (optional, default: false),
            "data": array (required if not using sample data),
            "n_components": integer (optional, default: 2),
            "n_samples": integer (optional, default: 100, for sample data),
            "n_features": integer (optional, default: 5, for sample data),
            "random_state": integer (optional, default: 42),
            "scale_features": boolean (optional, default: true),
            "include_raw_data": boolean (optional, default: false),
            "business_context": object (optional)
        }
    """
    try:
        # Parse request data
        request_data = request.get_json()
        if request_data is None:
            return jsonify({
                "status": "error",
                "error": "Invalid JSON or missing Content-Type: application/json header",
                "example": {
                    "use_sample_data": True,
                    "n_components": 2
                }
            }), 400
        
        logger.info(f"Processing PCA request: {len(str(request_data))} bytes")
        
        # Handle sample data generation
        if request_data.get('use_sample_data', False):
            logger.info("Generating synthetic coffee shop sensor data")
            
            # Check for coffee shop sample request
            if request_data.get('coffee_shop_sample', False):
                coffee_data = create_coffee_shop_sample(
                    location=request_data.get('location', 'downtown'),
                    hours=request_data.get('hours', 24),
                    sensor_types=request_data.get('sensor_types')
                )
                data = coffee_data['data']
                business_context = coffee_data['business_context']
                logger.info(f"Generated coffee shop sample: {len(data)} readings, {len(data[0])} sensors")
            else:
                # Generate basic synthetic data
                data = generate_sample_data(
                    n_samples=request_data.get('n_samples', 100),
                    n_features=request_data.get('n_features', 5),
                    n_redundant=request_data.get('n_redundant', 2),
                    n_informative=request_data.get('n_informative', 3),
                    random_state=request_data.get('random_state', 42)
                )
                business_context = {
                    "cost_per_sensor": 250,  # Annual cost per sensor
                    "analysis_type": "sensor_redundancy"
                }
                logger.info(f"Generated synthetic data: {data.shape}")
        
        else:
            # Validate uploaded data
            if 'data' not in request_data:
                return jsonify({
                    "status": "error",
                    "error": "Missing 'data' field in request",
                    "help": "Either provide 'data' array or set 'use_sample_data': true",
                    "example_data": [[1.2, 2.3, 3.1], [1.1, 2.4, 3.2], [1.3, 2.1, 3.0]]
                }), 400
            
            logger.info("Validating uploaded data")
            data = validate_input_data(request_data['data'])
            business_context = request_data.get('business_context', {})
            logger.info(f"Validated data: {data.shape}")
        
        # Process PCA request
        logger.info(f"Starting PCA analysis: {data.shape[0]} samples, {data.shape[1]} features")
        
        pca_results = process_pca_request(
            data=data,
            n_components=request_data.get('n_components', 2),
            scale_features=request_data.get('scale_features', True)
        )
        
        logger.info(f"PCA completed in {pca_results.get('performance', {}).get('execution_time_ms', 0):.1f}ms")
        
        # Format response with business insights
        formatted_response = format_response(
            pca_results=pca_results,
            platform="local-flask",
            include_raw_data=request_data.get('include_raw_data', False),
            business_context=business_context
        )
        
        # Return appropriate HTTP status
        if pca_results['status'] == 'success':
            return jsonify(formatted_response), 200
        else:
            return jsonify(formatted_response), 400
            
    except Exception as e:
        logger.error(f"Unexpected error in PCA analysis: {str(e)}", exc_info=True)
        
        error_response = {
            "status": "error",
            "error": {
                "type": type(e).__name__,
                "message": str(e),
                "platform": "local-flask"
            },
            "help": "Check server logs for detailed error information"
        }
        
        return jsonify(error_response), 500


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for service monitoring.
    
    Returns service status and basic information about capabilities.
    """
    try:
        # Test basic functionality by generating small sample
        test_data = generate_sample_data(n_samples=5, n_features=3, random_state=42)
        test_result = process_pca_request(test_data, n_components=2)
        
        health_info = {
            "core_functionality": "operational" if test_result["status"] == "success" else "degraded",
            "test_execution_time_ms": test_result.get("performance", {}).get("execution_time_ms", 0)
        }
        
        response = format_health_response(
            platform="local-flask",
            additional_info=health_info
        )
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        
        response = {
            "status": "unhealthy", 
            "error": str(e),
            "platform": "local-flask"
        }
        
        return jsonify(response), 503


@app.route('/', methods=['GET'])
def root():
    """
    Root endpoint with service information and usage examples.
    """
    return jsonify({
        "service": "SensorScope - Local Development Server",
        "description": "Serverless PCA analysis for coffee shop sensor optimization",
        "endpoints": {
            "pca_analysis": {
                "path": "/pca",
                "method": "POST", 
                "description": "Perform PCA analysis on sensor data"
            },
            "health_check": {
                "path": "/health",
                "method": "GET",
                "description": "Service health and status check"
            }
        },
        "quick_test": {
            "description": "Test with synthetic coffee shop sensor data",
            "example_curl": "curl -X POST http://localhost:8000/pca -H 'Content-Type: application/json' -d '{\"use_sample_data\": true}'"
        },
        "business_context": {
            "purpose": "Sensor redundancy analysis for cost optimization",
            "scenario": "Sita's coffee shop chain sensor reduction project",
            "goal": "Identify which sensors provide unique vs redundant information"
        },
        "documentation": "See README.md for complete setup and usage instructions"
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors with helpful information."""
    return jsonify({
        "error": "Endpoint not found",
        "available_endpoints": ["/", "/pca", "/health"],
        "help": "See root endpoint (/) for usage information"
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle method not allowed errors."""
    return jsonify({
        "error": "Method not allowed",
        "help": "POST /pca for analysis, GET /health for status check"
    }), 405


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 SensorScope - Local Development Server")
    print("=" * 60)
    print()
    print("Sita's Coffee Shop Sensor Analysis Service")
    print("Serverless PCA for sensor redundancy optimization")
    print()
    print("📡 Service URLs:")
    print("   • Main service: http://localhost:8000/pca")
    print("   • Health check: http://localhost:8000/health") 
    print("   • Documentation: http://localhost:8000/")
    print()
    print("🧪 Quick Test:")
    print("   curl -X POST http://localhost:8000/pca \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"use_sample_data\": true, \"n_components\": 2}'")
    print()
    print("📊 Expected Result:")
    print("   • 5D sensor data → 2D reduction")
    print("   • ~75% variance explained")
    print("   • Business insights for sensor optimization")
    print()
    print("⚡ Development Mode:")
    print("   • Auto-reload on file changes")
    print("   • Detailed error logging")
    print("   • Performance monitoring")
    print()
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        app.run(
            host='0.0.0.0',  # Accept connections from any IP
            port=8000,       # Consistent port across examples  
            debug=True,      # Auto-reload and detailed errors
            threaded=True    # Handle multiple concurrent requests
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped!")
    except Exception as e:
        print(f"\n❌ Server failed to start: {e}")
        print("\n🔧 Troubleshooting:")
        print("   • Check if port 8000 is already in use: lsof -i :8000")
        print("   • Verify all dependencies installed: pip list")
        print("   • Check Python version: python --version (need 3.9+)")
        sys.exit(1)
