# ZOIOS Marketing CRM - Installation Guide

## Overview

ZOIOS is a comprehensive marketing CRM software designed for tracking outreach efforts, managing contacts, companies, call logs, and email responses with powerful data visualization and analytics.

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: MongoDB 
- **Authentication**: JWT tokens with role-based access control
- **Password Hashing**: SHA-256 with salt
- **API Documentation**: Auto-generated with FastAPI/Swagger
- **CORS**: Configurable cross-origin resource sharing

### Frontend
- **Framework**: React 19.x
- **Routing**: React Router DOM 7.x
- **UI Components**: Shadcn/UI (Radix UI primitives)
- **Styling**: Tailwind CSS 3.4+
- **Charts**: Recharts 3.x for data visualization
- **State Management**: React Context API for authentication
- **HTTP Client**: Axios for API calls
- **Forms**: React Hook Form with Zod validation
- **Icons**: Lucide React

### Development Tools
- **Build Tool**: Create React App with CRACO
- **Package Manager**: Yarn (required)
- **Linting**: ESLint 9.x
- **Code Formatting**: Prettier (configured via ESLint)

### Server Requirements
- **Node.js**: 18.x or 20.x
- **Python**: 3.11 or higher
- **MongoDB**: 4.4 or higher
- **Memory**: Minimum 2GB RAM (4GB recommended)
- **Storage**: 10GB free space (minimum)
- **OS**: Ubuntu 20.04+, CentOS 8+, or similar Linux distribution

## Installation Steps

### 1. System Prerequisites

#### Install Node.js and Yarn
```bash
# Install Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Yarn
curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
sudo apt update && sudo apt install yarn
```

#### Install Python and Dependencies
```bash
# Install Python 3.11 and pip
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv python3.11-dev

# Create symbolic links (if needed)
sudo ln -sf /usr/bin/python3.11 /usr/bin/python3
sudo ln -sf /usr/bin/pip3 /usr/bin/pip
```

#### Install MongoDB
```bash
# Import MongoDB public GPG Key
curl -fsSL https://pgp.mongodb.com/server-7.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor

# Add MongoDB repository
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Install MongoDB
sudo apt update
sudo apt install mongodb-org

# Start and enable MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod
```

### 2. Application Setup

#### Clone/Download the Application
```bash
# Create application directory
mkdir -p /opt/zoios-crm
cd /opt/zoios-crm

# Copy your application files here
# The directory structure should be:
# /opt/zoios-crm/
# ├── backend/
# ├── frontend/
# └── INSTALLATION_GUIDE.md
```

#### Backend Setup
```bash
cd /opt/zoios-crm/backend

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Create environment file
cat > .env << EOF
MONGO_URL=mongodb://localhost:27017
DB_NAME=zoios_crm
CORS_ORIGINS=http://localhost:3000,http://your-domain.com
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
EOF

# Make sure MongoDB is running
sudo systemctl status mongod
```

#### Frontend Setup
```bash
cd /opt/zoios-crm/frontend

# Install Node.js dependencies
yarn install

# Create environment file
cat > .env << EOF
REACT_APP_BACKEND_URL=http://localhost:8001
WDS_SOCKET_PORT=443
EOF
```

### 3. Production Configuration

#### Backend Production Settings
```bash
# Update backend/.env for production
cat > backend/.env << EOF
MONGO_URL=mongodb://localhost:27017
DB_NAME=zoios_crm_production
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com
JWT_SECRET_KEY=$(openssl rand -hex 32)
EOF
```

#### Frontend Production Settings
```bash
# Update frontend/.env for production
cat > frontend/.env << EOF
REACT_APP_BACKEND_URL=https://your-api-domain.com
EOF
```

### 4. Process Management with Supervisor

#### Install Supervisor
```bash
sudo apt install supervisor
```

#### Create Supervisor Configuration
```bash
# Backend service configuration
sudo cat > /etc/supervisor/conf.d/zoios-backend.conf << EOF
[program:zoios-backend]
command=/opt/zoios-crm/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001
directory=/opt/zoios-crm/backend
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/zoios-backend.err.log
stdout_logfile=/var/log/supervisor/zoios-backend.out.log
environment=PATH="/opt/zoios-crm/backend/venv/bin"
EOF

# Frontend service configuration (for development)
sudo cat > /etc/supervisor/conf.d/zoios-frontend.conf << EOF
[program:zoios-frontend]
command=yarn start
directory=/opt/zoios-crm/frontend
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/zoios-frontend.err.log
stdout_logfile=/var/log/supervisor/zoios-frontend.out.log
environment=PATH="/usr/bin:/usr/local/bin"
EOF

# Update supervisor and start services
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all
```

### 5. Web Server Configuration (Nginx)

#### Install Nginx
```bash
sudo apt install nginx
```

