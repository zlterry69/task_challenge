#!/usr/bin/env python3
"""
Script para testear todas las funcionalidades REST API del Task Challenge
Requiere que el proyecto esté corriendo en Docker en localhost:8000
"""

import json
import requests
from datetime import datetime, timedelta
from typing import Optional

# Configuración
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_test(test_name: str):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}🧪 TESTING: {test_name}{Colors.ENDC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.ENDC}")

def print_success(message: str):
    print(f"{Colors.GREEN}✅ {message}{Colors.ENDC}")

def print_error(message: str):
    print(f"{Colors.RED}❌ {message}{Colors.ENDC}")

def print_info(message: str):
    print(f"{Colors.YELLOW}ℹ️  {message}{Colors.ENDC}")

def print_result(result: dict):
    print(f"{Colors.CYAN}📊 Result: {json.dumps(result, indent=2, default=str)}{Colors.ENDC}")

class RESTAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token: Optional[str] = None
        self.test_user_id: Optional[int] = None
        self.test_task_list_id: Optional[int] = None
        self.test_task_id: Optional[int] = None
        
    def set_auth_header(self):
        if self.access_token:
            self.session.headers.update({
                "Authorization": f"Bearer {self.access_token}"
            })
    
    def test_user_registration(self):
        print_test("User Registration")
        
        # Test data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        user_data = {
            "email": f"test_user_{timestamp}@example.com",
            "full_name": f"Test User {timestamp}",
            "password": "testpassword123"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/register", json=user_data)
            
            if response.status_code == 200:
                result = response.json()
                self.test_user_id = result.get("id")
                print_success(f"User registered successfully with ID: {self.test_user_id}")
                print_result(result)
                return user_data
            else:
                print_error(f"Registration failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print_error(f"Registration error: {str(e)}")
            return None
    
    def test_user_login(self, user_data: dict):
        print_test("User Login")
        
        login_data = {
            "username": user_data["email"],  # OAuth2 uses 'username' field
            "password": user_data["password"]
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/auth/login", 
                data=login_data,  # OAuth2 expects form data
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                result = response.json()
                self.access_token = result.get("access_token")
                print_success("Login successful")
                print_result(result)
                self.set_auth_header()
                return True
            else:
                print_error(f"Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Login error: {str(e)}")
            return False
    
    def test_get_current_user(self):
        print_test("Get Current User (/auth/me)")
        
        try:
            response = self.session.get(f"{API_BASE}/auth/me")
            
            if response.status_code == 200:
                result = response.json()
                print_success("User info retrieved successfully")
                print_result(result)
                return True
            else:
                print_error(f"Get user failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Get user error: {str(e)}")
            return False
    
    def test_create_task_list(self):
        print_test("Create Task List")
        
        task_list_data = {
            "name": f"Test Task List {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "description": "A test task list created by REST API test"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/task-lists/", json=task_list_data)
            
            if response.status_code == 200:
                result = response.json()
                self.test_task_list_id = result.get("id")
                print_success(f"Task list created successfully with ID: {self.test_task_list_id}")
                print_result(result)
                return True
            else:
                print_error(f"Create task list failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Create task list error: {str(e)}")
            return False
    
    def test_get_task_lists(self):
        print_test("Get All Task Lists")
        
        try:
            response = self.session.get(f"{API_BASE}/task-lists/")
            
            if response.status_code == 200:
                result = response.json()
                print_success(f"Retrieved {len(result)} task lists")
                print_result(result)
                return True
            else:
                print_error(f"Get task lists failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Get task lists error: {str(e)}")
            return False
    
    def test_get_single_task_list(self):
        print_test("Get Single Task List")
        
        if not self.test_task_list_id:
            print_error("No task list ID available for testing")
            return False
        
        try:
            response = self.session.get(f"{API_BASE}/task-lists/{self.test_task_list_id}")
            
            if response.status_code == 200:
                result = response.json()
                print_success("Task list retrieved successfully")
                print_result(result)
                return True
            else:
                print_error(f"Get task list failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Get task list error: {str(e)}")
            return False
    
    def test_create_task(self):
        print_test("Create Task")
        
        if not self.test_task_list_id:
            print_error("No task list ID available for creating task")
            return False
        
        # Create task with due date
        due_date = datetime.utcnow() + timedelta(days=7)
        task_data = {
            "title": f"Test Task {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "description": "A test task created by REST API test",
            "task_list_id": self.test_task_list_id,
            "priority": "high",
            "due_date": due_date.isoformat()
        }
        
        try:
            response = self.session.post(f"{API_BASE}/tasks/", json=task_data)
            
            if response.status_code == 200:
                result = response.json()
                self.test_task_id = result.get("id")
                print_success(f"Task created successfully with ID: {self.test_task_id}")
                print_result(result)
                return True
            else:
                print_error(f"Create task failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Create task error: {str(e)}")
            return False
    
    def test_get_tasks(self):
        print_test("Get All Tasks")
        
        try:
            # Test without filters
            response = self.session.get(f"{API_BASE}/tasks/")
            
            if response.status_code == 200:
                result = response.json()
                print_success(f"Retrieved {len(result)} tasks")
                print_result(result)
                
                # Test with filters
                print_info("Testing with filters...")
                if self.test_task_list_id:
                    params = {
                        "task_list_id": self.test_task_list_id,
                        "status": "pending",
                        "priority": "high"
                    }
                    filtered_response = self.session.get(f"{API_BASE}/tasks/", params=params)
                    if filtered_response.status_code == 200:
                        filtered_result = filtered_response.json()
                        print_success(f"Filtered query returned {len(filtered_result)} tasks")
                        print_result(filtered_result)
                
                return True
            else:
                print_error(f"Get tasks failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Get tasks error: {str(e)}")
            return False
    
    def test_get_task_stats(self):
        print_test("Get Task Statistics")
        
        try:
            response = self.session.get(f"{API_BASE}/tasks/stats")
            
            if response.status_code == 200:
                result = response.json()
                print_success("Task statistics retrieved successfully")
                print_result(result)
                
                # Test with filters
                if self.test_task_list_id:
                    print_info("Testing stats with task_list_id filter...")
                    params = {"task_list_id": self.test_task_list_id}
                    filtered_response = self.session.get(f"{API_BASE}/tasks/stats", params=params)
                    if filtered_response.status_code == 200:
                        filtered_result = filtered_response.json()
                        print_success("Filtered stats retrieved successfully")
                        print_result(filtered_result)
                
                return True
            else:
                print_error(f"Get task stats failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Get task stats error: {str(e)}")
            return False
    
    def test_update_task_status(self):
        print_test("Update Task Status")
        
        if not self.test_task_id:
            print_error("No task ID available for updating status")
            return False
        
        status_data = {"status": "in_progress"}
        
        try:
            response = self.session.patch(f"{API_BASE}/tasks/{self.test_task_id}/status", json=status_data)
            
            if response.status_code == 200:
                result = response.json()
                print_success("Task status updated successfully")
                print_result(result)
                return True
            else:
                print_error(f"Update task status failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Update task status error: {str(e)}")
            return False
    
    def test_update_task(self):
        print_test("Update Task (Full Update)")
        
        if not self.test_task_id:
            print_error("No task ID available for updating")
            return False
        
        update_data = {
            "title": "Updated Test Task",
            "description": "This task has been updated",
            "priority": "medium"
        }
        
        try:
            response = self.session.put(f"{API_BASE}/tasks/{self.test_task_id}", json=update_data)
            
            if response.status_code == 200:
                result = response.json()
                print_success("Task updated successfully")
                print_result(result)
                return True
            else:
                print_error(f"Update task failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Update task error: {str(e)}")
            return False
    
    def test_update_task_list(self):
        print_test("Update Task List")
        
        if not self.test_task_list_id:
            print_error("No task list ID available for updating")
            return False
        
        update_data = {
            "name": "Updated Test Task List",
            "description": "This task list has been updated"
        }
        
        try:
            response = self.session.put(f"{API_BASE}/task-lists/{self.test_task_list_id}", json=update_data)
            
            if response.status_code == 200:
                result = response.json()
                print_success("Task list updated successfully")
                print_result(result)
                return True
            else:
                print_error(f"Update task list failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Update task list error: {str(e)}")
            return False
    
    def test_delete_task(self):
        print_test("Delete Task")
        
        if not self.test_task_id:
            print_error("No task ID available for deletion")
            return False
        
        try:
            response = self.session.delete(f"{API_BASE}/tasks/{self.test_task_id}")
            
            if response.status_code == 200:
                result = response.json()
                print_success("Task deleted successfully")
                print_result(result)
                self.test_task_id = None  # Clear the task ID
                return True
            else:
                print_error(f"Delete task failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Delete task error: {str(e)}")
            return False
    
    def test_delete_task_list(self):
        print_test("Delete Task List")
        
        if not self.test_task_list_id:
            print_error("No task list ID available for deletion")
            return False
        
        try:
            response = self.session.delete(f"{API_BASE}/task-lists/{self.test_task_list_id}")
            
            if response.status_code == 200:
                result = response.json()
                print_success("Task list deleted successfully")
                print_result(result)
                self.test_task_list_id = None  # Clear the task list ID
                return True
            else:
                print_error(f"Delete task list failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Delete task list error: {str(e)}")
            return False
    
    def run_all_tests(self):
        print(f"{Colors.BOLD}{Colors.GREEN}")
        print("🚀 Starting REST API Testing Suite")
        print("📋 Testing Task Challenge API")
        print(f"🌐 Base URL: {BASE_URL}")
        print(f"{Colors.ENDC}")
        
        test_results = {}
        
        # Authentication flow
        user_data = self.test_user_registration()
        test_results["user_registration"] = user_data is not None
        
        if user_data:
            test_results["user_login"] = self.test_user_login(user_data)
            if self.access_token:
                test_results["get_current_user"] = self.test_get_current_user()
                
                # Task Lists flow
                test_results["create_task_list"] = self.test_create_task_list()
                test_results["get_task_lists"] = self.test_get_task_lists()
                test_results["get_single_task_list"] = self.test_get_single_task_list()
                test_results["update_task_list"] = self.test_update_task_list()
                
                # Tasks flow
                test_results["create_task"] = self.test_create_task()
                test_results["get_tasks"] = self.test_get_tasks()
                test_results["get_task_stats"] = self.test_get_task_stats()
                test_results["update_task_status"] = self.test_update_task_status()
                test_results["update_task"] = self.test_update_task()
                
                # Cleanup
                test_results["delete_task"] = self.test_delete_task()
                test_results["delete_task_list"] = self.test_delete_task_list()
        
        # Print summary
        self.print_test_summary(test_results)
    
    def print_test_summary(self, results: dict):
        print(f"\n{Colors.BOLD}{Colors.CYAN}")
        print("="*80)
        print("📊 TEST SUMMARY")
        print("="*80)
        print(f"{Colors.ENDC}")
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, passed_test in results.items():
            status = f"{Colors.GREEN}✅ PASSED" if passed_test else f"{Colors.RED}❌ FAILED"
            print(f"{status}{Colors.ENDC} - {test_name.replace('_', ' ').title()}")
        
        print(f"\n{Colors.BOLD}")
        if passed == total:
            print(f"{Colors.GREEN}🎉 All {total} tests PASSED! 🎉")
        else:
            print(f"{Colors.YELLOW}📋 {passed}/{total} tests passed")
            print(f"{Colors.RED}⚠️  {total - passed} tests failed")
        print(f"{Colors.ENDC}")

def main():
    try:
        # Check if API is accessible
        response = requests.get(f"{BASE_URL}/ping", timeout=5)
        if response.status_code != 200:
            raise Exception("API health check failed")
    except Exception as e:
        print_error(f"Cannot connect to API at {BASE_URL}")
        print_error("Make sure the Docker container is running on port 8000")
        print_error(f"Error: {str(e)}")
        return
    
    tester = RESTAPITester()
    tester.run_all_tests()

if __name__ == "__main__":
    main() 