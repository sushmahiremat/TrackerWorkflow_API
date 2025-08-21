#!/usr/bin/env python3
"""
Test script for the Task API endpoints
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def test_create_task():
    """Test creating a new task"""
    print("Testing task creation...")
    
    # First, create a project to associate the task with
    project_data = {
        "name": "Test Project for Tasks",
        "description": "A project to test task creation"
    }
    
    project_response = requests.post(
        f"{BASE_URL}/projects",
        json=project_data,
        headers={"Content-Type": "application/json"}
    )
    
    if project_response.status_code != 200:
        print(f"Failed to create project: {project_response.text}")
        return None, None
    
    project = project_response.json()
    project_id = project['id']
    print(f"Created project: {project['name']} (ID: {project_id})")
    
    # Now create a task
    task_data = {
        "title": "Design Homepage Layout",
        "description": "Create wireframes and mockups for the homepage",
        "status": "TODO",
        "priority": "HIGH",
        "assignee": "John Doe",
        "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
        "project_id": project_id
    }
    
    response = requests.post(
        f"{BASE_URL}/tasks",
        json=task_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Task creation status: {response.status_code}")
    if response.status_code == 200:
        task = response.json()
        print(f"Created task: {task['title']} (ID: {task['id']})")
        print(f"Status: {task['status']}, Priority: {task['priority']}")
        print(f"Assignee: {task['assignee']}, Due: {task['due_date']}")
        return project_id, task['id']
    else:
        print(f"Error: {response.text}")
        return project_id, None

def test_get_tasks_by_project(project_id):
    """Test getting tasks for a specific project"""
    print(f"\nTesting get tasks by project {project_id}...")
    response = requests.get(f"{BASE_URL}/tasks/project/{project_id}")
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        tasks = response.json()
        print(f"Found {len(tasks)} tasks for project {project_id}:")
        for task in tasks:
            print(f"  - {task['title']}: {task['status']} ({task['priority']})")
    else:
        print(f"Error: {response.text}")

def test_get_all_tasks():
    """Test getting all tasks"""
    print("\nTesting get all tasks...")
    response = requests.get(f"{BASE_URL}/tasks")
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        tasks = response.json()
        print(f"Found {len(tasks)} total tasks:")
        for task in tasks:
            print(f"  - {task['title']} (Project: {task['project_id']})")
    else:
        print(f"Error: {response.text}")

def test_update_task(task_id, project_id):
    """Test updating a task"""
    print(f"\nTesting update task {task_id}...")
    
    update_data = {
        "title": "Design Homepage Layout - Updated",
        "description": "Create wireframes and mockups for the homepage with accessibility features",
        "status": "IN_PROGRESS",
        "priority": "HIGH",
        "assignee": "John Doe",
        "due_date": (datetime.now() + timedelta(days=5)).isoformat(),
        "project_id": project_id
    }
    
    response = requests.put(
        f"{BASE_URL}/tasks/{task_id}",
        json=update_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        task = response.json()
        print(f"Updated task: {task['title']}")
        print(f"New status: {task['status']}, Description: {task['description']}")
    else:
        print(f"Error: {response.text}")

def test_delete_task(task_id):
    """Test deleting a task"""
    print(f"\nTesting delete task {task_id}...")
    response = requests.delete(f"{BASE_URL}/tasks/{task_id}")
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("Task deleted successfully")
    else:
        print(f"Error: {response.text}")

def test_cleanup(project_id):
    """Clean up test data"""
    print(f"\nCleaning up test project {project_id}...")
    response = requests.delete(f"{BASE_URL}/projects/{project_id}")
    
    print(f"Project deletion status: {response.status_code}")
    if response.status_code == 200:
        print("Test project deleted successfully")
    else:
        print(f"Error deleting project: {response.text}")

def main():
    """Run all task tests"""
    print("=== Task API Test Suite ===\n")
    
    # Test task CRUD operations
    project_id, task_id = test_create_task()
    
    if project_id and task_id:
        test_get_tasks_by_project(project_id)
        test_get_all_tasks()
        test_update_task(task_id, project_id)
        test_get_tasks_by_project(project_id)  # Verify update
        test_delete_task(task_id)
        test_get_tasks_by_project(project_id)  # Verify deletion
        test_cleanup(project_id)
    
    print("\n=== Task Test Suite Complete ===")

if __name__ == "__main__":
    main()