#### Configure Nginx for Production
```bash
sudo cat > /etc/nginx/sites-available/zoios-crm << 'EOF'
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL configuration (add your SSL certificates)
    ssl_certificate /path/to/your/certificate.pem;
    ssl_certificate_key /path/to/your/private-key.pem;
    
    # Frontend (React build)
    location / {
        root /opt/zoios-crm/frontend/build;
        index index.html;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
        add_header Access-Control-Allow-Headers "Authorization, Content-Type";
        
        # Handle preflight requests
        if ($request_method = 'OPTIONS') {
            return 204;
        }
    }
}
EOF

# Enable site and restart Nginx
sudo ln -s /etc/nginx/sites-available/zoios-crm /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. Production Build (Frontend)

```bash
cd /opt/zoios-crm/frontend

# Build for production
yarn build

# Update Nginx configuration to serve build files
# The build files will be in /opt/zoios-crm/frontend/build/
```

### 7. SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Verify auto-renewal
sudo certbot renew --dry-run
```

### 8. Firewall Configuration

```bash
# Configure UFW firewall
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable
```

### 9. Database Backup Setup

```bash
# Create backup script
sudo cat > /opt/zoios-crm/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/zoios-crm/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup MongoDB
mongodump --db zoios_crm_production --out $BACKUP_DIR/mongo_$DATE

# Keep only last 7 days of backups
find $BACKUP_DIR -type d -name "mongo_*" -mtime +7 -exec rm -rf {} \;
EOF

sudo chmod +x /opt/zoios-crm/backup.sh

# Add to crontab for daily backups
echo "0 2 * * * /opt/zoios-crm/backup.sh" | sudo crontab -
```

### 10. Monitoring and Logs

```bash
# View application logs
sudo tail -f /var/log/supervisor/zoios-backend.out.log
sudo tail -f /var/log/supervisor/zoios-backend.err.log

# Check service status
sudo supervisorctl status
sudo systemctl status nginx
sudo systemctl status mongod

# Monitor system resources
htop
df -h
free -m
```

## Environment Variables Reference

### Backend (.env)
```bash
MONGO_URL=mongodb://localhost:27017
DB_NAME=zoios_crm_production
CORS_ORIGINS=https://your-domain.com
JWT_SECRET_KEY=your-super-secret-key-32-characters-minimum
```

### Frontend (.env)
```bash
REACT_APP_BACKEND_URL=https://your-api-domain.com
```

## Default Admin Account

The system automatically creates a default admin account:
- **Email**: admin@zoios.com
- **Password**: admin123

⚠️ **Security Note**: Change this password immediately after first login in production!

## API Documentation

Once the backend is running, API documentation is available at:
- **Swagger UI**: `http://your-domain.com/docs`
- **ReDoc**: `http://your-domain.com/redoc`

## Troubleshooting

### Common Issues

1. **MongoDB Connection Issues**
   ```bash
   # Check MongoDB status
   sudo systemctl status mongod
   # Restart MongoDB
   sudo systemctl restart mongod
   ```

2. **Backend Won't Start**
   ```bash
   # Check Python dependencies
   cd /opt/zoios-crm/backend
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Frontend Build Errors**
   ```bash
   # Clear node_modules and reinstall
   cd /opt/zoios-crm/frontend
   rm -rf node_modules
   yarn install
   ```

4. **CORS Issues**
   - Update `CORS_ORIGINS` in backend/.env
   - Restart backend service

5. **Authentication Issues**
   - Check JWT_SECRET_KEY in backend/.env
   - Clear browser localStorage and cookies

### Performance Optimization

1. **Database Indexing**
   ```javascript
   // Connect to MongoDB and create indexes
   use zoios_crm_production
   db.contacts.createIndex({ "user_id": 1 })
   db.contacts.createIndex({ "email": 1 })
   db.call_logs.createIndex({ "user_id": 1, "date": -1 })
   db.email_responses.createIndex({ "user_id": 1, "date": -1 })
   ```

2. **Nginx Optimization**
   - Enable gzip compression
   - Configure proper caching headers
   - Use HTTP/2

3. **MongoDB Optimization**
   - Regular database maintenance
   - Monitor query performance
   - Set up replica sets for high availability

## Security Checklist

- [ ] Change default admin password
- [ ] Use strong JWT secret key (32+ characters)
- [ ] Configure SSL/TLS certificates
- [ ] Set up firewall rules
- [ ] Regular database backups
- [ ] Monitor application logs
- [ ] Keep system packages updated
- [ ] Use environment variables for sensitive data
- [ ] Configure CORS properly
- [ ] Set up monitoring and alerting

## Support

For issues and questions:
1. Check application logs first
2. Verify all services are running
3. Test database connectivity
4. Check firewall and network settings

## Version Information

- **Application Version**: 1.0.0
- **Node.js**: 18.x/20.x
- **Python**: 3.11+
- **MongoDB**: 4.4+
- **React**: 19.x
- **FastAPI**: Latest stable