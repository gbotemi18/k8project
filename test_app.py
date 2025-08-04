#!/usr/bin/env python3
"""
Simple test script to verify the IP reversal application
"""

import requests
import time

def test_application():
    """Test the application endpoints"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing IP Reversal Application")
    print("=" * 50)
    
    try:
        # Test health endpoint
        print("1. Testing health endpoint...")
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"   ✅ Health: {health_data['status']}")
            print(f"   📊 Database: {health_data['database_status']}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
        
        # Test IP endpoint
        print("\n2. Testing IP endpoint...")
        response = requests.get(f"{base_url}/api/ip")
        if response.status_code == 200:
            ip_data = response.json()
            print(f"   ✅ Original IP: {ip_data['original_ip']}")
            print(f"   ✅ Reversed IP: {ip_data['reversed_ip']}")
            print(f"   📋 Version: {ip_data['version']}")
        else:
            print(f"   ❌ IP endpoint failed: {response.status_code}")
            return False
        
        # Test stats endpoint
        print("\n3. Testing stats endpoint...")
        response = requests.get(f"{base_url}/api/stats")
        if response.status_code == 200:
            stats_data = response.json()
            print(f"   ✅ Total requests: {stats_data['total_requests']}")
            print(f"   ✅ Unique IPs: {stats_data['unique_ips']}")
            print(f"   ✅ Recent (24h): {stats_data['recent_requests_24h']}")
        else:
            print(f"   ❌ Stats endpoint failed: {response.status_code}")
            return False
        
        # Test history endpoint
        print("\n4. Testing history endpoint...")
        response = requests.get(f"{base_url}/api/history?limit=5")
        if response.status_code == 200:
            history_data = response.json()
            print(f"   ✅ Total records: {history_data['total_count']}")
            print(f"   ✅ Retrieved: {len(history_data['records'])}")
        else:
            print(f"   ❌ History endpoint failed: {response.status_code}")
            return False
        
        # Test web interface
        print("\n5. Testing web interface...")
        response = requests.get(base_url)
        if response.status_code == 200:
            print("   ✅ Web interface accessible")
        else:
            print(f"   ❌ Web interface failed: {response.status_code}")
            return False
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed! Application is working correctly.")
        print(f"🌐 Web Interface: {base_url}")
        print(f"📚 API Docs: {base_url}/api/docs")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the application.")
        print("   Make sure the application is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    # Wait a bit for the application to start
    print("⏳ Waiting for application to start...")
    time.sleep(2)
    
    success = test_application()
    exit(0 if success else 1) 