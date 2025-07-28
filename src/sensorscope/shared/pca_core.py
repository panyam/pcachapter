"""
Core PCA processing logic for serverless implementations.
Universal module that works identically across all deployment platforms.

Maya's Note: This is the heart of the sensor redundancy analysis - 
pure mathematical logic that doesn't care about clouds or coffee shops.
"""

import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import time
import psutil
import os
from typing import Dict, Any, Union, List


def process_pca_request(data: Union[List[List[float]], np.ndarray], 
                       n_components: int = 2, 
                       scale_features: bool = True) -> Dict[str, Any]:
    """
    Perform PCA analysis on input data with comprehensive error handling.
    
    This function handles the core PCA computation that Maya uses to identify
    redundant sensors in coffee shop operations. It works the same whether
    running on a laptop or in the cloud.
    
    Args:
        data: Input dataset (n_samples, n_features) - like sensor readings
        n_components: Number of principal components to extract
        scale_features: Whether to standardize features before PCA (recommended)
        
    Returns:
        dict: Analysis results including transformed data and statistics
        
    Example:
        >>> data = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        >>> result = process_pca_request(data, n_components=2)
        >>> print(result['explained_variance_ratio'])
    """
    start_time = time.time()
    
    # Memory monitoring (works on most platforms)
    try:
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    except:
        initial_memory = 0  # Fallback for restricted environments
    
    try:
        # Input validation and conversion
        data = np.array(data, dtype=np.float64)
        
        if data.ndim != 2:
            raise ValueError("Data must be 2-dimensional (samples × features)")
        
        n_samples, n_features = data.shape
        
        # Check for sufficient data
        if n_samples < 2:
            raise ValueError(f"Need at least 2 samples for PCA, got {n_samples}")
            
        if n_features < 1:
            raise ValueError(f"Need at least 1 feature for PCA, got {n_features}")
        
        # Validate n_components parameter
        max_components = min(n_samples, n_features)
        if n_components > max_components:
            raise ValueError(f"n_components ({n_components}) cannot exceed "
                           f"min(n_samples, n_features) = {max_components}")
        
        if n_components < 1:
            raise ValueError(f"n_components must be at least 1, got {n_components}")
        
        # Check for constant features (would cause scaling issues)
        feature_vars = np.var(data, axis=0)
        constant_features = np.where(feature_vars == 0)[0]
        if len(constant_features) > 0:
            raise ValueError(f"Features {constant_features.tolist()} have zero variance. "
                           "Remove constant features before PCA analysis.")
        
        # Feature scaling (recommended for sensor data with different units)
        if scale_features:
            scaler = StandardScaler()
            data_scaled = scaler.fit_transform(data)
            scaling_mean = scaler.mean_.tolist()
            scaling_std = scaler.scale_.tolist()
        else:
            data_scaled = data
            scaling_mean = None
            scaling_std = None
        
        # PCA computation - the core mathematical operation
        pca = PCA(n_components=n_components)
        data_transformed = pca.fit_transform(data_scaled)
        
        # Performance metrics
        execution_time = (time.time() - start_time) * 1000  # milliseconds
        
        try:
            peak_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_used = peak_memory - initial_memory
        except:
            peak_memory = 0
            memory_used = 0
        
        # Prepare comprehensive results
        results = {
            "status": "success",
            "input_shape": [n_samples, n_features],
            "output_shape": list(data_transformed.shape),
            "explained_variance_ratio": pca.explained_variance_ratio_.tolist(),
            "total_variance_explained": float(np.sum(pca.explained_variance_ratio_)),
            "principal_components": pca.components_.tolist(),
            "transformed_data": data_transformed.tolist(),
            "scaling_applied": scale_features,
            "performance": {
                "execution_time_ms": round(execution_time, 2),
                "memory_used_mb": round(memory_used, 2),
                "peak_memory_mb": round(peak_memory, 2)
            },
            "metadata": {
                "n_components_requested": n_components,
                "n_components_actual": int(pca.n_components_),
                "scaling_parameters": {
                    "mean": scaling_mean,
                    "std": scaling_std
                } if scale_features else None
            }
        }
        
        return results
        
    except Exception as e:
        # Comprehensive error handling with timing information
        execution_time = (time.time() - start_time) * 1000
        
        error_result = {
            "status": "error",
            "error_type": type(e).__name__,
            "error_message": str(e),
            "input_info": {
                "data_type": str(type(data)),
                "data_shape": getattr(data, 'shape', 'unknown'),
                "n_components_requested": n_components,
                "scale_features": scale_features
            },
            "performance": {
                "execution_time_ms": round(execution_time, 2)
            }
        }
        
        return error_result


