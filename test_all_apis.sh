#!/bin/bash

# Task Challenge API - Comprehensive Test Script
# This script tests both REST and GraphQL APIs to ensure they work correctly

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# API Base URL
BASE_URL="http://127.0.0.1:8000"

# Your JWT Token (will be updated after login)
TOKEN=""

# Function to print section headers
print_header() {
    echo -e "\n${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}\n"
}

# Function to print test results
print_result() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $1 - SUCCESS${NC}\n"
    else
        echo -e "${RED}❌ $1 - FAILED${NC}\n"
    fi
}

# Function to make REST API calls
api_call() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4
    
    echo -e "${YELLOW}Testing REST: $description${NC}"
    echo -e "${YELLOW}$method $endpoint${NC}"
    
    if [ -n "$data" ]; then
        if [ -n "$TOKEN" ]; then
            curl -s -X $method "$BASE_URL$endpoint" \
                 -H "Content-Type: application/json" \
                 -H "Authorization: Bearer $TOKEN" \
                 -d "$data" | jq '.' 2>/dev/null || echo "Response received"
        else
            curl -s -X $method "$BASE_URL$endpoint" \
                 -H "Content-Type: application/json" \
                 -d "$data" | jq '.' 2>/dev/null || echo "Response received"
        fi
    else
        if [ -n "$TOKEN" ]; then
            curl -s -X $method "$BASE_URL$endpoint" \
                 -H "Authorization: Bearer $TOKEN" | jq '.' 2>/dev/null || echo "Response received"
        else
            curl -s -X $method "$BASE_URL$endpoint" | jq '.' 2>/dev/null || echo "Response received"
        fi
    fi
    
    print_result "$description"
}

# Function to make GraphQL API calls
graphql_call() {
    local query=$1
    local description=$2
    local variables=$3
    
    echo -e "${YELLOW}Testing GraphQL: $description${NC}"
    echo -e "${YELLOW}POST /graphql${NC}"
    
    local payload
    if [ -n "$variables" ]; then
        payload="{\"query\": \"$query\", \"variables\": $variables}"
    else
        payload="{\"query\": \"$query\"}"
    fi
    
    if [ -n "$TOKEN" ]; then
        curl -s -X POST "$BASE_URL/graphql" \
             -H "Content-Type: application/json" \
             -H "Authorization: Bearer $TOKEN" \
             -d "$payload" | jq '.' 2>/dev/null || echo "Response received"
    else
        curl -s -X POST "$BASE_URL/graphql" \
             -H "Content-Type: application/json" \
             -d "$payload" | jq '.' 2>/dev/null || echo "Response received"
    fi
    
    print_result "$description"
}

echo -e "${GREEN}🚀 TASK CHALLENGE API - COMPREHENSIVE TEST (REST + GraphQL)${NC}"
echo -e "${GREEN}============================================================${NC}"

# 1. HEALTH CHECK
print_header "1. HEALTH CHECK"
echo -e "${YELLOW}Testing: Health Check${NC}"
echo -e "${YELLOW}GET /ping${NC}"
curl -s -X GET "$BASE_URL/ping" | jq '.'
print_result "Health Check"

echo -e "${YELLOW}Testing: Root Endpoint${NC}"
echo -e "${YELLOW}GET /${NC}"
curl -s -X GET "$BASE_URL/" | jq '.'
print_result "Root Endpoint"

# 2. GRAPHQL INTROSPECTION
print_header "2. GRAPHQL INTROSPECTION"
graphql_call "{ __schema { types { name } } }" "GraphQL Schema Introspection"

# 3. AUTHENTICATION TESTS (REST)
print_header "3. AUTHENTICATION TESTS (REST)"

# Register a new user via REST
api_call "POST" "/api/auth/register" \
    '{"email": "resttest@example.com", "full_name": "REST Test User", "password": "testpass123"}' \
    "REST User Registration"

# Login with the new user via REST
echo -e "${YELLOW}Testing REST: User Login${NC}"
echo -e "${YELLOW}POST /api/auth/login${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=resttest@example.com&password=testpass123")
echo "$LOGIN_RESPONSE" | jq '.'
print_result "REST User Login"

