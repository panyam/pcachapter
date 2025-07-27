"""
Data validation and sample data generation for PCA analysis.
Handles input validation and creates realistic synthetic sensor data.

Maya's Note: This module ensures data quality before PCA analysis
and generates coffee shop sensor simulations for testing.
"""

import numpy as np
from sklearn.datasets import make_classification
from typing import Union, List, Dict, Any
import json
import pandas as pd
import os
from pathlib import Path


def generate_sample_data(n_samples: int = 100, 
                        n_features: int = 5, 
                        n_redundant: int = 2,
                        n_informative: int = 3,
                        random_state: int = 42) -> np.ndarray:
    """
    Generate synthetic sensor data resembling coffee shop measurements.
    
    Creates realistic sensor data with known redundancy patterns,
    perfect for testing Maya's sensor optimization algorithms.
    
    Args:
        n_samples: Number of sensor readings (like hourly measurements)
        n_features: Number of sensor types (temperature, humidity, etc.)
        n_redundant: Number of sensors providing redundant information
        n_informative: Number of sensors with unique information
        random_state: Random seed for reproducible results
        
    Returns:
        numpy.ndarray: Synthetic sensor data (n_samples, n_features)
        
    Example:
        >>> data = generate_sample_data(n_samples=50, n_features=8)
        >>> print(f"Generated {data.shape[0]} readings from {data.shape[1]} sensors")
    """
    # Validate parameters
    if n_samples < 2:
        raise ValueError(f"Need at least 2 samples, got {n_samples}")
    
    if n_features < 1:
        raise ValueError(f"Need at least 1 feature, got {n_features}")
    
    if n_redundant + n_informative > n_features:
        # Adjust parameters to be valid
        n_informative = max(1, n_features - n_redundant)
        n_redundant = n_features - n_informative
    
    # Generate realistic sensor data using sklearn
    X, _ = make_classification(
        n_samples=n_samples,
        n_features=n_features,
        n_redundant=n_redundant,
        n_informative=n_informative,
        n_clusters_per_class=1,
        random_state=random_state,
        class_sep=0.8  # Moderate separation for realistic data
    )
    
    # Post-process to make data more sensor-like
    # Scale to realistic sensor ranges and add sensor-like characteristics
    
    # Simulate different sensor types with appropriate ranges
    sensor_configs = [
        {"name": "temperature", "min": 18.0, "max": 25.0, "noise": 0.1},
        {"name": "humidity", "min": 40.0, "max": 70.0, "noise": 0.2},  
        {"name": "pressure", "min": 1010.0, "max": 1025.0, "noise": 0.1},
        {"name": "vibration", "min": 0.1, "max": 2.0, "noise": 0.05},
        {"name": "flow_rate", "min": 2.0, "max": 8.0, "noise": 0.1},
        {"name": "sound_level", "min": 45.0, "max": 65.0, "noise": 0.3},
        {"name": "light_level", "min": 200.0, "max": 800.0, "noise": 10.0},
        {"name": "co2_level", "min": 400.0, "max": 1000.0, "noise": 5.0}
    ]
    
    # Apply realistic scaling to each feature
    for i in range(min(n_features, len(sensor_configs))):
        config = sensor_configs[i]
        
        # Normalize to 0-1 range first
        feature_min = X[:, i].min()
        feature_max = X[:, i].max()
        feature_range = feature_max - feature_min
        
        if feature_range > 0:
            X[:, i] = (X[:, i] - feature_min) / feature_range
        
        # Scale to sensor range
        sensor_range = config["max"] - config["min"]
        X[:, i] = X[:, i] * sensor_range + config["min"]
        
        # Add realistic sensor noise
        noise = np.random.normal(0, config["noise"], n_samples)
        X[:, i] = X[:, i] + noise
    
    # Handle any additional features beyond predefined sensors
    if n_features > len(sensor_configs):
        for i in range(len(sensor_configs), n_features):
            # Generic sensor scaling
            feature_min = X[:, i].min()
            feature_max = X[:, i].max()
            feature_range = feature_max - feature_min
            
            if feature_range > 0:
                X[:, i] = (X[:, i] - feature_min) / feature_range * 100  # 0-100 range
    
    return X


