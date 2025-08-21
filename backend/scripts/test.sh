#!/bin/bash
# TripCraft AI Backend - Test Execution Script
# Comprehensive test runner with multiple execution modes

set -e

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
BLUE='\\033[0;34m'
PURPLE='\\033[0;35m'
CYAN='\\033[0;36m'
NC='\\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Default values
API_URL="http://localhost:8000"
TEST_TYPE="all"
PARALLEL=false
GENERATE_REPORTS=true
VERBOSE=false
COVERAGE=true
DOCKER_MODE=false

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}================================${NC}"
}

# Function to show usage
show_usage() {
    cat << EOF
TripCraft AI Backend - Test Execution Script

Usage: $0 [OPTIONS]

OPTIONS:
    -t, --type TYPE         Test type: all, unit, integration, api, performance, security, smoke
    -u, --url URL          API base URL (default: http://localhost:8000)
    -p, --parallel         Run tests in parallel
    -v, --verbose          Verbose output
    -c, --no-coverage      Disable coverage reporting
    -r, --no-reports       Skip generating HTML/JSON reports
    -d, --docker           Run tests in Docker environment
    -h, --help             Show this help message

EXAMPLES:
    $0                                    # Run all tests
    $0 -t smoke                          # Run smoke tests only
    $0 -t api -u http://staging:8000     # Run API tests against staging
    $0 -p -v                             # Run all tests in parallel with verbose output
    $0 -d                                # Run tests in Docker environment

TEST TYPES:
    all           - All test suites
    unit          - Unit tests only
    integration   - Integration tests only
    api           - API endpoint tests
    performance   - Performance tests
    security      - Security tests
    smoke         - Smoke tests (quick validation)
    health        - Health check tests

EOF
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check if we're in the right directory
    if [[ ! -f "$PROJECT_DIR/main.py" ]]; then
        print_error "Please run this script from the backend directory"
        exit 1
    fi
    
    # Check if virtual environment exists
    if [[ ! -d "$PROJECT_DIR/venv" ]] && [[ -z "$VIRTUAL_ENV" ]]; then
        print_warning "No virtual environment detected. Consider creating one:"
        print_warning "python3 -m venv venv && source venv/bin/activate"
    fi
    
    print_success "Prerequisites check passed"
}

# Function to install test dependencies
install_dependencies() {
    print_status "Installing test dependencies..."
    
    cd "$PROJECT_DIR"
    
    # Install main requirements
    if [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt
    fi
    
    # Install test requirements
    if [[ -f "requirements-test.txt" ]]; then
        pip install -r requirements-test.txt
    else
        print_warning "requirements-test.txt not found, installing basic test dependencies"
        pip install pytest pytest-asyncio httpx rich
    fi
    
    print_success "Dependencies installed"
}

# Function to setup test environment
setup_test_environment() {
    print_status "Setting up test environment..."
    
    cd "$PROJECT_DIR"
    
    # Create necessary directories
    mkdir -p logs reports htmlcov
    
    # Set environment variables
    export ENVIRONMENT=testing
    export LOG_LEVEL=INFO
    export PYTHONPATH="$PROJECT_DIR/src:$PYTHONPATH"
    
    print_success "Test environment setup complete"
}

# Function to start API server if needed
start_api_server() {
    if [[ "$TEST_TYPE" == "api" ]] || [[ "$TEST_TYPE" == "integration" ]] || [[ "$TEST_TYPE" == "all" ]]; then
        print_status "Checking if API server is running..."
        
        if curl -s "$API_URL/health" > /dev/null 2>&1; then
            print_success "API server is already running at $API_URL"
        else
            print_warning "API server not running. Starting server..."
            
            if [[ "$DOCKER_MODE" == true ]]; then
                start_docker_api
            else
                start_local_api
            fi
        fi
    fi
}

# Function to start API in Docker
start_docker_api() {
    print_status "Starting API server in Docker..."
    
    cd "$PROJECT_DIR"
    
    # Build and start with docker-compose
    if [[ -f "docker-compose.yml" ]]; then
        docker-compose up -d tripcraft-api
        
        # Wait for API to be ready
        print_status "Waiting for API to be ready..."
        for i in {1..30}; do
            if curl -s "$API_URL/health" > /dev/null 2>&1; then
                print_success "API server is ready"
                return 0
            fi
            sleep 2
        done
        
        print_error "API server failed to start in Docker"
        exit 1
    else
        print_error "docker-compose.yml not found"
        exit 1
    fi
}

# Function to start API locally
start_local_api() {
    print_status "Starting API server locally..."
    
    cd "$PROJECT_DIR"
    
    # Start API in background
    python3 main.py &
    API_PID=$!
    
    # Wait for API to be ready
    print_status "Waiting for API to be ready..."
    for i in {1..30}; do
        if curl -s "$API_URL/health" > /dev/null 2>&1; then
            print_success "API server is ready (PID: $API_PID)"
            echo $API_PID > .api_pid
            return 0
        fi
        sleep 2
    done
    
    print_error "API server failed to start locally"
    kill $API_PID 2>/dev/null || true
    exit 1
}

# Function to run pytest tests
run_pytest_tests() {
    print_header "Running Pytest Tests"
    
    cd "$PROJECT_DIR"
    
    local pytest_args=""
    
    # Add coverage if enabled
    if [[ "$COVERAGE" == true ]]; then
        pytest_args="$pytest_args --cov=src --cov-report=html --cov-report=xml --cov-report=term"
    fi
    
    # Add verbosity if enabled
    if [[ "$VERBOSE" == true ]]; then
        pytest_args="$pytest_args -v"
    fi
    
    # Add parallel execution if enabled
    if [[ "$PARALLEL" == true ]]; then
        pytest_args="$pytest_args -n auto"
    fi
    
    # Add test type filtering
    case "$TEST_TYPE" in
        "unit")
            pytest_args="$pytest_args -m unit"
            ;;
        "integration")
            pytest_args="$pytest_args -m integration"
            ;;
        "api")
            pytest_args="$pytest_args -m api"
            ;;
        "performance")
            pytest_args="$pytest_args -m performance"
            ;;
        "security")
            pytest_args="$pytest_args -m security"
            ;;
        "smoke")
            pytest_args="$pytest_args -m smoke"
            ;;
        "health")
            pytest_args="$pytest_args -m health"
            ;;
    esac
    
    # Run pytest
    print_status "Executing: pytest $pytest_args tests/"
    
    if pytest $pytest_args tests/; then
        print_success "Pytest tests completed successfully"
        return 0
    else
        print_error "Pytest tests failed"
        return 1
    fi
}

