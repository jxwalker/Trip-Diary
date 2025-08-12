#!/bin/bash

# Server Manager for Trip Diary Application
# Version: 3.0 - Simplified and more reliable

# Configuration
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
PROJECT_NAME="trip-diary"
PID_DIR="$PROJECT_ROOT/pids"
LOG_DIR="$PROJECT_ROOT/logs"
FRONTEND_DIR="$PROJECT_ROOT/travel-pack"
BACKEND_DIR="$PROJECT_ROOT/travel-pack/backend"

# PID and log files
FRONTEND_PID_FILE="$PID_DIR/frontend.pid"
BACKEND_PID_FILE="$PID_DIR/backend.pid"
FRONTEND_LOG="$LOG_DIR/frontend.log"
BACKEND_LOG="$LOG_DIR/backend.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'
BOLD='\033[1m'

# Icons
CHECK="✓"
CROSS="✗"
ARROW="→"
DOT="•"

# Create necessary directories
mkdir -p "$PID_DIR" "$LOG_DIR"

# Simple header function
print_header() {
    echo
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${WHITE}${BOLD}  $1${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo
}

# Health check for frontend
check_frontend_health() {
    # Try each port and see if it responds
    for port in 3000 3001 3002 3003; do
        if timeout 2 curl -s -o /dev/null "http://localhost:$port/" 2>/dev/null; then
            echo $port
            return 0
        fi
    done
    return 1
}

# Health check for backend
check_backend_health() {
    if timeout 2 curl -s -o /dev/null "http://localhost:8000/" 2>/dev/null; then
        return 0
    fi
    return 1
}

# Kill all processes matching a pattern
kill_processes() {
    local pattern=$1
    local name=$2
    
    # Find all PIDs matching the pattern
    local pids=$(ps aux | grep "$pattern" | grep -v grep | awk '{print $2}')
    
    if [ ! -z "$pids" ]; then
        echo -e "  ${YELLOW}${DOT}${NC} Stopping $name processes: ${CYAN}$pids${NC}"
        for pid in $pids; do
            kill $pid 2>/dev/null
        done
        sleep 2
        
        # Force kill if still running
        local remaining=$(ps aux | grep "$pattern" | grep -v grep | awk '{print $2}')
        if [ ! -z "$remaining" ]; then
            echo -e "  ${YELLOW}${DOT}${NC} Force killing remaining processes..."
            for pid in $remaining; do
                kill -9 $pid 2>/dev/null
            done
        fi
        echo -e "  ${GREEN}${CHECK}${NC} $name stopped"
    else
        echo -e "  ${GREEN}${CHECK}${NC} No $name processes found"
    fi
}

# Start frontend
start_frontend() {
    print_header "Starting Frontend Server"
    
    # Kill any existing frontend processes
    kill_processes "next.*travel-pack\|node.*travel-pack.*next" "Frontend"
    
    # Clear old PID file
    rm -f "$FRONTEND_PID_FILE"
    
    echo -e "${BOLD}Starting new frontend server...${NC}"
    cd "$FRONTEND_DIR"
    
    # Start the server
    npm run dev > "$FRONTEND_LOG" 2>&1 &
    local pid=$!
    echo $pid > "$FRONTEND_PID_FILE"
    
    cd "$PROJECT_ROOT"
    
    # Wait for server to be healthy
    echo -e "  ${YELLOW}${DOT}${NC} Waiting for server to start..."
    local attempts=0
    local max_attempts=30
    
    while [ $attempts -lt $max_attempts ]; do
        local port=$(check_frontend_health)
        if [ $? -eq 0 ]; then
            echo
            echo -e "  ${GREEN}${CHECK}${NC} Frontend started successfully"
            echo -e "  ${BLUE}${DOT}${NC} PID: ${CYAN}$pid${NC}"
            echo -e "  ${BLUE}${DOT}${NC} Port: ${CYAN}$port${NC}"
            echo -e "  ${BLUE}${DOT}${NC} URL: ${CYAN}http://localhost:$port${NC}"
            return 0
        fi
        sleep 1
        attempts=$((attempts + 1))
        echo -n "."
    done
    
    echo
    echo -e "  ${RED}${CROSS}${NC} Frontend failed to start"
    echo -e "  ${YELLOW}${DOT}${NC} Check logs: ${CYAN}tail -f $FRONTEND_LOG${NC}"
    return 1
}

# Start backend
start_backend() {
    print_header "Starting Backend Server"
    
    # Kill any existing backend processes
    kill_processes "python.*main.py.*travel-pack/backend" "Backend"
    
    # Clear old PID file
    rm -f "$BACKEND_PID_FILE"
    
    echo -e "${BOLD}Starting new backend server...${NC}"
    cd "$BACKEND_DIR"
    
    # Check/create virtual environment
    if [ ! -d "venv" ]; then
        echo -e "  ${YELLOW}${DOT}${NC} Creating virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        echo -e "  ${YELLOW}${DOT}${NC} Installing dependencies..."
        pip install -q fastapi uvicorn aiofiles pypdf python-dotenv openai anthropic pymupdf
        deactivate
    fi
    
    # Start the server
    (source venv/bin/activate && python main.py > "$BACKEND_LOG" 2>&1) &
    local pid=$!
    echo $pid > "$BACKEND_PID_FILE"
    
    cd "$PROJECT_ROOT"
    
    # Wait for server to be healthy
    echo -e "  ${YELLOW}${DOT}${NC} Waiting for server to start..."
    local attempts=0
    local max_attempts=20
    
    while [ $attempts -lt $max_attempts ]; do
        if check_backend_health; then
            echo
            echo -e "  ${GREEN}${CHECK}${NC} Backend started successfully"
            echo -e "  ${BLUE}${DOT}${NC} PID: ${CYAN}$pid${NC}"
            echo -e "  ${BLUE}${DOT}${NC} Port: ${CYAN}8000${NC}"
            echo -e "  ${BLUE}${DOT}${NC} API: ${CYAN}http://localhost:8000${NC}"
            echo -e "  ${BLUE}${DOT}${NC} Docs: ${CYAN}http://localhost:8000/docs${NC}"
            return 0
        fi
        sleep 1
        attempts=$((attempts + 1))
        echo -n "."
    done
    
    echo
    echo -e "  ${RED}${CROSS}${NC} Backend failed to start"
    echo -e "  ${YELLOW}${DOT}${NC} Check logs: ${CYAN}tail -f $BACKEND_LOG${NC}"
    return 1
}

# Stop all servers
stop_all() {
    print_header "Stopping All Servers"
    
    echo -e "${BOLD}Stopping Frontend...${NC}"
    kill_processes "next.*travel-pack\|node.*travel-pack.*next" "Frontend"
    rm -f "$FRONTEND_PID_FILE"
    
    echo
    echo -e "${BOLD}Stopping Backend...${NC}"
    kill_processes "python.*main.py.*travel-pack/backend" "Backend"
    rm -f "$BACKEND_PID_FILE"
    
    echo
    echo -e "${GREEN}${CHECK} All servers stopped${NC}"
}

# Show status with health checks
show_status() {
    print_header "Server Status"
    
    # Frontend status
    echo -e "${BOLD}Frontend Server${NC}"
    echo -e "${CYAN}───────────────${NC}"
    
    local frontend_port=$(check_frontend_health)
    if [ $? -eq 0 ]; then
        local frontend_pid=""
        if [ -f "$FRONTEND_PID_FILE" ]; then
            frontend_pid=$(cat "$FRONTEND_PID_FILE")
        fi
        
        # Find actual PID if not in file
        if [ -z "$frontend_pid" ] || ! ps -p $frontend_pid > /dev/null 2>&1; then
            frontend_pid=$(ps aux | grep "node.*next.*travel-pack" | grep -v grep | head -1 | awk '{print $2}')
        fi
        
        echo -e "  Status:  ${GREEN}● RUNNING${NC}"
        echo -e "  Port:    ${CYAN}$frontend_port${NC}"
        echo -e "  PID:     ${CYAN}${frontend_pid:-unknown}${NC}"
        echo -e "  URL:     ${CYAN}http://localhost:$frontend_port${NC}"
        echo -e "  Health:  ${GREEN}✓ Responding${NC}"
    else
        # Check if process exists but not healthy
        local orphan_pids=$(ps aux | grep "next.*travel-pack\|node.*travel-pack.*next" | grep -v grep | awk '{print $2}')
        if [ ! -z "$orphan_pids" ]; then
            echo -e "  Status:  ${YELLOW}● UNHEALTHY${NC}"
            echo -e "  PIDs:    ${CYAN}$orphan_pids${NC}"
            echo -e "  Health:  ${RED}✗ Not responding${NC}"
            echo -e "  Action:  ${YELLOW}Run: ./server-manager.sh restart${NC}"
        else
            echo -e "  Status:  ${RED}● STOPPED${NC}"
        fi
    fi
    
    echo
    
    # Backend status
    echo -e "${BOLD}Backend Server${NC}"
    echo -e "${CYAN}──────────────${NC}"
    
    if check_backend_health; then
        local backend_pid=""
        if [ -f "$BACKEND_PID_FILE" ]; then
            backend_pid=$(cat "$BACKEND_PID_FILE")
        fi
        
        # Find actual PID if not in file
        if [ -z "$backend_pid" ] || ! ps -p $backend_pid > /dev/null 2>&1; then
            backend_pid=$(ps aux | grep "python.*main.py" | grep -v grep | head -1 | awk '{print $2}')
        fi
        
        echo -e "  Status:  ${GREEN}● RUNNING${NC}"
        echo -e "  Port:    ${CYAN}8000${NC}"
        echo -e "  PID:     ${CYAN}${backend_pid:-unknown}${NC}"
        echo -e "  API:     ${CYAN}http://localhost:8000${NC}"
        echo -e "  Docs:    ${CYAN}http://localhost:8000/docs${NC}"
        echo -e "  Health:  ${GREEN}✓ Responding${NC}"
    else
        # Check if process exists but not healthy
        local orphan_pids=$(ps aux | grep "python.*main.py.*travel-pack/backend" | grep -v grep | awk '{print $2}')
        if [ ! -z "$orphan_pids" ]; then
            echo -e "  Status:  ${YELLOW}● UNHEALTHY${NC}"
            echo -e "  PIDs:    ${CYAN}$orphan_pids${NC}"
            echo -e "  Health:  ${RED}✗ Not responding${NC}"
            echo -e "  Action:  ${YELLOW}Run: ./server-manager.sh restart${NC}"
        else
            echo -e "  Status:  ${RED}● STOPPED${NC}"
        fi
    fi
    
    echo
    
    # Quick summary
    echo -e "${BOLD}Quick Actions${NC}"
    echo -e "${CYAN}─────────────${NC}"
    
    local frontend_healthy=$(check_frontend_health > /dev/null 2>&1 && echo "yes" || echo "no")
    local backend_healthy=$(check_backend_health && echo "yes" || echo "no")
    
    if [ "$frontend_healthy" = "yes" ] && [ "$backend_healthy" = "yes" ]; then
        echo -e "  ${GREEN}${CHECK}${NC} All systems operational"
        echo -e "  ${BLUE}${DOT}${NC} View logs: ${CYAN}./server-manager.sh logs${NC}"
    elif [ "$frontend_healthy" = "no" ] && [ "$backend_healthy" = "no" ]; then
        echo -e "  ${RED}${CROSS}${NC} Both servers are down"
        echo -e "  ${BLUE}${DOT}${NC} Start all: ${CYAN}./server-manager.sh start${NC}"
    else
        echo -e "  ${YELLOW}!${NC} Some services need attention"
        echo -e "  ${BLUE}${DOT}${NC} Restart all: ${CYAN}./server-manager.sh restart${NC}"
    fi
}

# Simple status line after operations
show_quick_status() {
    echo
    echo -e "${CYAN}───────────────────────────────────────────────────────────────${NC}"
    
    local frontend_port=$(check_frontend_health)
    if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}●${NC} Frontend: ${GREEN}Running${NC} on port ${CYAN}$frontend_port${NC}"
    else
        echo -e "  ${RED}●${NC} Frontend: ${RED}Stopped${NC}"
    fi
    
    if check_backend_health; then
        echo -e "  ${GREEN}●${NC} Backend:  ${GREEN}Running${NC} on port ${CYAN}8000${NC}"
    else
        echo -e "  ${RED}●${NC} Backend:  ${RED}Stopped${NC}"
    fi
    
    echo -e "${CYAN}───────────────────────────────────────────────────────────────${NC}"
}

