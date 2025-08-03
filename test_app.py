#!/usr/bin/env python3
"""
Simple test script to verify the application functionality
"""

import requests
import time
import sys

def test_health_endpoint():
    """Test the health check endpoint"""
    try:
        response = requests.get('http://localhost:5000/health', timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed with status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_main_page():
    """Test the main page loads"""
    try:
        response = requests.get('http://localhost:5000/', timeout=5)
        if response.status_code == 200:
            print("✅ Main page loads successfully")
            return True
        else:
            print(f"❌ Main page failed with status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Main page failed: {e}")
        return False

def test_attendance_endpoint():
    """Test the attendance endpoint"""
    try:
        # Test with a sample date
        data = {'selected_date': '2024-01-01'}
        response = requests.post('http://localhost:5000/attendance', data=data, timeout=5)
        if response.status_code == 200:
            print("✅ Attendance endpoint responds correctly")
            return True
        else:
            print(f"❌ Attendance endpoint failed with status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Attendance endpoint failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Starting application tests...")
    
    # Wait a bit for the application to start
    print("⏳ Waiting for application to start...")
    time.sleep(3)
    
    tests = [
        test_health_endpoint,
        test_main_page,
        test_attendance_endpoint
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Application is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the application logs.")
        return 1

if __name__ == "__main__":
    sys.exit(main())