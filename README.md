# Serverless PCA: Multi-Cloud Implementation Guide

This repository accompanies the "Serverless PCA" chapter, providing working implementations of Principal Component Analysis across AWS, Google Cloud Platform, and Azure serverless platforms.

## Quick Start

Get the Hello World PCA example running locally in under 5 minutes:

```bash
# 1. Clone and navigate to project
cd pcachapter

# 2. Set up Hello World PCA
cd src/hello-world-pca/local
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Run local server
python app.py

# 4. Test in another terminal
curl -X POST http://localhost:8000/pca \
  -H "Content-Type: application/json" \
  -d '{"use_sample_data": true, "n_components": 2}'
```

Expected output: PCA analysis results with ~75% variance explained from 5D→2D reduction.

## Project Structure

```
├── CHAPTER.md                    # Main technical chapter
├── images/                       # Architecture diagrams and charts
├── src/
│   ├── hello-world-pca/         # Foundation example (local + 3 clouds)
│   │   ├── README.md            # Complete setup guide
│   │   ├── shared/              # Universal PCA utilities
│   │   ├── local/               # Flask development server
│   │   ├── aws/                 # AWS Lambda deployment
│   │   ├── gcp/                 # Google Cloud Functions deployment
│   │   └── azure/               # Azure Functions deployment
│   ├── examples/                # Three progressive examples
│   │   ├── 01-iot-pipeline/     # IoT sensor data processing
│   │   ├── 02-large-dataset/    # Batch processing workflows
│   │   └── 03-realtime-api/     # Real-time inference API
│   ├── datasets/                # Data generation utilities
│   └── tests/                   # Unit and integration tests
└── docs/                        # Additional documentation
    ├── ARCHITECTURE.md          # Technical architecture decisions
    ├── ROADMAP.md              # Project milestones and vision
    └── deployment-guides/       # Cloud-specific setup guides
```

## System Requirements

### Core Requirements
- **Python**: 3.9+ (no GPU required)
- **Operating System**: macOS, Linux, or Windows
- **Memory**: 4GB+ recommended for local development
- **Disk Space**: 2GB for full project setup

### Development Tools
- **Git**: For version control
- **curl**: For API testing (or use Postman/similar)
- **Text Editor**: VS Code, PyCharm, or your preference

### Cloud Prerequisites (Optional)
Choose one or more cloud providers for deployment:

- **AWS**: AWS CLI + AWS Account + SAM CLI
- **Google Cloud**: gcloud CLI + GCP Account  
- **Azure**: Azure CLI + Azure Functions Core Tools + Azure Account

Detailed cloud setup instructions are in each deployment folder's README.md.

## Examples Overview

### Hello World PCA Foundation
**Purpose**: Establish multi-cloud deployment patterns  
**Dataset**: Synthetic sensor data (5 features → 2 components)  
**Deployment**: Local + AWS + GCP + Azure  
**Time**: 15 minutes setup, 2 seconds execution  
**Cost**: <$0.001 per request

### Example 1: IoT Sensor Pipeline  
**Purpose**: Event-driven batch processing  
**Dataset**: Coffee shop sensor data simulation (~50MB)  
**Pattern**: Storage trigger → Serverless function → Results  
**Cost**: <$1 per analysis

### Example 2: Large Dataset Processing
**Purpose**: Orchestrated workflows for big data  
**Dataset**: NYC Taxi data subset (~1-2GB)  
**Pattern**: Workflow orchestration + parallel processing  
**Cost**: $3-5 per full dataset analysis

### Example 3: Real-Time Inference API
**Purpose**: Low-latency PCA transformations  
**Dataset**: Stock market features (streaming)  
**Pattern**: HTTP API + cached models + auto-scaling  
**Cost**: $0.01 per transformation

## Development Workflow

### 1. Local Development First
Always start with local implementation:
- Instant feedback loops
- Easy debugging
- Zero cloud costs during development
- Identical behavior to cloud deployments

### 2. Virtual Environment Per Example
Each example maintains its own isolated environment:
```bash
cd src/[example-name]
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Cloud Deployment
After local validation, deploy to your preferred cloud(s):
```bash
# Each deployment folder has its own README.md
cd aws/    && ./deploy.sh    # AWS Lambda
cd gcp/    && ./deploy.sh    # Google Cloud Functions  
cd azure/  && ./deploy.sh    # Azure Functions
```

### 4. Cross-Platform Validation
Test identical results across all platforms:
```bash
python test_all_platforms.py  # Automated validation
```

## Architecture Principles

### Cloud-Agnostic Design
- **Universal logic**: Same PCA computation everywhere
- **Thin adapters**: Cloud-specific wrappers only
- **Consistent APIs**: Identical request/response formats
- **Local development**: Reference implementation for validation

### Serverless Best Practices
- **Stateless functions**: No persistent state between invocations
- **Memory optimization**: Right-sized for dataset requirements  
- **Cost efficiency**: Pay only for actual computation time
- **Error handling**: Robust retry strategies and logging

### Production Readiness
- **Comprehensive testing**: Unit + integration + cross-platform
- **Monitoring**: Performance tracking and cost analysis
- **Security**: Proper authentication and data encryption
- **Documentation**: Complete setup and deployment guides

## Troubleshooting

### Common Issues

**Python Version Conflicts**:
```bash
python --version  # Must be 3.9+
which python      # Verify correct Python installation
```

**Virtual Environment Issues**:
```bash
deactivate        # Exit current venv
rm -rf venv       # Remove corrupted venv
python -m venv venv --clear  # Create fresh venv
```

**Package Installation Failures**:
```bash
pip install --upgrade pip  # Update pip first
pip install -r requirements.txt --no-cache-dir
```

**Local Server Won't Start**:
```bash
# Check if port 8000 is already in use
lsof -i :8000
# Kill existing process or change port in app.py
```

### Platform-Specific Issues
- **AWS**: Check `aws configure` and IAM permissions
- **GCP**: Verify `gcloud auth list` and project settings  
- **Azure**: Confirm `az login` and subscription access

Detailed troubleshooting for each platform is in the respective deployment README files.

## Contributing

### Running Tests
```bash
# Unit tests for PCA logic
cd src/tests/unit
python -m pytest

# Integration tests for cloud deployments  
cd src/tests/integration
python test_cross_platform.py
```

### Code Style
- **Formatting**: Follow PEP 8
- **Documentation**: Comprehensive docstrings
- **Testing**: Unit tests for all new functionality
- **Dependencies**: Minimal, well-justified package additions

## Cost Optimization

### Development Costs
- **Local development**: Free
- **Unit testing**: Free
- **Integration testing**: <$1/month with typical usage

### Production Costs (Estimated)
- **Hello World**: <$0.001 per request
- **IoT Pipeline**: <$1 per 50MB dataset  
- **Large Dataset**: $3-5 per 1GB dataset
- **Real-time API**: $0.01 per transformation

### Cost Monitoring
Each example includes cost tracking and optimization strategies. Set up billing alerts in your cloud console before deploying.

## Support

### Documentation
- **Chapter**: Complete technical explanations in CHAPTER.md
- **Architecture**: Design decisions in docs/ARCHITECTURE.md  
- **Individual READMEs**: Setup guides for each example

### Getting Help
1. **Check example README.md** for specific setup instructions
2. **Review troubleshooting section** for common issues
3. **Examine error logs** for specific error messages
4. **Validate prerequisites** are correctly installed

## License

This project is created for educational purposes as part of the "Serverless PCA" technical chapter. All code examples are provided as-is for learning and experimentation.