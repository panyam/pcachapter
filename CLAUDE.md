# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive technical documentation project for creating a **Serverless PCA (Principal Component Analysis)** implementation chapter. Despite the "golang" directory name, this is a **Python-based serverless project** focused on machine learning and cloud architecture. The examples are designed to work across AWS, Google Cloud Platform, and Azure, giving readers flexibility in their cloud choice.

## Key Development Commands

The project uses Python 3.9+ and serverless architecture. Common commands will include:

```bash
# Python environment setup
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Local development
cd src/hello-world-pca/local && python app.py

# Cloud deployment (choose your platform)
cd src/hello-world-pca/aws && ./deploy.sh
cd src/hello-world-pca/gcp && ./deploy.sh
cd src/hello-world-pca/azure && ./deploy.sh

# Testing
pytest src/tests/unit/
pytest src/tests/integration/
```

## Architecture Overview

The chapter demonstrates **Serverless PCA** through a foundation example and three progressive use cases:

**Foundation**: Hello World PCA - Multi-cloud serverless function demonstrating basic PCA transformation
**Example 1**: Basic PCA Pipeline - Event-driven processing for IoT sensor data (~50MB)  
**Example 2**: Large Dataset Processing - Orchestrated workflows for NYC Taxi data (~1-2GB)
**Example 3**: Real-time PCA API - HTTP API with caching for stock market data

### Core Technologies

- **Cloud Functions**: AWS Lambda, GCP Cloud Functions, Azure Functions
- **Storage**: S3, Cloud Storage, Blob Storage (abstracted through unified interface)
- **ML Stack**: scikit-learn, numpy, pandas, pyarrow
- **Local Development**: Flask for testing before cloud deployment
- **Deployment**: Cloud-specific CLI tools with unified patterns

## Repository Structure

```
├── CHAPTER.md                 # Main chapter content
├── images/                    # Architecture diagrams and charts
└── src/                       # All executable code
    ├── hello-world-pca/       # Foundation example (local + 3 clouds)
    ├── examples/              # Three progressive examples
    ├── datasets/              # Data generation scripts  
    ├── infrastructure/        # Infrastructure templates
    └── tests/                 # Unit and integration tests
```

## Key Implementation Patterns

### Cloud-Agnostic Design
- **Universal PCA logic**: Same scikit-learn code across all clouds
- **Storage abstraction**: Unified interface for object storage operations
- **Event handling**: Standardized request/response patterns
- **Local-first development**: Test with Flask before cloud deployment

### Serverless Best Practices
- **Event-driven processing**: Storage triggers and HTTP endpoints
- **Cost optimization**: Right-sized resources, efficient processing
- **Memory management**: Stay within function memory limits
- **Error handling**: Robust retry strategies and logging
- **Target costs**: $0.01-$5 per transformation depending on data size

## Dataset Specifications

1. **IoT Sensors**: 50MB, 20 features, 100K records → sensor redundancy analysis
2. **NYC Taxi**: 1-2GB, 15+ features → geographical clustering and travel patterns  
3. **Stock Market**: Real-time via yfinance → portfolio risk and feature reduction

## Production Requirements

- **Error Handling**: Robust retry strategies, proper exception handling
- **Monitoring**: Cloud-native logging and metrics (CloudWatch, Cloud Logging, Azure Monitor)  
- **Security**: Proper IAM policies, data encryption, secure secrets management
- **Testing**: Unit tests for PCA logic, integration tests for cloud deployments
- **Documentation**: All code must be production-ready with comprehensive docstrings

## Development Notes

- **Cloud flexibility**: Examples work on reader's preferred cloud platform
- **Local development**: Always test locally before cloud deployment
- **Cost awareness**: Include cost estimates and optimization strategies
- **Reader experience**: Code should be copy-paste ready with clear instructions
- **Educational focus**: Emphasize serverless PCA concepts over cloud-specific features