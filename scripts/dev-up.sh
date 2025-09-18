#!/bin/bash

# Linux Daily Tips - Development Environment Startup Script
# This script starts the complete development environment with proper error handling

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
SERVICES=("postgres" "redis" "pgadmin" "redis-commander" "mailhog")
BACKEND_SERVICE="backend"

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
    print_status "Checking Docker availability..."
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Function to check if docker-compose is available
check_docker_compose() {
    print_status "Checking Docker Compose availability..."
    if ! command -v docker-compose >/dev/null 2>&1; then
        print_error "docker-compose is not installed. Please install docker-compose and try again."
        exit 1
    fi
    print_success "Docker Compose is available"
}

# Function to create .env file if it doesn't exist
create_env_file() {
    if [ ! -f .env ]; then
        print_status "Creating .env file with default development settings..."
        cat > .env << EOF
# Linux Daily Tips Development Environment Variables
# Generated automatically by dev-up.sh

# Database Configuration
POSTGRES_DB=linux_daily_tips
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres_dev_password

# Redis Configuration
REDIS_PASSWORD=redis_dev_password

# FastAPI Configuration
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# LLM API Keys (add your keys here)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Terminal Configuration
TERMINAL_TIMEOUT=30
TERMINAL_MAX_MEMORY=512m
TERMINAL_MAX_CPU=0.5

# Development Tools
PGADMIN_DEFAULT_EMAIL=admin@linuxtips.dev
PGADMIN_DEFAULT_PASSWORD=pgadmin_dev_password
EOF
        print_success ".env file created with default values"
        print_warning "Please add your LLM API keys to .env file for full functionality"
    fi
}

# Function to pull latest images
pull_images() {
    print_status "Pulling latest Docker images..."
    docker-compose $COMPOSE_FILES pull --quiet
    print_success "Docker images updated"
}

# Function to build custom images
build_images() {
    print_status "Building custom Docker images..."
    if [ -f "backend/Dockerfile.dev" ]; then
        docker-compose $COMPOSE_FILES build $BACKEND_SERVICE
        print_success "Backend image built successfully"
    else
        print_warning "Backend Dockerfile.dev not found, skipping backend build"
    fi
}

# Function to start core services (postgres, redis)
start_core_services() {
    print_status "Starting core services (PostgreSQL, Redis)..."
    docker-compose $COMPOSE_FILES up -d postgres redis

    # Wait for services to be healthy
    print_status "Waiting for core services to be ready..."
    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if docker-compose $COMPOSE_FILES ps postgres | grep -q "healthy" && \
           docker-compose $COMPOSE_FILES ps redis | grep -q "Up"; then
            print_success "Core services are ready"
            return 0
        fi

        print_status "Waiting for services... (attempt $attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done

    print_error "Core services failed to start within expected time"
    print_status "Checking service logs..."
    docker-compose $COMPOSE_FILES logs postgres redis
    exit 1
}

# Function to start development tools
start_dev_tools() {
    print_status "Starting development tools (pgAdmin, Redis Commander, Mailhog)..."
    docker-compose $COMPOSE_FILES up -d pgadmin redis-commander mailhog
    print_success "Development tools started"
}

# Function to start backend service
start_backend() {
    if [ -f "backend/Dockerfile.dev" ] && [ -f "backend/main.py" ]; then
        print_status "Starting FastAPI backend..."
        docker-compose $COMPOSE_FILES up -d $BACKEND_SERVICE
        print_success "Backend service started"
    else
        print_warning "Backend service files not found, skipping backend startup"
        print_warning "Run this script again after setting up the FastAPI backend"
    fi
}

# Function to display service URLs
show_service_urls() {
    echo ""
    print_success "🚀 $PROJECT_NAME development environment is ready!"
    echo ""
    echo "📊 Development Services:"
    echo "   🗄️  PostgreSQL:      localhost:5432"
    echo "   🚀 Redis:            localhost:6379"
    echo ""
    echo "🛠️  Development Tools:"
    echo "   📱 pgAdmin:          http://localhost:5050"
    echo "      └── Email: admin@linuxtips.dev"
    echo "      └── Password: pgadmin_dev_password"
    echo ""
    echo "   🗂️  Redis Commander:  http://localhost:8081"
    echo "      └── User: admin"
    echo "      └── Password: redis_commander_password"
    echo ""
    echo "   📧 Mailhog:          http://localhost:8025"
    echo "      └── SMTP: localhost:1025"
    echo ""

    if docker-compose $COMPOSE_FILES ps $BACKEND_SERVICE >/dev/null 2>&1; then
        echo "🎯 Application Services:"
        echo "   🔧 FastAPI Backend:  http://localhost:8000"
        echo "      └── API Docs: http://localhost:8000/docs"
        echo "      └── ReDoc: http://localhost:8000/redoc"
        echo ""
    fi

    echo "🔧 Useful Commands:"
    echo "   📋 View logs:        docker-compose $COMPOSE_FILES logs -f"
    echo "   🛑 Stop services:    ./scripts/dev-down.sh"
    echo "   🔄 Restart:          ./scripts/dev-down.sh && ./scripts/dev-up.sh"
    echo "   📊 Check status:     docker-compose $COMPOSE_FILES ps"
}

# Function to run database health check
check_database() {
    print_status "Running database health check..."
    if docker-compose $COMPOSE_FILES exec -T postgres psql -U postgres -d linux_daily_tips -c "SELECT 1;" >/dev/null 2>&1; then
        print_success "Database connection successful"

        # Check if schema is initialized
        if docker-compose $COMPOSE_FILES exec -T postgres psql -U postgres -d linux_daily_tips -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'linux_tips';" | grep -q "7"; then
            print_success "Database schema is properly initialized"
        else
            print_warning "Database schema may not be fully initialized"
        fi
    else
        print_error "Database connection failed"
        return 1
    fi
}

# Main execution
main() {
    echo "🚀 Starting $PROJECT_NAME Development Environment"
    echo "=================================================="

    # Pre-flight checks
    check_docker
    check_docker_compose

    # Setup
    create_env_file
    pull_images
    build_images

    # Start services in order
    start_core_services
    start_dev_tools
    start_backend

    # Post-startup checks
    sleep 5
    check_database

    # Show status
    show_service_urls

    print_success "Development environment startup completed!"
    print_status "Use 'docker-compose $COMPOSE_FILES logs -f' to view real-time logs"
}

# Handle interruption
trap 'print_error "Script interrupted by user"; exit 1' INT

# Run main function
main "$@"