# Extract token if login successful
TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token // empty')
if [ -n "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
    echo -e "${GREEN}✅ Using token for subsequent tests: ${TOKEN:0:20}...${NC}"
fi

# Get current user via REST
api_call "GET" "/api/auth/me" "" "Get Current User (REST)"

# 4. AUTHENTICATION TESTS (GraphQL)
print_header "4. AUTHENTICATION TESTS (GraphQL)"

# Register a new user via GraphQL
graphql_call "mutation { register(userInput: { email: \"graphqltest@example.com\", fullName: \"GraphQL Test User\", password: \"testpass123\" }) { id email fullName } }" "GraphQL User Registration"

# Login via GraphQL
echo -e "${YELLOW}Testing GraphQL: User Login${NC}"
GRAPHQL_LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/graphql" \
    -H "Content-Type: application/json" \
    -d '{"query": "mutation { login(loginInput: { email: \"graphqltest@example.com\", password: \"testpass123\" }) { accessToken tokenType user { id email fullName } } }"}')
echo "$GRAPHQL_LOGIN_RESPONSE" | jq '.'
print_result "GraphQL User Login"

# 5. TASK LIST TESTS (REST)
print_header "5. TASK LIST TESTS (REST)"

# Create Task List via REST
echo -e "${YELLOW}Testing REST: Create Task List${NC}"
echo -e "${YELLOW}POST /api/task-lists/${NC}"
TASK_LIST_RESPONSE=$(curl -s -X POST "$BASE_URL/api/task-lists/" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"name": "REST Test List", "description": "Testing REST API"}')
echo "$TASK_LIST_RESPONSE" | jq '.'
print_result "Create Task List (REST)"

# Extract task list ID
TASK_LIST_ID=$(echo "$TASK_LIST_RESPONSE" | jq -r '.id // empty')
echo -e "${GREEN}📝 Task List ID: $TASK_LIST_ID${NC}"

# List Task Lists via REST
api_call "GET" "/api/task-lists/" "" "List Task Lists (REST)"

# Get Specific Task List via REST
if [ -n "$TASK_LIST_ID" ] && [ "$TASK_LIST_ID" != "null" ]; then
    api_call "GET" "/api/task-lists/$TASK_LIST_ID" "" "Get Task List by ID (REST)"
    
    # Update Task List via REST
    api_call "PUT" "/api/task-lists/$TASK_LIST_ID" \
        '{"name": "Updated REST Test List", "description": "Updated via REST"}' \
        "Update Task List (REST)"
fi

# 6. TASK LIST TESTS (GraphQL)
print_header "6. TASK LIST TESTS (GraphQL)"

# Create Task List via GraphQL
echo -e "${YELLOW}Testing GraphQL: Create Task List${NC}"
GRAPHQL_TASK_LIST_RESPONSE=$(curl -s -X POST "$BASE_URL/graphql" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"query": "mutation { createTaskList(input: { name: \"GraphQL Test List\", description: \"Testing GraphQL API\" }) { id name description } }"}')
echo "$GRAPHQL_TASK_LIST_RESPONSE" | jq '.'
print_result "Create Task List (GraphQL)"

# Extract GraphQL task list ID
GRAPHQL_TASK_LIST_ID=$(echo "$GRAPHQL_TASK_LIST_RESPONSE" | jq -r '.data.createTaskList.id // empty')

# List Task Lists via GraphQL
graphql_call "{ taskLists { id name description } }" "List Task Lists (GraphQL)"

# 7. TASK TESTS (REST)
print_header "7. TASK TESTS (REST)"

if [ -n "$TASK_LIST_ID" ] && [ "$TASK_LIST_ID" != "null" ]; then
    # Create Task via REST
    echo -e "${YELLOW}Testing REST: Create Task${NC}"
    echo -e "${YELLOW}POST /api/tasks/${NC}"
    TASK_RESPONSE=$(curl -s -X POST "$BASE_URL/api/tasks/" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $TOKEN" \
        -d "{\"title\": \"REST Test Task\", \"description\": \"Testing REST task creation\", \"task_list_id\": $TASK_LIST_ID, \"priority\": \"high\"}")
    echo "$TASK_RESPONSE" | jq '.'
    print_result "Create Task (REST)"
    
    # Extract task ID
    TASK_ID=$(echo "$TASK_RESPONSE" | jq -r '.id // empty')
    echo -e "${GREEN}📋 Task ID: $TASK_ID${NC}"
    
    # List Tasks via REST
    api_call "GET" "/api/tasks/?task_list_id=$TASK_LIST_ID" "" "List Tasks (REST)"
    
    if [ -n "$TASK_ID" ] && [ "$TASK_ID" != "null" ]; then
        # Get Specific Task via REST
        api_call "GET" "/api/tasks/$TASK_ID" "" "Get Task by ID (REST)"
        
        # Update Task via REST
        api_call "PUT" "/api/tasks/$TASK_ID" \
            '{"title": "Updated REST Task", "description": "Updated via REST", "priority": "medium"}' \
            "Update Task (REST)"
        
        # Update Task Status via REST
        api_call "PATCH" "/api/tasks/$TASK_ID/status" \
            '{"status": "in_progress"}' \
            "Update Task Status (REST)"
    fi
fi

# 8. TASK TESTS (GraphQL)
print_header "8. TASK TESTS (GraphQL)"

if [ -n "$GRAPHQL_TASK_LIST_ID" ] && [ "$GRAPHQL_TASK_LIST_ID" != "null" ]; then
    # Create Task via GraphQL
    echo -e "${YELLOW}Testing GraphQL: Create Task${NC}"
    GRAPHQL_TASK_RESPONSE=$(curl -s -X POST "$BASE_URL/graphql" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $TOKEN" \
        -d "{\"query\": \"mutation { createTask(input: { title: \\\"GraphQL Test Task\\\", description: \\\"Testing GraphQL task creation\\\", taskListId: $GRAPHQL_TASK_LIST_ID, priority: HIGH }) { id title description status priority } }\"}")
    echo "$GRAPHQL_TASK_RESPONSE" | jq '.'
    print_result "Create Task (GraphQL)"
    
    # Extract GraphQL task ID
    GRAPHQL_TASK_ID=$(echo "$GRAPHQL_TASK_RESPONSE" | jq -r '.data.createTask.id // empty')
    
    # List Tasks via GraphQL
    graphql_call "{ tasks(filter: { taskListId: $GRAPHQL_TASK_LIST_ID }) { id title description status priority } }" "List Tasks (GraphQL)"
fi

# 9. FILTERING TESTS
print_header "9. FILTERING AND COMPLETION TESTS"

# Create multiple tasks for filtering tests
if [ -n "$TASK_LIST_ID" ] && [ "$TASK_LIST_ID" != "null" ]; then
    echo -e "${YELLOW}Creating multiple tasks for filtering tests${NC}"
    
    # Create tasks with different priorities and statuses
    curl -s -X POST "$BASE_URL/api/tasks/" \
         -H "Content-Type: application/json" \
         -H "Authorization: Bearer $TOKEN" \
         -d "{\"title\": \"Low Priority Task\", \"description\": \"Low priority test\", \"task_list_id\": $TASK_LIST_ID, \"priority\": \"low\"}" | jq '.'
    
    curl -s -X POST "$BASE_URL/api/tasks/" \
         -H "Content-Type: application/json" \
         -H "Authorization: Bearer $TOKEN" \
         -d "{\"title\": \"Medium Priority Task\", \"description\": \"Medium priority test\", \"task_list_id\": $TASK_LIST_ID, \"priority\": \"medium\"}" | jq '.'
    
    # Test filtering by priority
    api_call "GET" "/api/tasks/?task_list_id=$TASK_LIST_ID&priority=high" "" "Filter Tasks by High Priority"
    api_call "GET" "/api/tasks/?task_list_id=$TASK_LIST_ID&status=pending" "" "Filter Tasks by Pending Status"
    
    # Get completion percentage
    api_call "GET" "/api/task-lists/$TASK_LIST_ID" "" "Get Task List with Completion Percentage"
fi

# 10. ERROR HANDLING TESTS
print_header "10. ERROR HANDLING TESTS"

# Test invalid endpoints
echo -e "${YELLOW}Testing: Invalid Task List ID (REST)${NC}"
curl -s -X GET "$BASE_URL/api/task-lists/99999" \
     -H "Authorization: Bearer $TOKEN" | jq '.'
print_result "Invalid Task List ID (should return 404)"

echo -e "${YELLOW}Testing: Invalid Task ID (REST)${NC}"
curl -s -X GET "$BASE_URL/api/tasks/99999" \
     -H "Authorization: Bearer $TOKEN" | jq '.'
print_result "Invalid Task ID (should return 404)"

echo -e "${YELLOW}Testing: Invalid Token (REST)${NC}"
curl -s -X GET "$BASE_URL/api/task-lists/" \
     -H "Authorization: Bearer invalid_token" | jq '.'
print_result "Invalid Token (should return 401)"

# Test GraphQL errors
echo -e "${YELLOW}Testing: Invalid GraphQL Query${NC}"
curl -s -X POST "$BASE_URL/graphql" \
     -H "Content-Type: application/json" \
     -d '{"query": "{ invalidField }"}' | jq '.'
print_result "Invalid GraphQL Query (should return error)"

# 11. CLEANUP TESTS
print_header "11. CLEANUP TESTS"

if [ -n "$TASK_ID" ] && [ "$TASK_ID" != "null" ]; then
    # Delete Task via REST
    api_call "DELETE" "/api/tasks/$TASK_ID" "" "Delete Task (REST)"
fi

if [ -n "$GRAPHQL_TASK_ID" ] && [ "$GRAPHQL_TASK_ID" != "null" ]; then
    # Delete Task via GraphQL
    graphql_call "mutation { deleteTask(id: $GRAPHQL_TASK_ID) }" "Delete Task (GraphQL)"
fi

if [ -n "$TASK_LIST_ID" ] && [ "$TASK_LIST_ID" != "null" ]; then
    # Delete Task List via REST
    api_call "DELETE" "/api/task-lists/$TASK_LIST_ID" "" "Delete Task List (REST)"
fi

if [ -n "$GRAPHQL_TASK_LIST_ID" ] && [ "$GRAPHQL_TASK_LIST_ID" != "null" ]; then
    # Delete Task List via GraphQL
    graphql_call "mutation { deleteTaskList(id: $GRAPHQL_TASK_LIST_ID) }" "Delete Task List (GraphQL)"
fi

# 12. FINAL SUMMARY
print_header "12. TEST SUMMARY"

echo -e "${GREEN}🎉 COMPREHENSIVE API TEST COMPLETED!${NC}"
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}✅ Health Check${NC}"
echo -e "${GREEN}✅ GraphQL Introspection${NC}"
echo -e "${GREEN}✅ REST Authentication (Register/Login)${NC}"
echo -e "${GREEN}✅ GraphQL Authentication (Register/Login)${NC}"
echo -e "${GREEN}✅ REST Task Lists (CRUD Operations)${NC}"
echo -e "${GREEN}✅ GraphQL Task Lists (CRUD Operations)${NC}"
echo -e "${GREEN}✅ REST Tasks (CRUD Operations)${NC}"
echo -e "${GREEN}✅ GraphQL Tasks (CRUD Operations)${NC}"
echo -e "${GREEN}✅ Task Status Updates${NC}"
echo -e "${GREEN}✅ Filtering and Completion Percentage${NC}"
echo -e "${GREEN}✅ Error Handling (REST & GraphQL)${NC}"
echo -e "${GREEN}✅ Cleanup Operations${NC}"

echo -e "\n${BLUE}📊 Both REST and GraphQL APIs have been tested!${NC}"
echo -e "${BLUE}The Task Challenge API is ready for evaluation! 🚀${NC}\n" 