# ZOIOS Marketing CRM

<div align="center">
<img src="https://customer-assets.emergentagent.com/job_outreach-pulse-3/artifacts/5adajuhk_Zoios.png" alt="ZOIOS Logo" width="100" height="100">

**Advanced Marketing CRM Platform**

*Track your outreach efforts and grow your business*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node.js](https://img.shields.io/badge/Node.js-20.x-green.svg)](https://nodejs.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.0-green.svg)](https://www.mongodb.com/)

</div>

## 🚀 Features

### Core Functionality
- **📊 Interactive Dashboard** with real-time analytics and data visualization
- **👥 Contact Management** with comprehensive contact profiles and relationship tracking
- **🏢 Company Management** for tracking target organizations and opportunities
- **📞 Call Logging** with detailed call outcomes, dispositions, and follow-up scheduling
- **📧 Email Response Tracking** for monitoring outreach campaigns and engagement rates

### Advanced Features
- **🔐 Secure Authentication** with JWT tokens and role-based access control
- **👨‍💼 User Management** (Admin-only) for creating and managing team members
- **📈 Data Visualization** with interactive charts (pie, bar, line charts)
- **🔍 Advanced Search & Filtering** across all data entities
- **🎯 Data Isolation** - Users see only their data, admins see everything
- **📱 Responsive Design** optimized for desktop and mobile devices

### Technical Excellence
- **⚡ High Performance** with optimized database queries and caching
- **🔒 Security First** with password hashing and protected API endpoints  
- **🌐 Modern UI/UX** with professional design and smooth animations
- **📊 Real-time Analytics** with automatic data aggregation and insights
- **🔄 Auto-sync** with real-time updates and seamless data flow

## 🛠️ Technology Stack

### Backend
- **FastAPI** (Python 3.11+) - High-performance async web framework
- **MongoDB** - NoSQL database for flexible data storage
- **JWT Authentication** - Secure token-based authentication
- **Motor** - Async MongoDB driver for Python
- **Uvicorn** - ASGI server for production deployment

### Frontend  
- **React 19.x** - Modern JavaScript UI library
- **Tailwind CSS** - Utility-first CSS framework
- **Shadcn/UI** - High-quality component library
- **Recharts** - Composable charting library for React
- **React Router** - Declarative routing for React apps
- **Axios** - Promise-based HTTP client

### Infrastructure
- **Nginx** - High-performance web server and reverse proxy
- **Supervisor** - Process control system for Unix-like systems
- **Docker** - Containerization platform (optional)
- **SSL/TLS** - Secure HTTPS encryption

## 📋 Prerequisites

### System Requirements
- **Operating System**: Ubuntu 20.04+ / CentOS 8+ / Similar Linux distribution
- **Memory**: Minimum 2GB RAM (4GB recommended for production)
- **Storage**: 10GB free disk space (minimum)
- **Network**: Internet connection for package installation

### Software Dependencies
- **Node.js**: 18.x or 20.x
- **Python**: 3.11 or higher  
- **MongoDB**: 4.4 or higher
- **Nginx**: Latest stable version
- **Supervisor**: For process management

## 🚀 Quick Start

### Option 1: Automated Installation (Recommended)

```bash
# Download the application
git clone <your-repository-url>
cd zoios-crm

# Run the automated installer (requires sudo)
sudo ./deploy.sh
```

The automated installer will:
- Install all system dependencies
- Set up the application with proper configuration
- Configure web server and process management
- Start all services automatically

### Option 2: Docker Installation

```bash
# Clone the repository
git clone <your-repository-url>
cd zoios-crm

# Start with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f
```

### Option 3: Manual Installation

Please refer to the comprehensive [INSTALLATION_GUIDE.md](./INSTALLATION_GUIDE.md) for detailed manual setup instructions.

## 🔐 Default Credentials

**Admin Account:**
- **Email**: `admin@zoios.com`
- **Password**: `admin123`

⚠️ **Important**: Change the default password immediately after first login in production environments!

## 📊 Application URLs

After installation, access the application at:

- **Main Application**: `http://your-server-ip` or `http://localhost`
- **API Documentation**: `http://your-server-ip/docs` (Swagger UI)
- **Alternative API Docs**: `http://your-server-ip/redoc`

## 👥 User Roles & Permissions

### Admin Users
- Full access to all data across the organization
- User management capabilities (create, edit, delete users)
- System configuration and settings access
- Complete dashboard analytics and reporting

### Regular Users  
- Access only to their own data (contacts, calls, emails, companies)
- Full CRUD operations on their assigned data
- Personal dashboard and analytics
- Cannot access user management features

## 📈 Key Metrics & Analytics

The dashboard provides comprehensive analytics including:

- **Contact Pipeline**: Distribution of contacts by status (New, Contacted, Qualified, Opportunity, Customer, Closed)
- **Call Analytics**: Call outcomes, dispositions, and success rates
- **Email Tracking**: Open rates, response rates, and engagement metrics
- **Activity Trends**: Contact acquisition over time with growth analysis
- **Performance KPIs**: Conversion rates and pipeline health indicators

## 🔧 Configuration

### Environment Variables

**Backend Configuration** (`.env` in backend directory):
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=zoios_crm_production
CORS_ORIGINS=https://your-domain.com
JWT_SECRET_KEY=your-secure-secret-key-32-chars-minimum
```

**Frontend Configuration** (`.env` in frontend directory):
```env
REACT_APP_BACKEND_URL=https://your-api-domain.com
```

### Database Configuration

MongoDB collections are automatically created and indexed for optimal performance:
- `users` - User accounts and authentication
- `contacts` - Contact information and relationship data
- `companies` - Company profiles and engagement metrics  
- `call_logs` - Call tracking and outcomes
- `email_responses` - Email campaign tracking

## 🚀 Production Deployment

### SSL/HTTPS Setup
```bash
# Install Certbot for Let's Encrypt
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Verify auto-renewal
sudo certbot renew --dry-run
```

### Performance Optimization
- Enable Nginx gzip compression
- Configure proper caching headers
- Set up database indexing for frequently queried fields
- Monitor resource usage and scale accordingly

### Security Hardening
- Change default passwords immediately
- Use strong JWT secret keys (32+ characters)
- Configure firewall rules (ports 80, 443, 22 only)
- Regular security updates and patches
- Enable MongoDB authentication in production

## 📊 Monitoring & Maintenance

### Service Management
```bash
# Check service status
sudo supervisorctl status

# View application logs
sudo tail -f /var/log/supervisor/zoios-backend.out.log
sudo tail -f /var/log/supervisor/zoios-frontend.out.log

# Restart services
sudo supervisorctl restart all
```

### Database Backup
```bash
# Manual backup
mongodump --db zoios_crm_production --out /backup/$(date +%Y%m%d)

# Automated backups are configured via cron
```

### Health Checks
- **Backend Health**: `http://your-domain.com/docs`
- **Database**: `sudo systemctl status mongod`
- **Web Server**: `sudo systemctl status nginx`
- **Application Services**: `sudo supervisorctl status`

## 🤝 Support & Troubleshooting

### Common Issues

1. **Application Won't Start**
   - Check service logs: `sudo tail -f /var/log/supervisor/zoios-*.log`
   - Verify MongoDB is running: `sudo systemctl status mongod`
   - Check disk space: `df -h`

2. **Authentication Issues** 
   - Verify JWT_SECRET_KEY in backend/.env
   - Clear browser cache and localStorage
   - Check API connectivity: `curl http://localhost:8001/docs`

3. **Database Connection Issues**
   - Restart MongoDB: `sudo systemctl restart mongod`  
   - Check MongoDB logs: `sudo tail -f /var/log/mongodb/mongod.log`
   - Verify MONGO_URL in backend/.env

### Log Locations
- **Backend**: `/var/log/supervisor/zoios-backend.out.log`
- **Frontend**: `/var/log/supervisor/zoios-frontend.out.log`
- **Nginx**: `/var/log/nginx/access.log` and `/var/log/nginx/error.log`
- **MongoDB**: `/var/log/mongodb/mongod.log`

### Performance Tuning
- Monitor system resources: `htop`, `iotop`, `nethogs`
- Optimize MongoDB queries and add indexes
- Configure Nginx worker processes based on CPU cores
- Scale horizontally by adding more server instances

## 🔄 Updates & Upgrades

### Application Updates
```bash
# Backup current installation
sudo cp -r /opt/zoios-crm /opt/zoios-crm.backup

# Update application code
cd /opt/zoios-crm
git pull origin main

# Update dependencies
cd backend && source venv/bin/activate && pip install -r requirements.txt
cd ../frontend && yarn install

# Restart services  
sudo supervisorctl restart all
```

### Database Migrations
Database migrations are handled automatically on application startup. Always backup before major updates.

## 📄 API Documentation

Comprehensive API documentation is automatically generated and available at:
- **Swagger UI**: `/docs` endpoint
- **ReDoc**: `/redoc` endpoint

### Key API Endpoints
- `POST /api/auth/login` - User authentication
- `GET /api/dashboard/stats` - Dashboard analytics
- `GET /api/contacts` - List contacts (filtered by user)
- `POST /api/contacts` - Create new contact
- `GET /api/call-logs` - List call logs
- `POST /api/email-responses` - Log email responses

## 🏗️ Development

### Local Development Setup
```bash
# Backend development
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn server:app --reload --port 8001

# Frontend development  
cd frontend
yarn install
yarn start
```

### Testing
```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend  
yarn test
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with modern web technologies for optimal performance
- Designed for scalability and enterprise-level requirements
- Focused on user experience and data security
- Continuously updated with latest security patches and features

---

<div align="center">
<strong>ZOIOS Marketing CRM</strong> - Empowering businesses to track, analyze, and optimize their marketing outreach efforts.

For support and questions, please refer to the troubleshooting section or contact your system administrator.
</div>
