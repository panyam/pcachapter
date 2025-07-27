#!/usr/bin/env python3
"""
Google Cloud Functions handler for SensorScope PCA analysis.

This module provides the Cloud Functions entry point for Maya's sensor
redundancy analysis system, handling HTTP requests and returning PCA results.

Usage:
    Deployed as a Cloud Functions Gen 2 HTTP function.
    Triggered by HTTP POST requests to the function URL.
"""

import sys
import os
import json
import logging
from typing import Dict, Any
import functions_framework

# Import shared modules (available via symlinks)
try:
    from pca_core import process_pca_request
    from data_validation import (generate_sample_data, validate_input_data, create_coffee_shop_sample,
                                 load_dataset_from_gcs, create_sample_datasets_directory)
    from response_formatter import format_response, format_health_response
except ImportError as e:
    logging.error(f"Failed to import shared modules: {e}")
    raise


# Configure logging for Cloud Functions
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@functions_framework.http
def sensorscope_pca(request):
    """
    Cloud Functions entry point for SensorScope PCA analysis.
    
    Handles HTTP requests for sensor redundancy analysis using Principal
    Component Analysis. Supports both sample data generation and uploaded
    sensor data.
    
    Args:
        request: Flask Request object containing JSON payload
        
    Returns:
        dict: JSON response with PCA analysis results and business insights
        
    Expected request format:
        {
            "use_sample_data": boolean (optional, default: false),
            "coffee_shop_sample": boolean (optional, default: false),
            "data": array (required if not using sample data),
            "n_components": integer (optional, default: 2),
            "n_samples": integer (optional, default: 100, for sample data),
            "n_features": integer (optional, default: 20, for sample data),
            "random_state": integer (optional, default: 42),
            "scale_features": boolean (optional, default: true),
            "business_context": object (optional)
        }
    """
    # Set CORS headers for browser compatibility
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)

    headers = {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json'
    }
    
    try:
        # Handle GET request for health check
        if request.method == 'GET':
            logger.info("Health check request received")
            
            # Test basic functionality
            try:
                test_data = generate_sample_data(n_samples=5, n_features=3, random_state=42)
                test_result = process_pca_request(test_data, n_components=2)
                
                health_info = {
                    "core_functionality": "operational" if test_result["status"] == "success" else "degraded",
                    "test_execution_time_ms": test_result.get("performance", {}).get("execution_time_ms", 0)
                }
                
                response = format_health_response(
                    platform="gcp-cloud-functions",
                    additional_info=health_info
                )
                
                return (json.dumps(response), 200, headers)
                
            except Exception as e:
                logger.error(f"Health check failed: {str(e)}")
                
                response = {
                    "status": "unhealthy",
                    "error": str(e),
                    "platform": "gcp-cloud-functions"
                }
                
                return (json.dumps(response), 503, headers)
        
        # Handle POST request for PCA analysis
        if request.method != 'POST':
            return (json.dumps({
                "status": "error",
                "error": "Method not allowed. Use POST for PCA analysis or GET for health check.",
                "platform": "gcp-cloud-functions"
            }), 405, headers)
        
        # Parse request data
        try:
            if hasattr(request, 'is_json') and request.is_json:
                request_data = request.get_json()
            else:
                # Handle raw data
                if hasattr(request, 'data'):
                    request_data = json.loads(request.data.decode('utf-8'))
                else:
                    request_data = json.loads(request.get_data(as_text=True))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.error(f"Invalid JSON in request: {str(e)}")
            return (json.dumps({
                "status": "error",
                "error": "Invalid JSON format",
                "help": "Send Content-Type: application/json with valid JSON body",
                "platform": "gcp-cloud-functions"
            }), 400, headers)
        
        if not request_data:
            return (json.dumps({
                "status": "error",
                "error": "Empty request body",
                "example": {
                    "use_sample_data": True,
                    "n_components": 5,
                    "n_features": 20
                },
                "platform": "gcp-cloud-functions"
            }), 400, headers)
        
        logger.info(f"Processing PCA request: {len(str(request_data))} bytes")
        
        # Handle different data input methods
        if request_data.get('gcs_bucket') and request_data.get('gcs_file_path'):
            # Load data from Google Cloud Storage
            bucket_name = request_data['gcs_bucket']
            file_path = request_data['gcs_file_path']
            logger.info(f"Loading sensor data from GCS: gs://{bucket_name}/{file_path}")
            
            try:
                file_data = load_dataset_from_gcs(bucket_name, file_path)
                data = file_data['data']
                business_context = file_data['business_context']
                logger.info(f"Loaded from GCS: {data.shape[0]} readings, {data.shape[1]} sensors")
            except Exception as e:
                logger.error(f"Failed to load from GCS: {str(e)}")
                return (json.dumps({
                    "status": "error",
                    "error": {
                        "type": "GCSLoadError",
                        "message": f"Failed to load data from gs://{bucket_name}/{file_path}: {str(e)}",
                        "platform": "gcp-cloud-functions"
                    },
                    "help": "Ensure bucket exists, file is accessible, and function has storage permissions"
                }), 400, headers)
                
        elif request_data.get('use_sample_data', False):
            logger.info("Generating synthetic sensor data")
            
            # Check for coffee shop sample request
            if request_data.get('coffee_shop_sample', False):
                coffee_data = create_coffee_shop_sample(
                    location=request_data.get('location', 'downtown'),
                    hours=request_data.get('hours', 24),
                    sensor_types=request_data.get('sensor_types')
                )
                # Convert list back to numpy array for PCA processing
                import numpy as np
                data = np.array(coffee_data['data'])
                business_context = coffee_data['business_context']
                logger.info(f"Generated coffee shop sample: {data.shape[0]} readings, {data.shape[1]} sensors")
            else:
                # Generate basic synthetic data
                data = generate_sample_data(
                    n_samples=request_data.get('n_samples', 100),
                    n_features=request_data.get('n_features', 20),  # Default to 20 sensors
                    n_redundant=request_data.get('n_redundant', 8),
                    n_informative=request_data.get('n_informative', 12),
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
                return (json.dumps({
                    "status": "error",
                    "error": "Missing 'data' field in request",
                    "help": "Either provide 'data' array or set 'use_sample_data': true",
                    "example_data": [[1.2, 2.3, 3.1], [1.1, 2.4, 3.2], [1.3, 2.1, 3.0]],
                    "platform": "gcp-cloud-functions"
                }), 400, headers)
            
            logger.info("Validating uploaded sensor data")
            data = validate_input_data(request_data['data'])
            business_context = request_data.get('business_context', {})
            logger.info(f"Validated data: {data.shape}")
        
        # Process PCA request
        logger.info(f"Starting PCA analysis: {data.shape[0]} samples, {data.shape[1]} features")
        
        pca_results = process_pca_request(
            data=data,
            n_components=request_data.get('n_components', 5),  # Default to 5 components for sensor reduction
            scale_features=request_data.get('scale_features', True)
        )
        
        logger.info(f"PCA completed in {pca_results.get('performance', {}).get('execution_time_ms', 0):.1f}ms")
        
        # Format response with business insights
        formatted_response = format_response(
            pca_results=pca_results,
            platform="gcp-cloud-functions",
            include_raw_data=request_data.get('include_raw_data', False),
            business_context=business_context
        )
        
        # Return appropriate HTTP status
        if pca_results['status'] == 'success':
            return (json.dumps(formatted_response), 200, headers)
        else:
            return (json.dumps(formatted_response), 400, headers)
            
    except Exception as e:
        logger.error(f"Unexpected error in PCA analysis: {str(e)}", exc_info=True)
        
        error_response = {
            "status": "error",
            "error": {
                "type": type(e).__name__,
                "message": str(e),
                "platform": "gcp-cloud-functions"
            },
            "help": "Check Cloud Functions logs for detailed error information"
        }
        
        return (json.dumps(error_response), 500, headers)


# For local testing with functions-framework
# Install: pip install functions-framework
# Run: functions-framework --target=sensorscope_pca --debug
# Test endpoint: http://localhost:8080