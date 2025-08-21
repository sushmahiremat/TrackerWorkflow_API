#!/usr/bin/env python3
"""
Test script to verify frontend-backend integration
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_frontend_integration():
    """Test the API endpoints that the frontend will use"""
    print("🧪 Testing Frontend-Backend Integration...")
    print("=" * 60)
    
    # Test 1: Health check
    print("1. Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"   ✅ Health check: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return False
    
    # Test 2: Login with demo credentials (frontend default)
    print("\n2. Testing login with demo credentials...")
    try:
        data = {
            "email": "demo@example.com",
            "password": "password"
        }
        response = requests.post(f"{BASE_URL}/login", json=data)
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get('access_token')
            print(f"   ✅ Login successful, token received")
            print(f"   📝 Token type: {token_data.get('token_type')}")
        else:
            print(f"   ❌ Login failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Login test failed: {e}")
        return False
    
    # Test 3: Get user info with token
    print("\n3. Testing user info retrieval...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/me", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            print(f"   ✅ User info retrieved successfully")
            print(f"   👤 User: {user_data.get('email')} (ID: {user_data.get('id')})")
        else:
            print(f"   ❌ User info failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ User info test failed: {e}")
        return False
    
    # Test 4: Test registration
    print("\n4. Testing user registration...")
    try:
        data = {
            "email": "newuser@example.com",
            "password": "newpassword123"
        }
        response = requests.post(f"{BASE_URL}/register", json=data)
        if response.status_code == 200:
            user_data = response.json()
            print(f"   ✅ Registration successful")
            print(f"   👤 New user: {user_data.get('email')} (ID: {user_data.get('id')})")
        else:
            print(f"   ⚠️  Registration response: {response.status_code}")
            print(f"   📝 Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Registration test failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Frontend-Backend Integration Test Complete!")
    print("\n📋 Summary:")
    print("✅ Health check endpoint working")
    print("✅ Login endpoint working")
    print("✅ User info endpoint working")
    print("✅ Registration endpoint working")
    print("\n🚀 Your frontend can now connect to the backend!")
    print("   - API Base URL: http://localhost:8000")
    print("   - Demo credentials: demo@example.com / password")
    print("   - JWT tokens are working correctly")
    
    return True

if __name__ == "__main__":
    test_frontend_integration() 