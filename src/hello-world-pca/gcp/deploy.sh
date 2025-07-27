#!/bin/bash
set -e

# SensorScope PCA Analysis - Google Cloud Functions Deployment Script
# 
# This script deploys Maya's sensor redundancy analysis system to Google Cloud
# Functions Gen 2 with one command. It handles all prerequisites validation,
# function packaging, and deployment automation.

echo "🚀 SensorScope PCA Analysis - Google Cloud Deployment"
echo "======================================================"
echo
echo "Deploying Maya's sensor redundancy analysis to Google Cloud Functions..."
echo

# Configuration
FUNCTION_NAME="sensorscope-pca"
REGION="us-central1"
MEMORY="512Mi"
TIMEOUT="60s"
ENTRY_POINT="sensorscope_pca"
RUNTIME="python311"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_status() {
    printf "${BLUE}📋 %s${NC}\n" "$1"
}

print_success() {
    printf "${GREEN}✅ %s${NC}\n" "$1"
}

print_warning() {
    printf "${YELLOW}⚠️  %s${NC}\n" "$1"
}

print_error() {
    printf "${RED}❌ %s${NC}\n" "$1"
}

# Check prerequisites
print_status "Checking prerequisites..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    print_error "gcloud CLI is not installed"
    echo "Please install gcloud CLI: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

print_success "gcloud CLI found"

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
    print_error "Not authenticated with gcloud"
    echo "Please run: gcloud auth login"
    exit 1
fi

ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n1)
print_success "Authenticated as: $ACCOUNT"

# Check if project is set
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    print_error "No GCP project configured"
    echo "Please run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

print_success "Using project: $PROJECT_ID"

# Check if billing is enabled (this is a simple check)
print_status "Checking if billing is enabled..."
if ! gcloud services list --enabled --filter="name:cloudbilling.googleapis.com" --format="value(name)" | grep -q "cloudbilling"; then
    print_warning "Cannot verify billing status. Please ensure billing is enabled for project $PROJECT_ID"
else
    print_success "Billing appears to be configured"
fi

# Enable required APIs
print_status "Enabling required Google Cloud APIs..."

REQUIRED_APIS=(
    "cloudfunctions.googleapis.com"
    "run.googleapis.com"
    "cloudbuild.googleapis.com"
    "artifactregistry.googleapis.com"
    "storage.googleapis.com"
)

for api in "${REQUIRED_APIS[@]}"; do
    print_status "Enabling $api..."
    if gcloud services enable "$api" --quiet; then
        print_success "$api enabled"
    else
        print_error "Failed to enable $api"
        exit 1
    fi
done

# Validate shared directory exists
if [ ! -d "../shared" ]; then
    print_error "Shared directory not found. Please run from src/hello-world-pca/gcp/"
    exit 1
fi

print_success "Found shared PCA modules"

# Check Python requirements
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found"
    exit 1
fi

print_success "Found requirements.txt"

# Deploy the function
print_status "Deploying Cloud Function..."
echo "Function details:"
echo "  Name: $FUNCTION_NAME"
echo "  Region: $REGION"
echo "  Runtime: $RUNTIME"
echo "  Memory: $MEMORY"
echo "  Timeout: $TIMEOUT"
echo

# Create deployment command
DEPLOY_CMD="gcloud functions deploy $FUNCTION_NAME \
    --gen2 \
    --runtime=$RUNTIME \
    --region=$REGION \
    --source=. \
    --entry-point=$ENTRY_POINT \
    --trigger-http \
    --allow-unauthenticated \
    --memory=$MEMORY \
    --timeout=$TIMEOUT \
    --set-env-vars=FUNCTION_REGION=$REGION,PROJECT_ID=$PROJECT_ID"

echo "Running deployment command..."
echo "$DEPLOY_CMD"
echo

if $DEPLOY_CMD; then
    print_success "Function deployed successfully!"
else
    print_error "Deployment failed"
    exit 1
fi

# Get function URL
print_status "Retrieving function URL..."
FUNCTION_URL=$(gcloud functions describe $FUNCTION_NAME --region=$REGION --gen2 --format="value(serviceConfig.uri)")

if [ -z "$FUNCTION_URL" ]; then
    print_error "Could not retrieve function URL"
    exit 1
fi

print_success "Function URL: $FUNCTION_URL"

# Test the deployment
print_status "Testing deployment..."

# Health check test
echo "Testing health check..."
if curl -s -f "$FUNCTION_URL" > /dev/null; then
    print_success "Health check passed"
else
    print_warning "Health check failed, but function may still work"
fi

# PCA analysis test
echo "Testing PCA analysis with sample data..."
TEST_RESPONSE=$(curl -s -X POST "$FUNCTION_URL" \
    -H "Content-Type: application/json" \
    -d '{"use_sample_data": true, "n_components": 3, "n_features": 20}')

if echo "$TEST_RESPONSE" | grep -q '"status": "success"'; then
    print_success "PCA analysis test passed"
    
    # Extract key metrics from response
    if command -v python3 &> /dev/null; then
        echo
        echo "Sample Results:"
        echo "$TEST_RESPONSE" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    analysis = data.get('analysis', {})
    variance = analysis.get('variance_analysis', {})
    print(f\"  Input dimensions: {analysis.get('input_dimensions', 'unknown')}\"
    print(f\"  Output dimensions: {analysis.get('output_dimensions', 'unknown')}\"
    print(f\"  Total variance explained: {variance.get('total_variance_explained', 0):.1%}\"
    
    # Business insights
    insights = data.get('business_insights', {})
    cost_impact = insights.get('cost_impact', {})
    if cost_impact:
        print(f\"  Potential savings: {cost_impact.get('potential_annual_savings', 'unknown')}\"
except:
    print('  Could not parse response details')
"
    fi
else
    print_warning "PCA analysis test failed, but function is deployed"
    echo "Response: $TEST_RESPONSE"
fi

# Deployment summary
echo
echo "🎉 Deployment Complete!"
echo "======================="
echo
echo "Function Details:"
echo "  Name: $FUNCTION_NAME"
echo "  Project: $PROJECT_ID"
echo "  Region: $REGION"
echo "  URL: $FUNCTION_URL"
echo
echo "Quick Tests:"
echo "  Health check:"
echo "    curl $FUNCTION_URL"
echo
echo "  Basic PCA analysis:"
echo "    curl -X POST $FUNCTION_URL \\"
echo "      -H 'Content-Type: application/json' \\"
echo "      -d '{\"use_sample_data\": true, \"n_components\": 5, \"n_features\": 20}'"
echo
echo "  Coffee shop scenario:"
echo "    curl -X POST $FUNCTION_URL \\"
echo "      -H 'Content-Type: application/json' \\"
echo "      -d '{\"coffee_shop_sample\": true, \"n_components\": 3}'"
echo
echo "💰 Cost Information:"
echo "  This function uses minimal resources and should cost <$0.01 per analysis"
echo "  Monitor usage: https://console.cloud.google.com/functions/list?project=$PROJECT_ID"
echo
echo "🧹 Cleanup:"
echo "  To delete the function:"
echo "    gcloud functions delete $FUNCTION_NAME --region=$REGION --gen2 --quiet"
echo
echo "📚 Documentation:"
echo "  Function logs: https://console.cloud.google.com/functions/details/$REGION/$FUNCTION_NAME/logs?project=$PROJECT_ID"
echo "  GitHub repo: https://github.com/panyam/sensorscope"
echo

print_success "SensorScope PCA analysis is now running on Google Cloud!"
