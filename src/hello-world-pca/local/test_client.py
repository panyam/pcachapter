#!/usr/bin/env python3
"""
Test client for Hello World PCA local development server.

This script provides comprehensive testing of the PCA service,
demonstrating various usage patterns for Maya's sensor analysis.

Usage:
    # Start the server first: python app.py
    # Then in another terminal: python test_client.py
"""

import requests
import json
import time
from typing import Dict, Any, List


class PCATestClient:
    """
    Test client for comprehensive PCA service validation.
    
    Provides methods to test different scenarios and validate
    the service behavior for Maya's sensor redundancy analysis.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        
    def test_health_check(self) -> bool:
        """Test the health check endpoint."""
        try:
            response = self.session.get(f"{self.base_url}/health")
            print(f"🏥 Health Check: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Status: {data['status']}")
                print(f"   Platform: {data['platform']}")
                return True
            else:
                print(f"   ❌ Health check failed: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Connection error: {e}")
            return False
    
    def test_basic_sample_data(self) -> Dict[str, Any]:
        """Test basic PCA with synthetic sample data."""
        print("\n📊 Testing Basic Sample Data Analysis")
        
        payload = {
            "use_sample_data": True,
            "n_components": 2,
            "random_state": 42
        }
        
        response = self.session.post(f"{self.base_url}/pca", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            analysis = data['analysis']
            performance = data['performance']
            
            print(f"   ✅ Success: {analysis['input_dimensions']} → {analysis['output_dimensions']}")
            print(f"   📈 Variance Explained: {analysis['variance_analysis']['total_variance_explained']:.3f}")
            print(f"   ⚡ Execution Time: {performance['execution_time_ms']:.1f}ms")
            print(f"   💾 Memory Used: {performance['memory_used_mb']:.1f}MB")
            
            return data
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
            return {}
    
    def test_coffee_shop_sample(self) -> Dict[str, Any]:
        """Test with realistic coffee shop sensor simulation."""
        print("\n☕ Testing Coffee Shop Sensor Simulation")
        
        payload = {
            "use_sample_data": True,
            "coffee_shop_sample": True,
            "location": "downtown",
            "hours": 12,
            "n_components": 3,
            "sensor_types": ["temperature", "humidity", "pressure", "vibration", "flow_rate"]
        }
        
        response = self.session.post(f"{self.base_url}/pca", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            analysis = data['analysis'] 
            insights = data['business_insights']
            
            print(f"   ✅ Success: {analysis['input_dimensions']} → {analysis['output_dimensions']}")
            print(f"   📊 Sensor Reduction: {insights['dimensionality_reduction']['potential_sensor_reduction']}")
            print(f"   💡 Key Finding: {insights['key_findings'][0] if insights['key_findings'] else 'None'}")
            
            return data
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
            return {}
    
    def test_custom_data(self) -> Dict[str, Any]:
        """Test with custom sensor data."""
        print("\n🔧 Testing Custom Sensor Data")
        
        # Simulate 3 sensors with some correlation
        custom_data = [
            [22.5, 45.2, 1013.2],  # temperature, humidity, pressure
            [23.1, 47.8, 1012.8],
            [21.9, 44.1, 1013.5],
            [24.2, 49.3, 1011.9],
            [22.8, 46.7, 1012.4],
            [23.5, 48.2, 1012.1]
        ]
        
        payload = {
            "data": custom_data,
            "n_components": 2,
            "scale_features": True,
            "business_context": {
                "cost_per_sensor": 250,
                "analysis_type": "sensor_redundancy"
            }
        }
        
        response = self.session.post(f"{self.base_url}/pca", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            analysis = data['analysis']
            insights = data['business_insights']
            
            print(f"   ✅ Success: {analysis['input_dimensions']} → {analysis['output_dimensions']}")
            print(f"   📈 Variance Explained: {analysis['variance_analysis']['total_variance_explained']:.3f}")
            
            if 'cost_impact' in insights:
                cost = insights['cost_impact']
                print(f"   💰 Current Cost: {cost['current_annual_cost']}")
                print(f"   💰 Potential Savings: {cost['potential_annual_savings']}")
            
            return data
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
            return {}
    
    def test_error_conditions(self) -> None:
        """Test various error conditions."""
        print("\n⚠️  Testing Error Handling")
        
        # Test missing data
        response = self.session.post(f"{self.base_url}/pca", json={})
        print(f"   Missing data: {response.status_code} ({'✅' if response.status_code == 400 else '❌'})")
        
        # Test invalid data format
        response = self.session.post(f"{self.base_url}/pca", json={"data": [1, 2, 3]})  # 1D data
        print(f"   Invalid format: {response.status_code} ({'✅' if response.status_code == 400 else '❌'})")
        
        # Test too many components
        response = self.session.post(f"{self.base_url}/pca", json={
            "data": [[1, 2], [3, 4]], 
            "n_components": 5  # More than available
        })
        print(f"   Too many components: {response.status_code} ({'✅' if response.status_code == 400 else '❌'})")
        
        # Test invalid JSON
        try:
            response = requests.post(f"{self.base_url}/pca", data="invalid json")
            print(f"   Invalid JSON: {response.status_code} ({'✅' if response.status_code == 400 else '❌'})")
        except:
            print(f"   Invalid JSON: Connection handled correctly ✅")
    
    def test_performance_scenarios(self) -> None:
        """Test different dataset sizes for performance characteristics."""
        print("\n🏎️  Testing Performance Scenarios")
        
        scenarios = [
            {"n_samples": 50, "n_features": 5, "n_components": 2, "name": "Small"},
            {"n_samples": 500, "n_features": 10, "n_components": 3, "name": "Medium"},
            {"n_samples": 1000, "n_features": 15, "n_components": 5, "name": "Large"}
        ]
        
        for scenario in scenarios:
            payload = {
                "use_sample_data": True,
                "n_samples": scenario["n_samples"],
                "n_features": scenario["n_features"],
                "n_components": scenario["n_components"],
                "random_state": 42
            }
            
            start_time = time.time()
            response = self.session.post(f"{self.base_url}/pca", json=payload)
            total_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                server_time = data['performance']['execution_time_ms']
                memory_used = data['performance']['memory_used_mb']
                
                print(f"   {scenario['name']}: {server_time:.1f}ms server, "
                      f"{total_time*1000:.1f}ms total, {memory_used:.1f}MB")
            else:
                print(f"   {scenario['name']}: ❌ Failed")
    
    def run_comprehensive_tests(self) -> None:
        """Run all tests and provide summary."""
        print("🧪 Hello World PCA - Comprehensive Test Suite")
        print("=" * 55)
        print("Testing Maya's sensor redundancy analysis service")
        print()
        
        # Check if server is running
        if not self.test_health_check():
            print("\n❌ Server not accessible. Please start the server first:")
            print("   cd src/hello-world-pca/local")
            print("   python app.py")
            return
        
        # Run all test scenarios
        basic_result = self.test_basic_sample_data()
        coffee_result = self.test_coffee_shop_sample()
        custom_result = self.test_custom_data()
        
        self.test_error_conditions()
        self.test_performance_scenarios()
        
        # Validation summary
        print("\n📋 Validation Summary")
        print("-" * 25)
        
        if basic_result:
            variance_explained = basic_result['analysis']['variance_analysis']['total_variance_explained']
            print(f"✅ Basic PCA: {variance_explained:.1%} variance explained")
        
        if coffee_result:
            reduction = coffee_result['business_insights']['dimensionality_reduction']['potential_sensor_reduction']
            print(f"✅ Coffee Shop: {reduction} potential sensor reduction")
        
        if custom_result:
            components = custom_result['analysis']['output_dimensions'][1]
            print(f"✅ Custom Data: Reduced to {components} components")
        
        print("\n🎉 Test Suite Complete!")
        print("\nNext steps:")
        print("• Deploy to cloud platforms using deployment scripts")
        print("• Run cross-platform validation tests")
        print("• Scale to larger datasets with production examples")


def main():
    """Main test execution."""
    client = PCATestClient()
    client.run_comprehensive_tests()


if __name__ == "__main__":
    main()