# Health check command
health_check() {
    print_header "Health Check"
    
    echo -e "${BOLD}Running health checks...${NC}"
    echo
    
    # Frontend health
    echo -e "${YELLOW}${DOT}${NC} Checking Frontend..."
    local frontend_port=$(check_frontend_health)
    if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}${CHECK}${NC} Frontend is healthy on port ${CYAN}$frontend_port${NC}"
        
        # Try to fetch a page
        local response=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$frontend_port/" 2>/dev/null)
        echo -e "  ${BLUE}${DOT}${NC} HTTP Status: ${CYAN}$response${NC}"
    else
        echo -e "  ${RED}${CROSS}${NC} Frontend is not responding"
    fi
    
    echo
    
    # Backend health
    echo -e "${YELLOW}${DOT}${NC} Checking Backend..."
    if check_backend_health; then
        echo -e "  ${GREEN}${CHECK}${NC} Backend is healthy on port ${CYAN}8000${NC}"
        
        # Try API endpoint
        local api_response=$(curl -s "http://localhost:8000/" 2>/dev/null | jq -r '.message' 2>/dev/null)
        if [ ! -z "$api_response" ]; then
            echo -e "  ${BLUE}${DOT}${NC} API Response: ${CYAN}$api_response${NC}"
        fi
        
        # Check if docs are accessible
        local docs_status=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000/docs" 2>/dev/null)
        echo -e "  ${BLUE}${DOT}${NC} API Docs Status: ${CYAN}$docs_status${NC}"
    else
        echo -e "  ${RED}${CROSS}${NC} Backend is not responding"
    fi
}

