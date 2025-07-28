# SensorScope: Example

This example demonstrates the core serverless PCA pattern across multiple deployment targets: local development, AWS Lambda, Google Cloud Functions, and Azure Functions.

## Overview

**Business Context**: Sita's coffee shop sensor redundancy analysis - identifying which of 5 sensor types provide unique vs redundant information for cost optimization.

**Technical Goal**: Implement identical PCA functionality that works locally and deploys to any major cloud provider.

## Quick Start (5 Minutes)

### Prerequisites
- Python 3.9+ installed
- Git (for cloning)
- curl or similar HTTP client

### Local Setup

```bash
# 1. Navigate to this directory
```
cd src/sensorscope
```

# 2. Create virtual environment (essential for reproducibility)
```
pyenv virtualenv sensorscope
```

# 3. Activate virtual environment

```
pyenv activate sensorscope
```

# 4. Upgrade pip and install dependencies
```
pip install --upgrade pip
pip install -r requirements.txt
```

# 5. Start local server
cd local
python app.py
```

You should see:
```
Starting local PCA service...
Test endpoint: POST http://localhost:8000/pca
Health check: GET http://localhost:8000/health
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:8000
 * Running on http://[::1]:8000
```

### Test the Service

In a new terminal (keep the server running):

```bash
# Basic health check
curl http://localhost:8000/health

# PCA analysis with synthetic sensor data
curl -X POST http://localhost:8000/pca \
  -H "Content-Type: application/json" \
  -d '{
    "use_sample_data": true,
    "n_components": 2,
    "random_state": 42
  }'
```

### Expected Results
```json
{
  "status": "success",
  "input_shape": [100, 5],
  "output_shape": [100, 2],
  "explained_variance_ratio": [0.48324, 0.26606],
  "total_variance_explained": 0.7493,
  "platform": "local-flask",
  "performance": {
    "execution_time_ms": 12.34,
    "memory_used_mb": 15.6
  }
}
```

This means: **75% of sensor information is captured in just 2 dimensions**, suggesting Sita could reduce sensor complexity significantly.

## Project Structure

```
sensorscope/
├── README.md                     # This file
├── requirements.txt              # Python dependencies
├── shared/                       # Universal components
│   ├── pca_core.py              # Core PCA processing logic
│   ├── data_validation.py       # Input validation utilities
│   ├── response_formatter.py    # Standardized output formatting
│   └── sample_data.py           # Synthetic data generation
├── local/                       # Local development
│   ├── app.py                   # Flask application
│   ├── test_client.py           # Local testing utilities
│   └── requirements.txt         # Local-specific dependencies
├── aws/                         # AWS Lambda deployment
│   ├── README.md                # AWS setup instructions
│   ├── lambda_function.py       # AWS handler
│   ├── template.yaml            # SAM template
│   ├── requirements.txt         # Lambda dependencies
│   └── deploy.sh               # Deployment script
├── gcp/                        # Google Cloud Functions
│   ├── README.md               # GCP setup instructions
│   ├── main.py                 # GCP handler
│   ├── requirements.txt        # GCP dependencies
│   └── deploy.sh               # Deployment script
└── azure/                      # Azure Functions
    ├── README.md               # Azure setup instructions
    ├── __init__.py             # Azure handler
    ├── function.json           # Function configuration
    ├── requirements.txt        # Azure dependencies
    └── deploy.sh              # Deployment script
```

## API Reference

### POST /pca

Perform PCA analysis on input data.

**Request Body**:
```json
{
  "use_sample_data": boolean,     // Generate synthetic sensor data
  "n_components": integer,        // Number of principal components (default: 2)
  "n_samples": integer,           // Sample size if using synthetic data (default: 100)
  "n_features": integer,          // Feature count if using synthetic data (default: 5)
  "random_state": integer,        // Random seed for reproducibility (default: 42)
  "scale_features": boolean,      // Apply feature scaling (default: true)
  "data": array                   // Raw data if not using sample data
}
```

**Response**:
```json
{
  "status": "success|error",
  "input_shape": [samples, features],
  "output_shape": [samples, components],
  "explained_variance_ratio": [float, float, ...],
  "total_variance_explained": float,
  "principal_components": [[float, ...], ...],
  "transformed_data": [[float, ...], ...],
  "platform": "local-flask|aws-lambda|gcp-functions|azure-functions",
  "performance": {
    "execution_time_ms": float,
    "memory_used_mb": float
  }
}
```

