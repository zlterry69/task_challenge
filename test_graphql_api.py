#!/usr/bin/env python3
"""
Script para testear todas las funcionalidades GraphQL API del Task Challenge
Requiere que el proyecto esté corriendo en Docker en localhost:8000
"""

import json
import requests
from datetime import datetime, timedelta
from typing import Optional

# Configuración
BASE_URL = "http://localhost:8000"
GRAPHQL_ENDPOINT = f"{BASE_URL}/graphql"

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

def print_query(query: str):
    print(f"{Colors.YELLOW}📝 GraphQL Query/Mutation:{Colors.ENDC}")
    print(f"{Colors.CYAN}{query}{Colors.ENDC}")

class GraphQLAPITester:
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
    
    def execute_graphql(self, query: str, variables: dict = None):
        """Execute a GraphQL query/mutation with token if available"""
        payload = {
            "query": query,
            "variables": variables or {}
        }

        headers = {
            "Content-Type": "application/json"
        }

        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"  # 🔹 Forzado siempre

        response = requests.post(  # 👈 Usar requests.post en lugar de self.session.post
            GRAPHQL_ENDPOINT,
            json=payload,
            headers=headers
        )
        return response

    
    def test_user_registration(self):
        print_test("User Registration (GraphQL)")
        
        # Test data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        mutation = '''
        mutation Register($input: UserCreateInput!) {
            register(input: $input) {
                id
                email
                fullName
            }
        }
        '''
        
        variables = {
            "input": {
                "email": f"test_graphql_{timestamp}@example.com",
                "fullName": f"Test GraphQL User {timestamp}",
                "password": "testpassword123"
            }
        }
        
        print_query(mutation)
        
        try:
            response = self.execute_graphql(mutation, variables)
            
            if response.status_code == 200:
                result = response.json()
                if "errors" in result:
                    print_error(f"GraphQL errors: {result['errors']}")
                    return None
                
                user_data = result.get("data", {}).get("register")
                if user_data:
                    self.test_user_id = user_data.get("id")
                    print_success(f"User registered successfully with ID: {self.test_user_id}")
                    print_result(user_data)
                    # Return the original input for login
                    return variables["input"]
                else:
                    print_error("No user data returned")
                    return None
            else:
                print_error(f"Registration failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print_error(f"Registration error: {str(e)}")
            return None
    
    def test_user_login(self, user_data: dict):
        print_test("User Login (GraphQL)")
        
        mutation = '''
        mutation Login($loginInput: UserLoginInput!) {
            login(loginInput: $loginInput) {
                accessToken
                tokenType
                user {
                    id
                    email
                    fullName
                }
            }
        }
        '''
        
        variables = {
            "loginInput": {
                "email": user_data["email"],
                "password": user_data["password"]
            }
        }
        
        print_query(mutation)
        
        try:
            response = self.execute_graphql(mutation, variables)
            
            if response.status_code == 200:
                result = response.json()
                if "errors" in result:
                    print_error(f"GraphQL errors: {result['errors']}")
                    return False
                
                login_data = result.get("data", {}).get("login")
                if login_data:
                    self.access_token = login_data.get("accessToken")
                    print_success("Login successful")
                    print_result(login_data)
                    self.set_auth_header()
                    return True
                else:
                    print_error("No login data returned")
                    return False
            else:
                print_error(f"Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Login error: {str(e)}")
            return False
    
    def test_get_current_user(self):
        print_test("Get Current User (GraphQL)")
        
        query = '''
        query Me {
            me {
                id
                email
                fullName
            }
        }
        '''
        
        print_query(query)
        
        try:
            response = self.execute_graphql(query)
            
            if response.status_code == 200:
                result = response.json()
                if "errors" in result:
                    print_error(f"GraphQL errors: {result['errors']}")
                    return False
                
                user_data = result.get("data", {}).get("me")
                if user_data:
                    print_success("User info retrieved successfully")
                    print_result(user_data)
                    return True
                else:
                    print_error("No user data returned")
                    return False
            else:
                print_error(f"Get user failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Get user error: {str(e)}")
            return False
    
    def test_create_task_list(self):
        print_test("Create Task List (GraphQL)")
        
        mutation = '''
        mutation CreateTaskList($input: TaskListCreateInput!) {
            createTaskList(input: $input) {
                id
                name
                description
                ownerId
                completionPercentage
                taskCount
                createdAt
                updatedAt
            }
        }
        '''
        
        variables = {
            "input": {
                "name": f"GraphQL Test List {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "A test task list created by GraphQL"
            }
        }
        
        print_query(mutation)
        
        try:
            response = self.execute_graphql(mutation, variables)
            
            if response.status_code == 200:
                result = response.json()
                if "errors" in result:
                    print_error(f"GraphQL errors: {result['errors']}")
                    return False
                
                task_list_data = result.get("data", {}).get("createTaskList")
                if task_list_data:
                    self.test_task_list_id = task_list_data.get("id")
                    print_success(f"Task list created successfully with ID: {self.test_task_list_id}")
                    print_result(task_list_data)
                    return True
                else:
                    print_error("No task list data returned")
                    return False
            else:
                print_error(f"Create task list failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Create task list error: {str(e)}")
            return False
    
    def test_get_task_lists(self):
        print_test("Get All Task Lists (GraphQL)")
        
        query = '''
        query GetTaskLists {
            taskLists {
                id
                name
                description
                ownerId
                completionPercentage
                taskCount
                createdAt
                updatedAt
            }
        }
        '''
        
        print_query(query)
        
        try:
            response = self.execute_graphql(query)
            
            if response.status_code == 200:
                result = response.json()
                if "errors" in result:
                    print_error(f"GraphQL errors: {result['errors']}")
                    return False
                
                task_lists = result.get("data", {}).get("taskLists", [])
                print_success(f"Retrieved {len(task_lists)} task lists")
                print_result(task_lists)
                return True
            else:
                print_error(f"Get task lists failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Get task lists error: {str(e)}")
            return False
    
    def test_get_single_task_list(self):
        print_test("Get Single Task List (GraphQL)")
        
        if not self.test_task_list_id:
            print_error("No task list ID available for testing")
            return False
        
        query = '''
        query GetTaskList($id: Int!) {
            taskList(id: $id) {
                id
                name
                description
                ownerId
                completionPercentage
                taskCount
                createdAt
                updatedAt
            }
        }
        '''
        
        variables = {"id": self.test_task_list_id}
        
        print_query(query)
        
        try:
            response = self.execute_graphql(query, variables)
            
            if response.status_code == 200:
                result = response.json()
                if "errors" in result:
                    print_error(f"GraphQL errors: {result['errors']}")
                    return False
                
                task_list_data = result.get("data", {}).get("taskList")
                if task_list_data:
                    print_success("Task list retrieved successfully")
                    print_result(task_list_data)
                    return True
                else:
                    print_error("No task list data returned")
                    return False
            else:
                print_error(f"Get task list failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Get task list error: {str(e)}")
            return False
    
    def test_create_task(self):
        print_test("Create Task (GraphQL)")
        
        if not self.test_task_list_id:
            print_error("No task list ID available for creating task")
            return False
        
        # Note: GraphQL doesn't have createTask mutation according to the resolvers I read
        # Let me check if there's a createTask mutation
        mutation = '''
        mutation CreateTask($input: TaskCreateInput!) {
            createTask(input: $input) {
                id
                title
                description
                status
                priority
                taskListId
                assignedTo
                assigneeName
                dueDate
                isOverdue
                createdAt
                updatedAt
            }
        }
        '''
        
        # Create task with due date
        due_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
        variables = {
            "input": {
                "title": f"GraphQL Test Task {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "A test task created by GraphQL",
                "taskListId": self.test_task_list_id,
                "priority": "HIGH",
                "status": "PENDING",
                "dueDate": due_date
            }
        }
        
        print_query(mutation)
        
        try:
            response = self.execute_graphql(mutation, variables)
            
            if response.status_code == 200:
                result = response.json()
                if "errors" in result:
                    print_error(f"GraphQL errors: {result['errors']}")
                    return False
                
                task_data = result.get("data", {}).get("createTask")
                if task_data:
                    self.test_task_id = task_data.get("id")
                    print_success(f"Task created successfully with ID: {self.test_task_id}")
                    print_result(task_data)
                    return True
                else:
                    print_error("No task data returned")
                    return False
            else:
                print_error(f"Create task failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Create task error: {str(e)}")
            return False
    
    def test_get_tasks(self):
        print_test("Get All Tasks (GraphQL)")
        
        query = '''
        query GetTasks($filter: TaskFilterInput) {
            tasks(filter: $filter) {
                id
                title
                description
                status
                priority
                taskListId
                assignedTo
                assigneeName
                dueDate
                isOverdue
                createdAt
                updatedAt
            }
        }
        '''
        
        print_query(query)
        
        try:
            # Test without filters
            response = self.execute_graphql(query)
            
            if response.status_code == 200:
                result = response.json()
                if "errors" in result:
                    print_error(f"GraphQL errors: {result['errors']}")
                    return False
                
                tasks = result.get("data", {}).get("tasks", [])
                print_success(f"Retrieved {len(tasks)} tasks")
                print_result(tasks)
                
                # Test with filters
                if self.test_task_list_id:
                    print_info("Testing with filters...")
                    filter_variables = {
                        "filter": {
                            "taskListId": self.test_task_list_id,
                            "status": "PENDING",
                            "priority": "HIGH"
                        }
                    }
                    filtered_response = self.execute_graphql(query, filter_variables)
                    if filtered_response.status_code == 200:
                        filtered_result = filtered_response.json()
                        if "errors" not in filtered_result:
                            filtered_tasks = filtered_result.get("data", {}).get("tasks", [])
                            print_success(f"Filtered query returned {len(filtered_tasks)} tasks")
                            print_result(filtered_tasks)
                
                return True
            else:
                print_error(f"Get tasks failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Get tasks error: {str(e)}")
            return False
    
    def test_update_task(self):
        print_test("Update Task (GraphQL)")
        
        if not self.test_task_id:
            print_error("No task ID available for updating")
            return False
        
        mutation = '''
        mutation UpdateTask($id: Int!, $input: TaskUpdateInput!) {
            updateTask(id: $id, input: $input) {
                id
                title
                description
                status
                priority
                taskListId
                assignedTo
                assigneeName
                dueDate
                isOverdue
                createdAt
                updatedAt
            }
        }
        '''
        
        variables = {
            "id": self.test_task_id,
            "input": {
                "title": "Updated GraphQL Test Task",
                "description": "This task has been updated via GraphQL",
                "status": "IN_PROGRESS",
                "priority": "MEDIUM"
            }
        }
        
        print_query(mutation)
        
        try:
            response = self.execute_graphql(mutation, variables)
            
            if response.status_code == 200:
                result = response.json()
                if "errors" in result:
                    print_error(f"GraphQL errors: {result['errors']}")
                    return False
                
                task_data = result.get("data", {}).get("updateTask")
                if task_data:
                    print_success("Task updated successfully")
                    print_result(task_data)
                    return True
                else:
                    print_error("No task data returned")
                    return False
            else:
                print_error(f"Update task failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Update task error: {str(e)}")
            return False
    
    def test_update_task_list(self):
        print_test("Update Task List (GraphQL)")
        
        if not self.test_task_list_id:
            print_error("No task list ID available for updating")
            return False
        
        mutation = '''
        mutation UpdateTaskList($id: Int!, $input: TaskListUpdateInput!) {
            updateTaskList(id: $id, input: $input) {
                id
                name
                description
                ownerId
                completionPercentage
                taskCount
                createdAt
                updatedAt
            }
        }
        '''
        
        variables = {
            "id": self.test_task_list_id,
            "input": {
                "name": "Updated GraphQL Test List",
                "description": "This task list has been updated via GraphQL"
            }
        }
        
        print_query(mutation)
        
        try:
            response = self.execute_graphql(mutation, variables)
            
            if response.status_code == 200:
                result = response.json()
                if "errors" in result:
                    print_error(f"GraphQL errors: {result['errors']}")
                    return False
                
                task_list_data = result.get("data", {}).get("updateTaskList")
                if task_list_data:
                    print_success("Task list updated successfully")
                    print_result(task_list_data)
                    return True
                else:
                    print_error("No task list data returned")
                    return False
            else:
                print_error(f"Update task list failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Update task list error: {str(e)}")
            return False
    
    def test_delete_task(self):
        print_test("Delete Task (GraphQL)")
        
        if not self.test_task_id:
            print_error("No task ID available for deletion")
            return False
        
        mutation = '''
        mutation DeleteTask($id: Int!) {
            deleteTask(id: $id)
        }
        '''
        
        variables = {"id": self.test_task_id}
        
        print_query(mutation)
        
        try:
            response = self.execute_graphql(mutation, variables)
            
            if response.status_code == 200:
                result = response.json()
                if "errors" in result:
                    print_error(f"GraphQL errors: {result['errors']}")
                    return False
                
                delete_result = result.get("data", {}).get("deleteTask")
                if delete_result:
                    print_success("Task deleted successfully")
                    print_result({"deleted": delete_result})
                    self.test_task_id = None  # Clear the task ID
                    return True
                else:
                    print_error("Task deletion failed")
                    return False
            else:
                print_error(f"Delete task failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Delete task error: {str(e)}")
            return False
    
    def test_delete_task_list(self):
        print_test("Delete Task List (GraphQL)")
        
        if not self.test_task_list_id:
            print_error("No task list ID available for deletion")
            return False
        
        mutation = '''
        mutation DeleteTaskList($id: Int!) {
            deleteTaskList(id: $id)
        }
        '''
        
        variables = {"id": self.test_task_list_id}
        
        print_query(mutation)
        
        try:
            response = self.execute_graphql(mutation, variables)
            
            if response.status_code == 200:
                result = response.json()
                if "errors" in result:
                    print_error(f"GraphQL errors: {result['errors']}")
                    return False
                
                delete_result = result.get("data", {}).get("deleteTaskList")
                if delete_result:
                    print_success("Task list deleted successfully")
                    print_result({"deleted": delete_result})
                    self.test_task_list_id = None  # Clear the task list ID
                    return True
                else:
                    print_error("Task list deletion failed")
                    return False
            else:
                print_error(f"Delete task list failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Delete task list error: {str(e)}")
            return False
    
    def test_graphql_introspection(self):
        print_test("GraphQL Schema Introspection")
        
        query = '''
        query IntrospectionQuery {
            __schema {
                types {
                    name
                    kind
                }
                queryType {
                    name
                    fields {
                        name
                        type {
                            name
                        }
                    }
                }
                mutationType {
                    name
                    fields {
                        name
                        type {
                            name
                        }
                    }
                }
            }
        }
        '''
        
        print_query(query)
        
        try:
            response = self.execute_graphql(query)
            
            if response.status_code == 200:
                result = response.json()
                if "errors" in result:
                    print_error(f"GraphQL errors: {result['errors']}")
                    return False
                
                schema_data = result.get("data", {}).get("__schema")
                if schema_data:
                    print_success("Schema introspection successful")
                    
                    # Show available queries
                    query_fields = schema_data.get("queryType", {}).get("fields", [])
                    print_info(f"Available Queries: {[field['name'] for field in query_fields]}")
                    
                    # Show available mutations
                    mutation_fields = schema_data.get("mutationType", {}).get("fields", [])
                    print_info(f"Available Mutations: {[field['name'] for field in mutation_fields]}")
                    
                    return True
                else:
                    print_error("No schema data returned")
                    return False
            else:
                print_error(f"Introspection failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Introspection error: {str(e)}")
            return False
    
    def run_all_tests(self):
        print(f"{Colors.BOLD}{Colors.GREEN}")
        print("🚀 Starting GraphQL API Testing Suite")
        print("📋 Testing Task Challenge GraphQL API")
        print(f"🌐 GraphQL Endpoint: {GRAPHQL_ENDPOINT}")
        print(f"{Colors.ENDC}")
        
        test_results = {}
        
        # Start with introspection
        test_results["schema_introspection"] = self.test_graphql_introspection()
        
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
                test_results["update_task"] = self.test_update_task()
                
                # Cleanup
                test_results["delete_task"] = self.test_delete_task()
                test_results["delete_task_list"] = self.test_delete_task_list()
        
        # Print summary
        self.print_test_summary(test_results)
    
    def print_test_summary(self, results: dict):
        print(f"\n{Colors.BOLD}{Colors.CYAN}")
        print("="*80)
        print("📊 GRAPHQL TEST SUMMARY")
        print("="*80)
        print(f"{Colors.ENDC}")
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, passed_test in results.items():
            status = f"{Colors.GREEN}✅ PASSED" if passed_test else f"{Colors.RED}❌ FAILED"
            print(f"{status}{Colors.ENDC} - {test_name.replace('_', ' ').title()}")
        
        print(f"\n{Colors.BOLD}")
        if passed == total:
            print(f"{Colors.GREEN}🎉 All {total} GraphQL tests PASSED! 🎉")
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
    
    tester = GraphQLAPITester()
    tester.run_all_tests()

if __name__ == "__main__":
    main() 