#!/bin/bash

# Linux Daily Tips - Development Environment Shutdown Script
# This script gracefully stops the development environment

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="Linux Daily Tips"
COMPOSE_FILES="-f docker-compose.yml -f docker-compose.dev.yml"

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

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Cannot stop services."
        exit 1
    fi
}

# Function to gracefully stop services
stop_services() {
    print_status "Stopping $PROJECT_NAME development services..."

    # Check if any services are running
    if ! docker-compose $COMPOSE_FILES ps --services --filter "status=running" | head -1 >/dev/null 2>&1; then
        print_warning "No running services found"
        return 0
    fi

    # Stop services with timeout
    docker-compose $COMPOSE_FILES down --timeout 30

    print_success "All services stopped successfully"
}

# Function to clean up resources (optional)
cleanup_resources() {
    local clean_volumes=false
    local clean_networks=false
    local clean_images=false

    # Parse command line arguments
    for arg in "$@"; do
        case $arg in
            --clean-volumes)
                clean_volumes=true
                shift
                ;;
            --clean-networks)
                clean_networks=true
                shift
                ;;
            --clean-images)
                clean_images=true
                shift
                ;;
            --clean-all)
                clean_volumes=true
                clean_networks=true
                clean_images=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
        esac
    done

    # Clean volumes if requested
    if [ "$clean_volumes" = true ]; then
        print_warning "Removing volumes (this will delete all data)..."
        read -p "Are you sure you want to delete all database data? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose $COMPOSE_FILES down --volumes
            print_success "Volumes removed"
        else
            print_status "Volume cleanup cancelled"
        fi
    fi

    # Clean networks if requested
    if [ "$clean_networks" = true ]; then
        print_status "Removing custom networks..."
        docker network rm linux_tips_network 2>/dev/null || print_warning "Network not found or already removed"
    fi

    # Clean images if requested
    if [ "$clean_images" = true ]; then
        print_status "Removing project images..."
        docker-compose $COMPOSE_FILES down --rmi local
        print_success "Local images removed"
    fi
}

# Function to show terminal sessions and cleanup
cleanup_terminals() {
    print_status "Checking for active terminal sessions..."

    # Find any running terminal containers
    local terminal_containers=$(docker ps --filter "name=linux_tips_terminal" --format "{{.Names}}" 2>/dev/null || true)

    if [ -n "$terminal_containers" ]; then
        print_warning "Found active terminal sessions:"
        echo "$terminal_containers"
        print_status "Stopping terminal containers..."

        echo "$terminal_containers" | while read -r container; do
            if [ -n "$container" ]; then
                docker stop "$container" >/dev/null 2>&1 || true
                docker rm "$container" >/dev/null 2>&1 || true
                print_status "Stopped and removed: $container"
            fi
        done
        print_success "Terminal sessions cleaned up"
    else
        print_status "No active terminal sessions found"
    fi
}

# Function to show service status
show_status() {
    print_status "Checking service status..."
    echo ""

    # Check if any containers are still running
    local running_containers=$(docker ps --filter "label=com.docker.compose.project=linux-daily-tips" --format "{{.Names}}" 2>/dev/null || true)

    if [ -n "$running_containers" ]; then
        print_warning "The following containers are still running:"
        echo "$running_containers"
        echo ""
        print_status "Use 'docker stop <container_name>' to stop them manually"
    else
        print_success "All project containers are stopped"
    fi

    # Show volume status
    local volumes=$(docker volume ls --filter "name=linux_tips" --format "{{.Name}}" 2>/dev/null || true)
    if [ -n "$volumes" ]; then
        echo ""
        print_status "Persistent volumes (data preserved):"
        echo "$volumes"
        echo ""
        print_status "Use '$0 --clean-volumes' to remove volumes and delete all data"
    fi
}

# Function to show help
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --clean-volumes    Remove all volumes (deletes database data)"
    echo "  --clean-networks   Remove custom networks"
    echo "  --clean-images     Remove locally built images"
    echo "  --clean-all        Remove volumes, networks, and images"
    echo "  --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                        # Stop services, keep data"
    echo "  $0 --clean-volumes        # Stop services and delete all data"
    echo "  $0 --clean-all            # Complete cleanup"
}

# Function to save logs before shutdown (optional)
save_logs() {
    if [[ "$1" == "--save-logs" ]]; then
        print_status "Saving container logs before shutdown..."
        local log_dir="logs/$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$log_dir"

        # Save logs for each service
        for service in postgres redis backend pgadmin redis-commander mailhog; do
            if docker-compose $COMPOSE_FILES ps "$service" >/dev/null 2>&1; then
                docker-compose $COMPOSE_FILES logs "$service" > "$log_dir/${service}.log" 2>&1
                print_status "Saved logs for $service"
            fi
        done

        print_success "Logs saved to $log_dir"
    fi
}

# Main execution
main() {
    echo "🛑 Stopping $PROJECT_NAME Development Environment"
    echo "================================================="

    # Check prerequisites
    check_docker

    # Save logs if requested
    save_logs "$@"

    # Stop services
    stop_services

    # Cleanup terminal sessions
    cleanup_terminals

    # Cleanup resources based on arguments
    cleanup_resources "$@"

    # Show final status
    show_status

    echo ""
    print_success "🛑 $PROJECT_NAME development environment stopped"
    print_status "Use './scripts/dev-up.sh' to start the environment again"
    echo ""
}

# Handle interruption
trap 'print_error "Script interrupted by user"; exit 1' INT

# Show help if requested
if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    show_help
    exit 0
fi

# Run main function
main "$@"