def validate_input_data(data: Union[List, np.ndarray, str]) -> np.ndarray:
    """
    Validate and convert input data to numpy array format.
    
    Handles various input formats and ensures data is suitable for PCA analysis.
    Provides helpful error messages when data doesn't meet requirements.
    
    Args:
        data: Input data in various formats (list, array, JSON string)
        
    Returns:
        numpy.ndarray: Validated data ready for PCA
        
    Raises:
        ValueError: If data format is invalid or unsuitable for PCA
        TypeError: If data type cannot be converted to numeric
        
    Example:
        >>> data = [[1, 2, 3], [4, 5, 6]]
        >>> validated = validate_input_data(data)
        >>> print(validated.shape)  # (2, 3)
    """
    # Handle JSON string input
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON string: {str(e)}")
    
    # Convert to numpy array
    try:
        data_array = np.array(data, dtype=np.float64)
    except (ValueError, TypeError) as e:
        raise TypeError(f"Cannot convert data to numeric array: {str(e)}")
    
    # Check dimensions
    if data_array.ndim == 0:
        raise ValueError("Data cannot be a scalar value")
    elif data_array.ndim == 1:
        raise ValueError("Data must be 2-dimensional (samples × features). "
                        "Got 1D array - reshape to (n_samples, 1) for single feature.")
    elif data_array.ndim > 2:
        raise ValueError(f"Data must be 2-dimensional, got {data_array.ndim} dimensions")
    
    n_samples, n_features = data_array.shape
    
    # Check for minimum requirements
    if n_samples < 2:
        raise ValueError(f"Need at least 2 samples for PCA analysis, got {n_samples}")
    
    if n_features < 1:
        raise ValueError(f"Need at least 1 feature for PCA analysis, got {n_features}")
    
    # Check for invalid values
    if np.any(np.isnan(data_array)):
        nan_count = np.sum(np.isnan(data_array))
        raise ValueError(f"Data contains {nan_count} NaN values. Remove or impute missing values.")
    
    if np.any(np.isinf(data_array)):
        inf_count = np.sum(np.isinf(data_array))
        raise ValueError(f"Data contains {inf_count} infinite values. Remove or cap extreme values.")
    
    # Check for constant features (will cause issues with scaling)
    feature_vars = np.var(data_array, axis=0)
    constant_features = np.where(feature_vars == 0)[0]
    
    if len(constant_features) > 0:
        raise ValueError(f"Features at indices {constant_features.tolist()} have zero variance. "
                        "Remove constant features or add variation to proceed with PCA.")
    
    # Warn about potential issues (but don't fail)
    warnings = []
    
    # Check for highly correlated features (not an error, but good to know)
    if n_features > 1:
        corr_matrix = np.corrcoef(data_array.T)
        high_corr_pairs = []
        
        for i in range(n_features):
            for j in range(i+1, n_features):
                if abs(corr_matrix[i, j]) > 0.95:
                    high_corr_pairs.append((i, j, corr_matrix[i, j]))
        
        if high_corr_pairs:
            warnings.append(f"Found {len(high_corr_pairs)} highly correlated feature pairs (|r| > 0.95)")
    
    # Check for extreme values (potential outliers)
    z_scores = np.abs((data_array - np.mean(data_array, axis=0)) / np.std(data_array, axis=0))
    extreme_values = np.sum(z_scores > 4)  # Values > 4 standard deviations
    
    if extreme_values > 0:
        warnings.append(f"Found {extreme_values} potential outliers (|z-score| > 4)")
    
    # Store warnings in array metadata (if supported)
    if warnings:
        if hasattr(data_array, '__dict__'):
            data_array.validation_warnings = warnings
    
    return data_array