def validate_pca_results(results: Dict[str, Any]) -> bool:
    """
    Validate PCA results for consistency and correctness.
    
    Maya's validation checklist - ensures results make mathematical sense
    before making business decisions about sensor optimization.
    
    Args:
        results: Output from process_pca_request
        
    Returns:
        bool: True if results pass validation checks
        
    Raises:
        ValueError: If validation fails with specific error message
    """
    if results["status"] != "success":
        raise ValueError(f"Cannot validate failed PCA: {results.get('error_message', 'Unknown error')}")
    
    # Check variance ratios
    variance_ratios = results["explained_variance_ratio"]
    
    # Should be in descending order
    if not all(variance_ratios[i] >= variance_ratios[i+1] for i in range(len(variance_ratios)-1)):
        raise ValueError("Explained variance ratios should be in descending order")
    
    # Should sum to reasonable total (≤ 1.0, accounting for floating point precision)
    total_variance = sum(variance_ratios)
    if total_variance > 1.01:  # Allow small floating point error
        raise ValueError(f"Total explained variance {total_variance:.4f} exceeds 1.0")
    
    # Should have positive variance ratios
    if any(ratio < 0 for ratio in variance_ratios):
        raise ValueError("Explained variance ratios should be non-negative")
    
    # Check dimensional consistency
    input_shape = results["input_shape"]
    output_shape = results["output_shape"]
    
    if input_shape[0] != output_shape[0]:  # Same number of samples
        raise ValueError(f"Sample count mismatch: input {input_shape[0]}, output {output_shape[0]}")
    
    expected_components = min(input_shape[0], input_shape[1])
    if output_shape[1] > expected_components:
        raise ValueError(f"Too many components: {output_shape[1]} > max possible {expected_components}")
    
    # Check principal components shape
    components = results["principal_components"]
    expected_component_shape = [output_shape[1], input_shape[1]]  # [n_components, n_features]
    
    if len(components) != expected_component_shape[0]:
        raise ValueError(f"Wrong number of principal components: {len(components)} != {expected_component_shape[0]}")
    
    if len(components[0]) != expected_component_shape[1]:
        raise ValueError(f"Wrong component dimension: {len(components[0])} != {expected_component_shape[1]}")
    
    return True


def get_pca_insights(results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate business-friendly insights from PCA results.
    
    Translates Maya's mathematical results into actionable business intelligence
    about sensor redundancy and cost optimization opportunities.
    
    Args:
        results: Successful PCA analysis results
        
    Returns:
        dict: Business insights and recommendations
    """
    if results["status"] != "success":
        return {
            "insights": "No insights available - PCA analysis failed",
            "recommendations": []
        }
    
    variance_ratios = results["explained_variance_ratio"]
    total_variance = results["total_variance_explained"]
    n_original = results["input_shape"][1]
    n_components = results["output_shape"][1]
    
    # Calculate insights
    insights = {
        "dimensionality_reduction": {
            "original_dimensions": n_original,
            "reduced_dimensions": n_components,
            "reduction_ratio": round((n_original - n_components) / n_original, 3),
            "information_preserved": round(total_variance, 3)
        },
        "variance_analysis": {
            "first_component_importance": round(variance_ratios[0], 3),
            "diminishing_returns": round(variance_ratios[0] / variance_ratios[-1], 2) if len(variance_ratios) > 1 else 1.0,
            "component_contributions": [round(ratio, 3) for ratio in variance_ratios]
        },
        "business_impact": []
    }
    
    # Generate business recommendations
    recommendations = []
    
    # High information preservation suggests successful reduction
    if total_variance >= 0.8:
        recommendations.append(f"Excellent: {n_components} components preserve {total_variance:.1%} of information")
    elif total_variance >= 0.6:
        recommendations.append(f"Good: {n_components} components preserve {total_variance:.1%} of information")
    else:
        recommendations.append(f"Consider more components: only {total_variance:.1%} information preserved")
    
    # Sensor cost optimization insights
    potential_savings = (n_original - n_components) / n_original
    if potential_savings > 0.3:
        recommendations.append(f"High cost savings potential: could reduce sensors by {potential_savings:.1%}")
    
    # Component importance insights
    if variance_ratios[0] > 0.5:
        recommendations.append("First component is dominant - one key operational factor")
    
    if len(variance_ratios) > 1 and variance_ratios[1] > 0.2:
        recommendations.append("Second component is significant - two key operational factors")
    
    insights["recommendations"] = recommendations
    
    return insights