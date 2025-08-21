#!/usr/bin/env python3
"""
Test script for the TrackerWorkflow API
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_create_project():
    """Test creating a new project"""
    print("Testing project creation...")
    
    project_data = {
        "name": "Website Redesign",
        "description": "Redesign the company website with modern UI/UX principles"
    }
    
    response = requests.post(
        f"{BASE_URL}/projects",
        json=project_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        project = response.json()
        print(f"Created project: {project['name']} (ID: {project['id']})")
        print(f"Created at: {project['created_at']}")
        return project['id']
    else:
        print(f"Error: {response.text}")
        return None

def test_get_projects():
    """Test getting all projects"""
    print("Testing get all projects...")
    response = requests.get(f"{BASE_URL}/projects")
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        projects = response.json()
        print(f"Found {len(projects)} projects:")
        for project in projects:
            print(f"  - {project['name']}: {project['description']}")
    else:
        print(f"Error: {response.text}")
    print()

def test_get_project(project_id):
    """Test getting a specific project"""
    print(f"Testing get project {project_id}...")
    response = requests.get(f"{BASE_URL}/projects/{project_id}")
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        project = response.json()
        print(f"Project: {project['name']}")
        print(f"Description: {project['description']}")
        print(f"Created at: {project['created_at']}")
    else:
        print(f"Error: {response.text}")
    print()

def test_update_project(project_id):
    """Test updating a project"""
    print(f"Testing update project {project_id}...")
    
    update_data = {
        "name": "Website Redesign - Updated",
        "description": "Redesign the company website with modern UI/UX principles and accessibility features"
    }
    
    response = requests.put(
        f"{BASE_URL}/projects/{project_id}",
        json=update_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        project = response.json()
        print(f"Updated project: {project['name']}")
        print(f"New description: {project['description']}")
    else:
        print(f"Error: {response.text}")
    print()

def test_delete_project(project_id):
    """Test deleting a project"""
    print(f"Testing delete project {project_id}...")
    response = requests.delete(f"{BASE_URL}/projects/{project_id}")
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("Project deleted successfully")
    else:
        print(f"Error: {response.text}")
    print()

def main():
    """Run all tests"""
    print("=== TrackerWorkflow API Test Suite ===\n")
    
    # Test health check
    test_health_check()
    
    # Test project CRUD operations
    project_id = test_create_project()
    
    if project_id:
        test_get_projects()
        test_get_project(project_id)
        test_update_project(project_id)
        test_get_project(project_id)  # Verify update
        test_delete_project(project_id)
        test_get_projects()  # Verify deletion
    
    print("=== Test Suite Complete ===")

if __name__ == "__main__":
    main() 