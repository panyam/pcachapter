"""
Response formatting utilities for consistent API responses across platforms.
Standardizes output format whether running locally or in any cloud provider.

Maya's Note: Ensures business stakeholders get the same information format
regardless of which cloud platform is processing their sensor data.
"""

from typing import Dict, Any, Optional
import json
from datetime import datetime


def format_response(pca_results: Dict[str, Any], 
                   platform: str = "unknown",
                   include_raw_data: bool = False,
                   business_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Format PCA results for consistent API responses across all platforms.
    
    Creates standardized response format with business insights and
    technical details appropriate for both engineers and business users.
    
    Args:
        pca_results: Raw results from pca_core.process_pca_request()
        platform: Deployment platform identifier
        include_raw_data: Whether to include full transformed data
        business_context: Additional business context for interpretation
        
    Returns:
        dict: Formatted response ready for JSON serialization
    """
    
    # Start with base response structure
    response = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "platform": platform,
        "service": "serverless-pca",
        "version": "1.0.0"
    }
    
    if pca_results["status"] == "success":
        # Format successful PCA response
        response.update({
            "status": "success",
            "analysis": {
                "input_dimensions": pca_results["input_shape"],
                "output_dimensions": pca_results["output_shape"],
                "variance_analysis": {
                    "explained_variance_ratio": pca_results["explained_variance_ratio"],
                    "total_variance_explained": round(pca_results["total_variance_explained"], 4),
                    "variance_percentages": [round(ratio * 100, 2) for ratio in pca_results["explained_variance_ratio"]]
                },
                "principal_components": pca_results["principal_components"],
                "configuration": {
                    "scaling_applied": pca_results["scaling_applied"],
                    "n_components": pca_results["metadata"]["n_components_requested"]
                }
            },
            "performance": pca_results["performance"],
            "business_insights": _generate_business_insights(pca_results, business_context)
        })
        
        # Include transformed data if requested (careful with large datasets)
        if include_raw_data:
            response["analysis"]["transformed_data"] = pca_results["transformed_data"]
        else:
            # Include just sample of transformed data for verification
            transformed_data = pca_results["transformed_data"]
            if len(transformed_data) > 5:
                response["analysis"]["sample_transformed_data"] = {
                    "first_5_samples": transformed_data[:5],
                    "total_samples": len(transformed_data),
                    "note": "Full transformed data available with include_raw_data=true"
                }
            else:
                response["analysis"]["transformed_data"] = transformed_data
    
    else:
        # Format error response
        response.update({
            "status": "error",
            "error": {
                "type": pca_results["error_type"],
                "message": pca_results["error_message"],
                "input_info": pca_results.get("input_info", {}),
                "timestamp": response["timestamp"]
            },
            "performance": pca_results.get("performance", {}),
            "troubleshooting": _generate_error_guidance(pca_results)
        })
    
    return response


def format_health_response(platform: str = "unknown", 
                          additional_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Format health check response for service monitoring.
    
    Args:
        platform: Platform identifier
        additional_info: Extra platform-specific information
        
    Returns:
        dict: Health check response
    """
    response = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "platform": platform,
        "service": "serverless-pca",
        "version": "1.0.0",
        "endpoints": {
            "pca_analysis": "/pca",
            "health_check": "/health"
        },
        "capabilities": [
            "Multi-dimensional PCA analysis",
            "Feature scaling and normalization", 
            "Business insight generation",
            "Cross-platform compatibility"
        ]
    }
    
    if additional_info:
        response["platform_info"] = additional_info
        
    return response