def get_data_summary(data: np.ndarray) -> Dict[str, Any]:
    """
    Generate descriptive statistics and data quality summary.
    
    Provides Maya with insights about the data before PCA analysis,
    helping identify potential issues or interesting patterns.
    
    Args:
        data: Validated numpy array (n_samples, n_features)
        
    Returns:
        dict: Comprehensive data summary including statistics and quality metrics
    """
    if data.ndim != 2:
        return {"error": "Data must be 2-dimensional for summary"}
    
    n_samples, n_features = data.shape
    
    # Basic statistics
    summary = {
        "shape": {
            "n_samples": n_samples,
            "n_features": n_features,
            "total_values": n_samples * n_features
        },
        "statistics": {
            "mean": np.mean(data, axis=0).tolist(),
            "std": np.std(data, axis=0).tolist(),
            "min": np.min(data, axis=0).tolist(),
            "max": np.max(data, axis=0).tolist(),
            "median": np.median(data, axis=0).tolist()
        },
        "data_quality": {
            "missing_values": int(np.sum(np.isnan(data))),
            "infinite_values": int(np.sum(np.isinf(data))),
            "constant_features": np.where(np.var(data, axis=0) == 0)[0].tolist(),
            "feature_ranges": (np.max(data, axis=0) - np.min(data, axis=0)).tolist()
        }
    }
    
    # Correlation analysis
    if n_features > 1:
        corr_matrix = np.corrcoef(data.T)
        
        # Find high correlations
        high_correlations = []
        for i in range(n_features):
            for j in range(i+1, n_features):
                corr_val = corr_matrix[i, j]
                if abs(corr_val) > 0.7:  # Significant correlation
                    high_correlations.append({
                        "feature_pair": [i, j],
                        "correlation": round(float(corr_val), 3)
                    })
        
        summary["correlation_analysis"] = {
            "max_correlation": float(np.max(np.abs(corr_matrix - np.eye(n_features)))),
            "mean_absolute_correlation": float(np.mean(np.abs(corr_matrix - np.eye(n_features)))),
            "high_correlations": high_correlations
        }
    
    # PCA suitability assessment
    suitability_score = 0
    suitability_notes = []
    
    # Check sample size
    if n_samples >= 50:
        suitability_score += 2
        suitability_notes.append("Good sample size for PCA")
    elif n_samples >= 10:
        suitability_score += 1
        suitability_notes.append("Adequate sample size for PCA")
    else:
        suitability_notes.append("Small sample size - PCA results may be unstable")
    
    # Check feature correlations
    if n_features > 1:
        if summary["correlation_analysis"]["max_correlation"] > 0.5:
            suitability_score += 2
            suitability_notes.append("Strong feature correlations - good for PCA")
        elif summary["correlation_analysis"]["max_correlation"] > 0.3:
            suitability_score += 1
            suitability_notes.append("Moderate feature correlations - PCA may be beneficial")
        else:
            suitability_notes.append("Weak feature correlations - limited PCA benefit expected")
    
    # Check feature scaling consistency
    feature_ranges = np.array(summary["data_quality"]["feature_ranges"])
    range_ratio = np.max(feature_ranges) / np.min(feature_ranges) if np.min(feature_ranges) > 0 else float('inf')
    
    if range_ratio > 100:
        suitability_notes.append("Large differences in feature scales - scaling recommended")
    elif range_ratio > 10:
        suitability_notes.append("Moderate differences in feature scales - scaling may help")
    else:
        suitability_score += 1
        suitability_notes.append("Similar feature scales - good for PCA")
    
    summary["pca_suitability"] = {
        "score": min(suitability_score, 5),  # Cap at 5
        "max_score": 5,
        "notes": suitability_notes,
        "recommendation": "Proceed with PCA" if suitability_score >= 3 else "PCA may have limited benefit"
    }
    
    return summary