# Tail logs
tail_logs() {
    print_header "Server Logs"
    
    echo -e "${YELLOW}Tailing logs (Ctrl+C to stop)...${NC}"
    echo -e "${BLUE}Frontend:${NC} $FRONTEND_LOG"
    echo -e "${BLUE}Backend:${NC} $BACKEND_LOG"
    echo -e "${CYAN}───────────────────────────────────────────────────────────────${NC}"
    echo
    
    # Use multitail if available, otherwise regular tail
    if command -v multitail > /dev/null 2>&1; then
        multitail -s 2 -l "echo '=== Frontend ===' && tail -f $FRONTEND_LOG" -l "echo '=== Backend ===' && tail -f $BACKEND_LOG"
    else
        tail -f "$FRONTEND_LOG" "$BACKEND_LOG"
    fi
}

# Clean everything
clean_all() {
    print_header "Clean Up"
    
    echo -e "${BOLD}Killing all processes...${NC}"
    kill_processes "next.*travel-pack\|node.*travel-pack.*next" "Frontend"
    kill_processes "python.*main.py.*travel-pack/backend" "Backend"
    
    echo
    echo -e "${BOLD}Removing PID files...${NC}"
    rm -f "$FRONTEND_PID_FILE" "$BACKEND_PID_FILE"
    echo -e "  ${GREEN}${CHECK}${NC} PID files removed"
    
    echo
    echo -e "${BOLD}Clearing logs...${NC}"
    > "$FRONTEND_LOG"
    > "$BACKEND_LOG"
    echo -e "  ${GREEN}${CHECK}${NC} Log files cleared"
    
    echo
    echo -e "${GREEN}${CHECK} Clean up complete${NC}"
}