### GET /health

Simple health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "platform": "local-flask",
  "message": "PCA service running locally"
}
```

## Testing Different Scenarios

### 1. Basic Sensor Analysis (Default)
```bash
curl -X POST http://localhost:8000/pca \
  -H "Content-Type: application/json" \
  -d '{"use_sample_data": true}'
```

### 2. Higher Dimensional Analysis
```bash
curl -X POST http://localhost:8000/pca \
  -H "Content-Type: application/json" \
  -d '{
    "use_sample_data": true,
    "n_features": 10,
    "n_components": 3
  }'
```

### 3. Larger Dataset
```bash
curl -X POST http://localhost:8000/pca \
  -H "Content-Type: application/json" \
  -d '{
    "use_sample_data": true,
    "n_samples": 1000,
    "n_features": 8,
    "n_components": 3
  }'
```

### 4. Custom Data
```bash
curl -X POST http://localhost:8000/pca \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      [1.2, 2.3, 3.1, 4.5, 5.2],
      [1.1, 2.4, 3.2, 4.6, 5.1],
      [1.3, 2.1, 3.0, 4.4, 5.3]
    ],
    "n_components": 2
  }'
```

## Cloud Deployments

After validating locally, deploy to your preferred cloud platform(s):

### AWS Lambda
```bash
cd aws
# Follow aws/README.md for detailed setup
./deploy.sh
```

### Google Cloud Functions
```bash
cd gcp  
# Follow gcp/README.md for detailed setup
./deploy.sh
```

### Azure Functions
```bash
cd azure
# Follow azure/README.md for detailed setup  
./deploy.sh
```

## Validation Testing

Test consistency across all platforms:

```bash
# Local testing utility
python local/test_client.py

# Cross-platform validation (after cloud deployment)
python test_all_platforms.py
```

Expected: Identical PCA results across all deployment targets within floating-point precision.

## Performance Benchmarks

Typical performance on standard hardware:

| Scenario | Dataset Size | Local Time | Memory Usage | Expected Cloud Time |
|----------|-------------|------------|--------------|-------------------|
| Basic (5→2D) | 100×5 | ~15ms | ~15MB | 150-300ms |
| Medium (10→3D) | 500×10 | ~45ms | ~25MB | 200-400ms |
| Large (20→5D) | 1000×20 | ~120ms | ~45MB | 300-600ms |

Note: Cloud times include cold start overhead. Warm function performance is closer to local times.

## Troubleshooting

### Common Issues

**Import Errors**:
```bash
# Ensure virtual environment is activated
which python  # Should show venv/bin/python

# Verify all packages installed
pip list | grep -E "(flask|scikit|numpy|pandas)"
```

**Port Already in Use**:
```bash
# Kill existing process on port 8000
lsof -i :8000
kill -9 [PID]

# Or change port in local/app.py:
# app.run(host='0.0.0.0', port=8001, debug=True)
```

**Memory Issues with Large Datasets**:
```bash
# Reduce dataset size for testing
curl -X POST http://localhost:8000/pca \
  -d '{"use_sample_data": true, "n_samples": 50, "n_features": 5}'
```

**JSON Format Errors**:
```bash
# Validate JSON before sending
echo '{"use_sample_data": true}' | jq .

# Use proper Content-Type header
curl -H "Content-Type: application/json" ...
```

### Development Tips

**Debug Mode**: The Flask app runs with `debug=True`, so changes auto-reload.

**Verbose Logging**: Check terminal output for detailed execution information.

**Memory Monitoring**: Responses include memory usage for optimization insights.

**Error Details**: Error responses include specific error types and messages.

## Next Steps

1. **Validate Local Setup**: Ensure works perfectly locally
2. **Choose Cloud Platform**: Pick AWS, GCP, or Azure based on your preference  
3. **Deploy and Test**: Follow cloud-specific README for deployment
4. **Cross-Platform Validation**: Confirm identical results everywhere
5. **Explore Examples**: Move to more complex IoT pipeline and large dataset examples

## Business Context

This example simulates Sita's sensor redundancy analysis:
- **5 sensor types** representing temperature, humidity, pressure, vibration, flow
- **2 principal components** capture 75% of variation
- **Result**: Potential to reduce 5 sensors to 2-3 key measurements
- **Cost savings**: 40-60% reduction in sensor infrastructure

The same pattern scales to Sita's full challenge: 20 sensor types across 47 locations, enabling data-driven decisions about sensor optimization.
