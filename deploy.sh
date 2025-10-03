#!/bin/bash

# ZOIOS CRM Deployment Script
# This script automates the installation process for ZOIOS Marketing CRM

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/opt/zoios-crm"
APP_USER="www-data"
BACKEND_PORT="8001"
FRONTEND_PORT="3000"

# Functions
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

install_dependencies() {
    print_status "Installing system dependencies..."
    
    # Update system
    apt update
    
    # Install Node.js 20.x
    if ! command -v node &> /dev/null; then
        print_status "Installing Node.js 20.x..."
        curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
        apt-get install -y nodejs
    fi
    
    # Install Yarn
    if ! command -v yarn &> /dev/null; then
        print_status "Installing Yarn..."
        curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -
        echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list
        apt update && apt install yarn
    fi
    
    # Install Python 3.11
    if ! command -v python3.11 &> /dev/null; then
        print_status "Installing Python 3.11..."
        apt install -y python3.11 python3.11-pip python3.11-venv python3.11-dev
    fi
    
    # Install MongoDB
    if ! command -v mongod &> /dev/null; then
        print_status "Installing MongoDB..."
        curl -fsSL https://pgp.mongodb.com/server-7.0.asc | gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor
        echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-7.0.list
        apt update
        apt install -y mongodb-org
        systemctl start mongod
        systemctl enable mongod
    fi
    
    # Install Supervisor
    if ! command -v supervisorctl &> /dev/null; then
        print_status "Installing Supervisor..."
        apt install -y supervisor
    fi
    
    # Install Nginx
    if ! command -v nginx &> /dev/null; then
        print_status "Installing Nginx..."
        apt install -y nginx
    fi
    
    print_status "System dependencies installed successfully"
}

setup_application() {
    print_status "Setting up ZOIOS CRM application..."
    
    # Create application directory
    mkdir -p $APP_DIR
    cd $APP_DIR
    
    # Copy application files (assuming they're in current directory)
    if [ -d "./backend" ] && [ -d "./frontend" ]; then
        print_status "Application files found, copying..."
        cp -r ./backend $APP_DIR/
        cp -r ./frontend $APP_DIR/
    else
        print_error "Backend and frontend directories not found in current directory"
        print_warning "Please ensure you're running this script from the ZOIOS application directory"
        exit 1
    fi
    
    # Set permissions
    chown -R $APP_USER:$APP_USER $APP_DIR
    
    print_status "Application files copied successfully"
}

setup_backend() {
    print_status "Setting up backend..."
    
    cd $APP_DIR/backend
    
    # Create Python virtual environment
    sudo -u $APP_USER python3.11 -m venv venv
    
    # Install Python dependencies
    sudo -u $APP_USER bash -c "source venv/bin/activate && pip install -r requirements.txt"
    
    # Generate JWT secret key
    JWT_SECRET=$(openssl rand -hex 32)
    
    # Create environment file
    cat > .env << EOF
MONGO_URL=mongodb://localhost:27017
DB_NAME=zoios_crm
CORS_ORIGINS=*
JWT_SECRET_KEY=$JWT_SECRET
EOF
    
    chown $APP_USER:$APP_USER .env
    
    print_status "Backend setup completed"
}

setup_frontend() {
    print_status "Setting up frontend..."
    
    cd $APP_DIR/frontend
    
    # Install Node.js dependencies
    sudo -u $APP_USER yarn install
    
    # Create environment file
    cat > .env << EOF
REACT_APP_BACKEND_URL=http://localhost:$BACKEND_PORT
EOF
    
    chown $APP_USER:$APP_USER .env
    
    print_status "Frontend setup completed"
}

setup_services() {
    print_status "Setting up system services..."
    
    # Backend supervisor configuration
    cat > /etc/supervisor/conf.d/zoios-backend.conf << EOF
[program:zoios-backend]
command=$APP_DIR/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port $BACKEND_PORT
directory=$APP_DIR/backend
user=$APP_USER
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/zoios-backend.err.log
stdout_logfile=/var/log/supervisor/zoios-backend.out.log
environment=PATH="$APP_DIR/backend/venv/bin"
EOF
    
    # Frontend supervisor configuration (for development)
    cat > /etc/supervisor/conf.d/zoios-frontend.conf << EOF
[program:zoios-frontend]
command=yarn start
directory=$APP_DIR/frontend
user=$APP_USER
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/zoios-frontend.err.log
stdout_logfile=/var/log/supervisor/zoios-frontend.out.log
environment=PATH="/usr/bin:/usr/local/bin",PORT="$FRONTEND_PORT"
EOF
    
    # Reload supervisor
    supervisorctl reread
    supervisorctl update
    
    print_status "Services configured"
}

setup_nginx() {
    print_status "Setting up Nginx..."
    
    # Create Nginx configuration
    cat > /etc/nginx/sites-available/zoios-crm << EOF
server {
    listen 80;
    server_name _;
    
    # Frontend
    location / {
        proxy_pass http://127.0.0.1:$FRONTEND_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support for development
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_cache_bypass \$http_upgrade;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:$BACKEND_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF
    
    # Enable site
    ln -sf /etc/nginx/sites-available/zoios-crm /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # Test and reload Nginx
    nginx -t
    systemctl reload nginx
    
    print_status "Nginx configured"
}

setup_firewall() {
    print_status "Setting up firewall..."
    
    # Configure UFW firewall
    ufw --force reset
    ufw allow ssh
    ufw allow 80
    ufw allow 443
    ufw --force enable
    
    print_status "Firewall configured"
}

start_services() {
    print_status "Starting services..."
    
    # Start all services
    systemctl start mongod
    supervisorctl start all
    systemctl start nginx
    
    # Check service status
    sleep 5
    
    print_status "Service Status:"
    echo "MongoDB: $(systemctl is-active mongod)"
    echo "Backend: $(supervisorctl status zoios-backend | awk '{print $2}')"
    echo "Frontend: $(supervisorctl status zoios-frontend | awk '{print $2}')"
    echo "Nginx: $(systemctl is-active nginx)"
}

print_completion() {
    print_status "ZOIOS CRM installation completed!"
    echo ""
    echo "===================================================="
    echo "🎉 ZOIOS Marketing CRM is now installed and running!"
    echo "===================================================="
    echo ""
    echo "📍 Application URL: http://$(hostname -I | awk '{print $1}')"
    echo "📍 Local URL: http://localhost"
    echo ""
    echo "🔐 Default Admin Login:"
    echo "   Email: admin@zoios.com"
    echo "   Password: admin123"
    echo ""
    echo "⚠️  IMPORTANT: Change the default password after first login!"
    echo ""
    echo "📊 Service Management:"
    echo "   Backend logs: sudo tail -f /var/log/supervisor/zoios-backend.out.log"
    echo "   Frontend logs: sudo tail -f /var/log/supervisor/zoios-frontend.out.log"
    echo "   Service status: sudo supervisorctl status"
    echo ""
    echo "📚 Documentation: $APP_DIR/INSTALLATION_GUIDE.md"
    echo "===================================================="
}

# Main execution
main() {
    print_status "Starting ZOIOS CRM installation..."
    
    check_root
    install_dependencies
    setup_application
    setup_backend
    setup_frontend
    setup_services
    setup_nginx
    setup_firewall
    start_services
    print_completion
}

# Run main function
main "$@"