def _generate_business_insights(pca_results: Dict[str, Any], 
                               context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Generate business-friendly insights from PCA results.
    
    Translates technical PCA output into actionable business intelligence
    that Maya can present to coffee shop management.
    """
    variance_ratios = pca_results["explained_variance_ratio"]
    total_variance = pca_results["total_variance_explained"]
    original_dims = pca_results["input_shape"][1]
    reduced_dims = pca_results["output_shape"][1]
    
    insights = {
        "dimensionality_reduction": {
            "summary": f"Reduced {original_dims} measurements to {reduced_dims} key factors",
            "information_preserved": f"{total_variance:.1%}",
            "potential_sensor_reduction": f"{(original_dims - reduced_dims) / original_dims:.1%}"
        },
        "key_findings": [],
        "recommendations": [],
        "cost_impact": {}
    }
    
    # Generate key findings based on results
    if total_variance >= 0.9:
        insights["key_findings"].append(
            f"Excellent dimensionality reduction: {reduced_dims} components capture {total_variance:.1%} of variation"
        )
        insights["recommendations"].append(
            f"Strong candidate for sensor optimization - could reduce to {reduced_dims} primary sensors"
        )
    elif total_variance >= 0.75:
        insights["key_findings"].append(
            f"Good dimensionality reduction: {reduced_dims} components capture {total_variance:.1%} of variation"
        )
        insights["recommendations"].append(
            f"Moderate sensor optimization opportunity - {reduced_dims} sensors capture most information"
        )
    elif total_variance >= 0.6:
        insights["key_findings"].append(
            f"Moderate dimensionality reduction: {reduced_dims} components capture {total_variance:.1%} of variation"
        )
        insights["recommendations"].append(
            f"Limited sensor optimization - may need {reduced_dims + 1} sensors to maintain data quality"
        )
    else:
        insights["key_findings"].append(
            f"Limited dimensionality reduction: {reduced_dims} components only capture {total_variance:.1%} of variation"
        )
        insights["recommendations"].append(
            "Sensor data may not have strong redundancy patterns - minimal optimization opportunity"
        )
    
    # Component importance analysis
    if len(variance_ratios) >= 1:
        first_component = variance_ratios[0]
        if first_component > 0.6:
            insights["key_findings"].append(
                f"One dominant operational factor explains {first_component:.1%} of sensor variation"
            )
        elif first_component > 0.4:
            insights["key_findings"].append(
                f"Primary operational factor explains {first_component:.1%} of sensor variation"
            )
    
    if len(variance_ratios) >= 2:
        second_component = variance_ratios[1]
        if second_component > 0.2:
            insights["key_findings"].append(
                f"Secondary factor explains additional {second_component:.1%} of variation"
            )
    
    # Cost impact analysis (if context provided)
    if context and "cost_per_sensor" in context:
        cost_per_sensor = context["cost_per_sensor"]
        current_cost = original_dims * cost_per_sensor
        optimized_cost = reduced_dims * cost_per_sensor
        potential_savings = current_cost - optimized_cost
        
        insights["cost_impact"] = {
            "current_annual_cost": f"${current_cost:,.0f}",
            "optimized_annual_cost": f"${optimized_cost:,.0f}",  
            "potential_annual_savings": f"${potential_savings:,.0f}",
            "savings_percentage": f"{potential_savings/current_cost:.1%}"
        }
        
        if potential_savings > 0:
            insights["recommendations"].append(
                f"Potential cost savings: ${potential_savings:,.0f} annually ({potential_savings/current_cost:.1%})"
            )
    
    return insights


def _generate_error_guidance(error_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate helpful troubleshooting guidance for common errors.
    """
    error_type = error_results.get("error_type", "Unknown")
    error_message = error_results.get("error_message", "")
    
    guidance = {
        "common_solutions": [],
        "next_steps": [],
        "documentation": "See project README.md for detailed troubleshooting"
    }
    
    # Provide specific guidance based on error type
    if error_type == "ValueError":
        if "2-dimensional" in error_message:
            guidance["common_solutions"] = [
                "Ensure data is formatted as [[row1], [row2], ...] with samples as rows",
                "Single feature data should be shaped as [[x1], [x2], ...] not [x1, x2, ...]",
                "Convert 1D arrays using data.reshape(-1, 1) for single feature analysis"
            ]
        elif "n_components" in error_message:
            guidance["common_solutions"] = [
                "Reduce n_components to be less than min(n_samples, n_features)",
                "Increase sample size or reduce requested components",
                "For small datasets, try n_components=1 or 2"
            ]
        elif "zero variance" in error_message:
            guidance["common_solutions"] = [
                "Remove constant features (columns with same value for all samples)",
                "Check for data import issues that might create constant columns",
                "Add small amount of noise to constant features if scientifically appropriate"
            ]
    
    elif error_type == "TypeError":
        guidance["common_solutions"] = [
            "Ensure all data values are numeric (no text or missing values)",
            "Convert string numbers to floats: [[float(x) for x in row] for row in data]",
            "Replace missing values with appropriate numeric substitutes"
        ]
    
    # General guidance
    guidance["next_steps"] = [
        "Validate input data format using the data validation examples",
        "Test with sample data first: {\"use_sample_data\": true}",
        "Check the health endpoint to verify service is running correctly",
        "Review the business context to ensure PCA is appropriate for your use case"
    ]
    
    return guidance


def create_sample_responses() -> Dict[str, Dict[str, Any]]:
    """
    Create sample responses for testing and documentation.
    
    Returns example responses for successful analysis, errors, and health checks.
    """
    
    # Successful PCA analysis response
    success_response = {
        "timestamp": "2024-01-15T10:30:45.123Z",
        "platform": "local-flask",
        "service": "serverless-pca", 
        "version": "1.0.0",
        "status": "success",
        "analysis": {
            "input_dimensions": [100, 5],
            "output_dimensions": [100, 2],
            "variance_analysis": {
                "explained_variance_ratio": [0.4832, 0.2661],
                "total_variance_explained": 0.7493,
                "variance_percentages": [48.32, 26.61]
            },
            "principal_components": [
                [-0.1234, 0.5678, -0.9012, 0.3456, -0.7890],
                [0.2345, -0.6789, 0.0123, -0.4567, 0.8901]
            ],
            "configuration": {
                "scaling_applied": True,
                "n_components": 2
            },
            "sample_transformed_data": {
                "first_5_samples": [
                    [-1.2345, 0.6789],
                    [0.9876, -1.3456], 
                    [2.1234, 1.7890],
                    [-0.5432, -0.9876],
                    [1.6789, 0.2345]
                ],
                "total_samples": 100,
                "note": "Full transformed data available with include_raw_data=true"
            }
        },
        "performance": {
            "execution_time_ms": 12.34,
            "memory_used_mb": 15.6,
            "peak_memory_mb": 67.8
        },
        "business_insights": {
            "dimensionality_reduction": {
                "summary": "Reduced 5 measurements to 2 key factors",
                "information_preserved": "74.9%", 
                "potential_sensor_reduction": "60.0%"
            },
            "key_findings": [
                "Good dimensionality reduction: 2 components capture 74.9% of variation",
                "Primary operational factor explains 48.3% of sensor variation",
                "Secondary factor explains additional 26.6% of variation"
            ],
            "recommendations": [
                "Moderate sensor optimization opportunity - 2 sensors capture most information"
            ]
        }
    }
    
    # Error response
    error_response = {
        "timestamp": "2024-01-15T10:35:22.456Z",
        "platform": "local-flask", 
        "service": "serverless-pca",
        "version": "1.0.0",
        "status": "error",
        "error": {
            "type": "ValueError",
            "message": "Data must be 2-dimensional (samples × features)",
            "input_info": {
                "data_type": "<class 'list'>",
                "data_shape": "(10,)",
                "n_components_requested": 2,
                "scale_features": True
            },
            "timestamp": "2024-01-15T10:35:22.456Z"
        },
        "performance": {
            "execution_time_ms": 1.23
        },
        "troubleshooting": {
            "common_solutions": [
                "Ensure data is formatted as [[row1], [row2], ...] with samples as rows",
                "Single feature data should be shaped as [[x1], [x2], ...] not [x1, x2, ...]",
                "Convert 1D arrays using data.reshape(-1, 1) for single feature analysis"
            ],
            "next_steps": [
                "Validate input data format using the data validation examples",
                "Test with sample data first: {\"use_sample_data\": true}",
                "Check the health endpoint to verify service is running correctly"
            ],
            "documentation": "See project README.md for detailed troubleshooting"
        }
    }
    
    # Health check response
    health_response = {
        "status": "healthy",
        "timestamp": "2024-01-15T10:40:11.789Z",
        "platform": "local-flask",
        "service": "serverless-pca",
        "version": "1.0.0",
        "endpoints": {
            "pca_analysis": "/pca",
            "health_check": "/health"
        },
        "capabilities": [
            "Multi-dimensional PCA analysis",
            "Feature scaling and normalization",
            "Business insight generation", 
            "Cross-platform compatibility"
        ]
    }
    
    return {
        "success": success_response,
        "error": error_response,
        "health": health_response
    }