def create_coffee_shop_sample(location: str = "downtown", 
                             hours: int = 24,
                             sensor_types: List[str] = None) -> Dict[str, Any]:
    """
    Create realistic coffee shop sensor data for testing.
    
    Generates synthetic data that resembles actual coffee shop operations,
    complete with daily patterns and realistic sensor correlations.
    
    Args:
        location: Coffee shop location type (affects patterns)
        hours: Number of hours of data to generate
        sensor_types: List of sensor types to include
        
    Returns:
        dict: Complete dataset with metadata and sensor data
    """
    if sensor_types is None:
        # Default to Maya's full 20-sensor coffee shop scenario
        sensor_types = [
            "temperature", "humidity", "pressure", "vibration", "flow_rate",
            "sound_level", "light_level", "co2_level", "door_sensor", "wifi_connections",
            "equipment_temp", "steam_pressure", "water_flow", "power_consumption", "customer_count",
            "ambient_noise", "air_quality", "motion_detector", "refrigeration_temp", "grinder_vibration"
        ]
    
    n_samples = hours * 4  # 15-minute intervals
    n_features = len(sensor_types)
    
    # Generate base data with realistic patterns
    data = generate_sample_data(
        n_samples=n_samples,
        n_features=n_features,
        n_redundant=min(2, n_features//2),
        n_informative=max(1, n_features - n_features//2),
        random_state=42
    )
    
    # Add time-based patterns (daily cycles, rush hours)
    time_hours = np.linspace(0, hours, n_samples)
    
    for i, sensor in enumerate(sensor_types):
        if sensor == "temperature":
            # Temperature varies with time of day and equipment usage
            daily_pattern = 2 * np.sin(2 * np.pi * time_hours / 24) 
            rush_pattern = 1.5 * (np.sin(2 * np.pi * (time_hours - 7) / 12) + 
                                 np.sin(2 * np.pi * (time_hours - 17) / 12))
            data[:, i] += daily_pattern + np.maximum(0, rush_pattern)
            
        elif sensor == "vibration":
            # Higher vibration during rush hours
            rush_hours = ((time_hours % 24 >= 7) & (time_hours % 24 <= 9)) | \
                        ((time_hours % 24 >= 17) & (time_hours % 24 <= 19))
            data[rush_hours, i] += np.random.normal(0.5, 0.2, np.sum(rush_hours))
    
    # Create comprehensive metadata
    dataset = {
        "metadata": {
            "location": location,
            "duration_hours": hours,
            "sampling_interval_minutes": 15,
            "sensor_types": sensor_types,
            "generation_timestamp": "synthetic",
            "description": f"Synthetic coffee shop sensor data for {location} location"
        },
        "data": data.tolist(),
        "summary": get_data_summary(data),
        "business_context": {
            "purpose": "Sensor redundancy analysis for cost optimization",
            "expected_redundancies": ["temperature sensors may correlate with equipment vibration",
                                    "humidity and temperature often correlated"],
            "cost_per_sensor_annual": 250,  # Realistic sensor cost
            "potential_savings": f"Up to ${len(sensor_types) * 250 * 0.3:.0f} annually"
        }
    }
    
    return dataset


def save_sample_dataset_to_file(file_path: str, dataset_type: str = "coffee_shop", **kwargs) -> Dict[str, Any]:
    """
    Generate and save a sample dataset to file for upload testing.
    
    Creates realistic sensor data files that Maya could use to test
    file-based data processing workflows.
    
    Args:
        file_path: Path where to save the dataset file
        dataset_type: Type of dataset ("coffee_shop", "basic", "complex")
        **kwargs: Additional parameters for dataset generation
        
    Returns:
        dict: Dataset metadata and file information
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Generate dataset based on type
    if dataset_type == "coffee_shop":
        dataset = create_coffee_shop_sample(
            location=kwargs.get('location', 'downtown'),
            hours=kwargs.get('hours', 48),  # 2 days of data
            sensor_types=kwargs.get('sensor_types')
        )
        data = np.array(dataset['data'])
        metadata = dataset['metadata']
        business_context = dataset['business_context']
        
    elif dataset_type == "basic":
        data = generate_sample_data(
            n_samples=kwargs.get('n_samples', 200),
            n_features=kwargs.get('n_features', 20),
            n_redundant=kwargs.get('n_redundant', 8),
            n_informative=kwargs.get('n_informative', 12),
            random_state=kwargs.get('random_state', 42)
        )
        metadata = {
            "dataset_type": "basic_synthetic",
            "description": "Basic synthetic sensor data for PCA testing"
        }
        business_context = {
            "cost_per_sensor_annual": 250,
            "analysis_type": "sensor_redundancy"
        }
        
    else:  # complex
        data = generate_sample_data(
            n_samples=kwargs.get('n_samples', 500),
            n_features=kwargs.get('n_features', 25),
            n_redundant=kwargs.get('n_redundant', 5),
            n_informative=kwargs.get('n_informative', 20),
            random_state=kwargs.get('random_state', 42)
        )
        metadata = {
            "dataset_type": "complex_synthetic", 
            "description": "Complex synthetic sensor data with minimal redundancy"
        }
        business_context = {
            "cost_per_sensor_annual": 300,
            "analysis_type": "sensor_redundancy"
        }
    
    # Create DataFrame with sensor column names
    if dataset_type == "coffee_shop":
        columns = kwargs.get('sensor_types') or [
            "temperature", "humidity", "pressure", "vibration", "flow_rate",
            "sound_level", "light_level", "co2_level", "door_sensor", "wifi_connections",
            "equipment_temp", "steam_pressure", "water_flow", "power_consumption", "customer_count",
            "ambient_noise", "air_quality", "motion_detector", "refrigeration_temp", "grinder_vibration"
        ]
    else:
        columns = [f"sensor_{i+1}" for i in range(data.shape[1])]
    
    df = pd.DataFrame(data, columns=columns[:data.shape[1]])
    
    # Add timestamp column for realism
    import datetime
    start_time = datetime.datetime.now() - datetime.timedelta(days=2)
    timestamps = [start_time + datetime.timedelta(minutes=15*i) for i in range(len(df))]
    df.insert(0, 'timestamp', timestamps)
    
    # Save to CSV
    df.to_csv(file_path, index=False)
    
    # Create metadata file
    metadata_path = file_path.replace('.csv', '_metadata.json')
    file_metadata = {
        "file_info": {
            "file_path": file_path,
            "file_size_mb": round(os.path.getsize(file_path) / 1024 / 1024, 2),
            "num_rows": len(df),
            "num_sensor_columns": data.shape[1],
            "columns": list(df.columns),
            "created_timestamp": datetime.datetime.now().isoformat()
        },
        "dataset_metadata": metadata,
        "business_context": business_context
    }
    
    with open(metadata_path, 'w') as f:
        json.dump(file_metadata, f, indent=2)
    
    return file_metadata


def load_dataset_from_file(file_path: str, timestamp_column: str = "timestamp") -> Dict[str, Any]:
    """
    Load sensor dataset from CSV file for PCA analysis.
    
    Handles Maya's uploaded sensor data files and prepares them
    for PCA processing with proper validation and formatting.
    
    Args:
        file_path: Path to the CSV file containing sensor data
        timestamp_column: Name of timestamp column to exclude from analysis
        
    Returns:
        dict: Processed dataset ready for PCA analysis
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is invalid
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset file not found: {file_path}")
    
    try:
        # Load CSV file
        df = pd.read_csv(file_path)
        
        # Remove timestamp column if present
        sensor_columns = [col for col in df.columns if col != timestamp_column]
        sensor_data = df[sensor_columns]
        
        # Convert to numpy array and validate
        data_array = validate_input_data(sensor_data.values)
        
        # Load metadata if available
        metadata_path = file_path.replace('.csv', '_metadata.json')
        metadata = {}
        business_context = {}
        
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                file_metadata = json.load(f)
                metadata = file_metadata.get('dataset_metadata', {})
                business_context = file_metadata.get('business_context', {})
        
        # Create summary
        data_summary = get_data_summary(data_array)
        
        return {
            "data": data_array,
            "metadata": {
                "source": "uploaded_file",
                "file_path": file_path,
                "sensor_columns": sensor_columns,
                "num_samples": data_array.shape[0],
                "num_sensors": data_array.shape[1],
                **metadata
            },
            "business_context": business_context,
            "data_summary": data_summary
        }
        
    except Exception as e:
        raise ValueError(f"Error processing dataset file {file_path}: {str(e)}")


def create_sample_datasets_directory(base_path: str = "./datasets") -> Dict[str, str]:
    """
    Create sample dataset files for testing file upload workflows.
    
    Generates the datasets Maya would use to test SensorScope's
    file processing capabilities.
    
    Args:
        base_path: Directory where to create sample files
        
    Returns:
        dict: Paths to created dataset files
    """
    datasets = {}
    
    # Create coffee shop dataset (realistic scenario)
    coffee_path = os.path.join(base_path, "coffee_shop_sensors.csv")
    coffee_metadata = save_sample_dataset_to_file(
        coffee_path, 
        dataset_type="coffee_shop",
        location="downtown",
        hours=48
    )
    datasets["coffee_shop"] = coffee_path
    
    # Create basic dataset (strong redundancy)
    basic_path = os.path.join(base_path, "basic_sensors.csv")
    basic_metadata = save_sample_dataset_to_file(
        basic_path,
        dataset_type="basic", 
        n_samples=200,
        n_features=15,
        n_redundant=8,
        random_state=42
    )
    datasets["basic"] = basic_path
    
    # Create complex dataset (minimal redundancy)
    complex_path = os.path.join(base_path, "complex_sensors.csv")
    complex_metadata = save_sample_dataset_to_file(
        complex_path,
        dataset_type="complex",
        n_samples=300,
        n_features=20,
        n_redundant=3,
        random_state=123
    )
    datasets["complex"] = complex_path
    
    return datasets


def load_dataset_from_gcs(bucket_name: str, file_path: str, timestamp_column: str = "timestamp") -> Dict[str, Any]:
    """
    Load sensor dataset from Google Cloud Storage for PCA analysis.
    
    Handles Maya's uploaded sensor data files from GCS bucket and prepares them
    for PCA processing with proper validation and formatting.
    
    Args:
        bucket_name: Name of the GCS bucket containing the dataset
        file_path: Path to the CSV file within the bucket
        timestamp_column: Name of timestamp column to exclude from analysis
        
    Returns:
        dict: Processed dataset ready for PCA analysis
        
    Raises:
        Exception: If file doesn't exist or can't be accessed
        ValueError: If file format is invalid
    """
    try:
        from google.cloud import storage
        import io
        
        # Initialize GCS client
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(file_path)
        
        # Check if file exists
        if not blob.exists():
            raise FileNotFoundError(f"Dataset file not found: gs://{bucket_name}/{file_path}")
        
        # Download CSV content
        csv_content = blob.download_as_text()
        
        # Load CSV from string
        df = pd.read_csv(io.StringIO(csv_content))
        
        # Remove timestamp column if present
        sensor_columns = [col for col in df.columns if col != timestamp_column]
        sensor_data = df[sensor_columns]
        
        # Convert to numpy array and validate
        data_array = validate_input_data(sensor_data.values)
        
        # Try to load metadata file
        metadata_path = file_path.replace('.csv', '_metadata.json')
        metadata = {}
        business_context = {}
        
        try:
            metadata_blob = bucket.blob(metadata_path)
            if metadata_blob.exists():
                metadata_content = metadata_blob.download_as_text()
                file_metadata = json.loads(metadata_content)
                metadata = file_metadata.get('dataset_metadata', {})
                business_context = file_metadata.get('business_context', {})
        except Exception:
            # Metadata file is optional
            pass
        
        # Create summary
        data_summary = get_data_summary(data_array)
        
        return {
            "data": data_array,
            "metadata": {
                "source": "gcs_bucket",
                "bucket_name": bucket_name,
                "file_path": file_path,
                "sensor_columns": sensor_columns,
                "num_samples": data_array.shape[0],
                "num_sensors": data_array.shape[1],
                **metadata
            },
            "business_context": business_context,
            "data_summary": data_summary
        }
        
    except ImportError:
        raise ValueError("google-cloud-storage package not available. Cannot load from GCS.")
    except Exception as e:
        raise ValueError(f"Error loading dataset from gs://{bucket_name}/{file_path}: {str(e)}")