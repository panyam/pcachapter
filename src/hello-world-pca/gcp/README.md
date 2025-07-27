# SensorScope PCA Analysis - Google Cloud Functions Deployment

Deploy Maya's sensor redundancy analysis system to Google Cloud Functions Gen 2 with one command. This implementation demonstrates serverless PCA processing for coffee shop sensor optimization in a production cloud environment.

## Prerequisites

### Google Cloud Platform Account
- **GCP Account**: Active Google Cloud Platform account (free tier available)
- **Project**: Create a new project or use an existing one (instructions below)
- **Billing Enabled**: Project must have billing enabled (functions incur minimal costs ~$0.001 per analysis)

### Required APIs
The deployment script automatically enables these APIs, but you can enable them manually if needed:
- Cloud Functions API (`cloudfunctions.googleapis.com`)
- Cloud Run API (`run.googleapis.com`) - Required for Functions Gen 2
- Cloud Build API (`cloudbuild.googleapis.com`)
- Artifact Registry API (`artifactregistry.googleapis.com`)
- Cloud Storage API (`storage.googleapis.com`)

### Local Development Environment
- **Python 3.9+**: Required for local testing
- **gcloud CLI**: [Install Google Cloud CLI](https://cloud.google.com/sdk/docs/install)
- **Git**: For repository access

## Quick Start

### 1. Set Up Google Cloud Project

#### Option A: Create New Project (Recommended for first-time users)
```bash
# Install gcloud CLI (if not already installed)
# Follow: https://cloud.google.com/sdk/docs/install

# Authenticate with Google Cloud
gcloud auth login

# Create a new project (replace 'sensorscope-demo' with your preferred name)
gcloud projects create sensorscope-demo --name="SensorScope Demo"

# Set the new project as active
gcloud config set project sensorscope-demo

# Enable billing (required for Cloud Functions)
# You'll need to link a billing account via the Cloud Console:
# https://console.cloud.google.com/billing/linkedaccount?project=sensorscope-demo
```

#### Option B: Use Existing Project
```bash
# Authenticate with Google Cloud
gcloud auth login

# List your existing projects
gcloud projects list

# Set your project (replace YOUR_PROJECT_ID)
gcloud config set project YOUR_PROJECT_ID
```

#### Verify Setup
```bash
# Verify configuration
gcloud config list

# Check billing is enabled (should show a billing account)
gcloud billing projects describe $(gcloud config get-value project)
```

### 2. Clone Repository
```bash
git clone https://github.com/panyam/sensorscope
cd sensorscope/src/hello-world-pca/gcp
```

### 3. Deploy Function
```bash
# One-command deployment
./deploy.sh
```

The script will:
- ✅ Validate prerequisites (authentication, project, billing)
- ✅ Enable required Google Cloud APIs
- ✅ Deploy the function with proper configuration
- ✅ Test the deployment automatically
- ✅ Provide function URL and test commands

## Testing Your Deployment

### Health Check
```bash
curl https://YOUR_FUNCTION_URL
```

Expected response:
```json
{
  "status": "healthy",
  "platform": "gcp-cloud-functions",
  "message": "SensorScope PCA service operational"
}
```

### Basic Sensor Analysis (20 sensors → 5 components)
```bash
curl -X POST https://YOUR_FUNCTION_URL \
  -H 'Content-Type: application/json' \
  -d '{
    "use_sample_data": true,
    "n_components": 5,
    "n_features": 20,
    "random_state": 42
  }'
```

Expected results:
- **Input dimensions**: [100, 20] - 100 readings from 20 sensors
- **Output dimensions**: [100, 5] - Reduced to 5 key measurements  
- **Variance explained**: ~79% - Most sensor information preserved
- **Business insights**: $164K-$176K potential annual savings

### Coffee Shop Scenario
```bash
curl -X POST https://YOUR_FUNCTION_URL \
  -H 'Content-Type: application/json' \
  -d '{
    "coffee_shop_sample": true,
    "location": "downtown",
    "n_components": 3
  }'
```

This simulates Maya's exact use case: analyzing a downtown coffee shop's sensors to identify the 3 most critical measurements.

### Custom Sensor Data
```bash
curl -X POST https://YOUR_FUNCTION_URL \
  -H 'Content-Type: application/json' \
  -d '{
    "data": [
      [22.5, 45.2, 1013.2, 0.8, 5.2],
      [23.1, 47.8, 1012.8, 0.9, 5.5],
      [21.9, 44.1, 1013.5, 0.7, 4.8]
    ],
    "n_components": 2,
    "scale_features": true,
    "business_context": {
      "cost_per_sensor": 250,
      "analysis_type": "sensor_redundancy"
    }
  }'
```

## Local Development

### Test Locally Before Deploying
```bash
# Install dependencies
pip install -r requirements.txt

# Run local development server
functions-framework --target=sensorscope_pca --debug

# Test local endpoint
curl -X POST http://localhost:8080 \
  -H 'Content-Type: application/json' \
  -d '{"use_sample_data": true, "n_components": 3}'
```

## Cost Management

### Expected Costs
- **Per analysis**: <$0.001 for typical sensor datasets
- **Monthly baseline**: ~$0 (no charges when not in use)
- **Memory allocation**: 512MB (sufficient for 20-sensor analysis)
- **Execution time**: 60s timeout (typical analysis <5s)

### Monitor Usage
- **Cloud Console**: [Functions Dashboard](https://console.cloud.google.com/functions)
- **Billing**: [Billing Dashboard](https://console.cloud.google.com/billing)
- **Usage metrics**: Automatically tracked in function logs

## Function Configuration

### Deployed Settings
- **Runtime**: Python 3.9
- **Memory**: 512Mi (optimized for PCA processing)
- **Timeout**: 60 seconds
- **Trigger**: HTTP (unauthenticated for demo purposes)
- **Region**: us-central1 (configurable in deploy.sh)

### Environment Variables
- `FUNCTION_REGION`: Deployment region
- `PROJECT_ID`: GCP project identifier

## Troubleshooting

### Common Issues

**Authentication Error**
```
ERROR: (gcloud.auth.login) There was a problem with web authentication.
```
Solution: Run `gcloud auth login` and complete browser authentication.

**Project Not Set**
```
ERROR: (gcloud) The required property [core/project] is not currently set.
```
Solution: Run `gcloud config set project YOUR_PROJECT_ID`

**API Not Enabled**
```
ERROR: Cloud Function API has not been used in project
```
Solution: The deploy script automatically enables APIs, or manually enable via Cloud Console.

**Billing Not Enabled**
```
ERROR: Cloud billing account required
```
Solution: 
1. Go to [Cloud Console Billing](https://console.cloud.google.com/billing)
2. Create a billing account (requires credit card, but free tier covers this demo)
3. Link billing account to your project
4. Alternative: Use direct link `https://console.cloud.google.com/billing/linkedaccount?project=YOUR_PROJECT_ID`

**Function Timeout**
```
Function execution took 60001 ms, finished with status: 'timeout'
```
Solution: Reduce dataset size or increase timeout in deploy.sh.

### View Logs
```bash
# View function logs
gcloud functions logs read sensorscope-pca --region=us-central1

# Stream live logs
gcloud functions logs tail sensorscope-pca --region=us-central1
```

## Cleanup

### Delete Function
```bash
# Remove deployed function
gcloud functions delete sensorscope-pca --region=us-central1 --gen2 --quiet

# Verify deletion
gcloud functions list --regions=us-central1
```

### Remove APIs (Optional)
```bash
# Only disable if not used by other services
gcloud services disable cloudfunctions.googleapis.com --force
```

## Next Steps

### Cross-Platform Validation
- Compare results with local Flask implementation
- Verify identical PCA outputs across platforms
- Test performance and cost differences

### Production Considerations
- Enable authentication for production use
- Configure custom domains
- Set up monitoring and alerting
- Implement rate limiting

### Advanced Features
- Deploy to multiple regions
- Add CI/CD pipeline integration
- Connect to Cloud Storage for large datasets
- Integrate with BigQuery for data warehousing

## Support

- **Documentation**: [Google Cloud Functions](https://cloud.google.com/functions/docs)
- **GitHub Repository**: https://github.com/panyam/sensorscope
- **Function Logs**: Available in Cloud Console
- **Community**: Google Cloud community forums

---

This deployment demonstrates how Maya's sensor redundancy analysis scales from local development to production cloud deployment in under 5 minutes, providing the foundation for real-world serverless PCA implementations.