# Function to run integration tests
run_integration_tests() {
    print_header "Running Integration Tests"
    
    cd "$PROJECT_DIR"
    
    local args=""
    
    # Build arguments
    if [[ "$PARALLEL" == true ]]; then
        args="$args --parallel"
    fi
    
    if [[ "$VERBOSE" == true ]]; then
        args="$args --verbose"
    fi
    
    if [[ "$GENERATE_REPORTS" == false ]]; then
        args="$args --no-reports"
    fi
    
    if [[ "$TEST_TYPE" != "all" ]]; then
        args="$args --categories $TEST_TYPE"
    fi
    
    # Run integration tests
    print_status "Executing: python3 run_tests.py --url $API_URL $args"
    
    if python3 run_tests.py --url "$API_URL" $args; then
        print_success "Integration tests completed successfully"
        return 0
    else
        print_error "Integration tests failed"
        return 1
    fi
}

# Function to cleanup
cleanup() {
    print_status "Cleaning up..."
    
    # Stop local API server if we started it
    if [[ -f ".api_pid" ]]; then
        local api_pid=$(cat .api_pid)
        if kill -0 $api_pid 2>/dev/null; then
            print_status "Stopping API server (PID: $api_pid)"
            kill $api_pid
        fi
        rm -f .api_pid
    fi
    
    # Stop Docker containers if in Docker mode
    if [[ "$DOCKER_MODE" == true ]]; then
        print_status "Stopping Docker containers..."
        docker-compose down
    fi
    
    print_success "Cleanup completed"
}

# Function to generate final report
generate_final_report() {
    if [[ "$GENERATE_REPORTS" == true ]]; then
        print_header "Test Reports Generated"
        
        if [[ -f "test_report.html" ]]; then
            print_success "HTML Report: $(pwd)/test_report.html"
        fi
        
        if [[ -f "test_report.json" ]]; then
            print_success "JSON Report: $(pwd)/test_report.json"
        fi
        
        if [[ -f "htmlcov/index.html" ]]; then
            print_success "Coverage Report: $(pwd)/htmlcov/index.html"
        fi
        
        if [[ -f "reports/pytest_report.html" ]]; then
            print_success "Pytest Report: $(pwd)/reports/pytest_report.html"
        fi
    fi
}

# Main execution function
main() {
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -t|--type)
                TEST_TYPE="$2"
                shift 2
                ;;
            -u|--url)
                API_URL="$2"
                shift 2
                ;;
            -p|--parallel)
                PARALLEL=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -c|--no-coverage)
                COVERAGE=false
                shift
                ;;
            -r|--no-reports)
                GENERATE_REPORTS=false
                shift
                ;;
            -d|--docker)
                DOCKER_MODE=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Trap cleanup on exit
    trap cleanup EXIT
    
    print_header "TripCraft AI Backend - Test Execution"
    print_status "Test Type: $TEST_TYPE"
    print_status "API URL: $API_URL"
    print_status "Parallel: $PARALLEL"
    print_status "Docker Mode: $DOCKER_MODE"
    
    # Execute test pipeline
    check_prerequisites
    install_dependencies
    setup_test_environment
    start_api_server
    
    local exit_code=0
    
    # Run appropriate tests
    case "$TEST_TYPE" in
        "unit")
            run_pytest_tests || exit_code=1
            ;;
        "all"|"integration"|"api"|"performance"|"security"|"smoke"|"health")
            run_pytest_tests || exit_code=1
            run_integration_tests || exit_code=1
            ;;
        *)
            print_error "Unknown test type: $TEST_TYPE"
            exit_code=1
            ;;
    esac
    
    generate_final_report
    
    if [[ $exit_code -eq 0 ]]; then
        print_success "All tests completed successfully! 🎉"
    else
        print_error "Some tests failed! ❌"
    fi
    
    exit $exit_code
}

# Run main function
main "$@"