# Main command handler
case "$1" in
    start)
        start_frontend
        echo
        start_backend
        show_quick_status
        ;;
    stop)
        stop_all
        show_quick_status
        ;;
    restart)
        stop_all
        echo
        sleep 2
        start_frontend
        echo
        start_backend
        show_quick_status
        ;;
    status)
        show_status
        ;;
    health)
        health_check
        ;;
    logs)
        tail_logs
        ;;
    clean)
        clean_all
        ;;
    frontend)
        case "$2" in
            start)
                start_frontend
                show_quick_status
                ;;
            stop)
                print_header "Stopping Frontend"
                kill_processes "next.*travel-pack\|node.*travel-pack.*next" "Frontend"
                rm -f "$FRONTEND_PID_FILE"
                show_quick_status
                ;;
            restart)
                print_header "Restarting Frontend"
                kill_processes "next.*travel-pack\|node.*travel-pack.*next" "Frontend"
                rm -f "$FRONTEND_PID_FILE"
                sleep 2
                start_frontend
                show_quick_status
                ;;
            *)
                echo "Usage: $0 frontend {start|stop|restart}"
                ;;
        esac
        ;;
    backend)
        case "$2" in
            start)
                start_backend
                show_quick_status
                ;;
            stop)
                print_header "Stopping Backend"
                kill_processes "python.*main.py.*travel-pack/backend" "Backend"
                rm -f "$BACKEND_PID_FILE"
                show_quick_status
                ;;
            restart)
                print_header "Restarting Backend"
                kill_processes "python.*main.py.*travel-pack/backend" "Backend"
                rm -f "$BACKEND_PID_FILE"
                sleep 2
                start_backend
                show_quick_status
                ;;
            *)
                echo "Usage: $0 backend {start|stop|restart}"
                ;;
        esac
        ;;
    *)
        print_header "Trip Diary Server Manager v3.0"
        echo -e "${BOLD}Usage:${NC}"
        echo -e "  ${CYAN}$0${NC} {start|stop|restart|status|health|logs|clean}"
        echo -e "  ${CYAN}$0${NC} frontend {start|stop|restart}"
        echo -e "  ${CYAN}$0${NC} backend {start|stop|restart}"
        echo
        echo -e "${BOLD}Commands:${NC}"
        echo -e "  ${GREEN}start${NC}    - Start both servers"
        echo -e "  ${GREEN}stop${NC}     - Stop both servers"
        echo -e "  ${GREEN}restart${NC}  - Restart both servers"
        echo -e "  ${GREEN}status${NC}   - Show detailed status"
        echo -e "  ${GREEN}health${NC}   - Run health checks"
        echo -e "  ${GREEN}logs${NC}     - Tail server logs"
        echo -e "  ${GREEN}clean${NC}    - Kill all and clean up"
        echo
        echo -e "${BOLD}Location:${NC} $PROJECT_ROOT"
        ;;
esac