# Deployment Guide

This guide will help you deploy the Facial Recognition Attendance System to production.

## Prerequisites

- Docker and Docker Compose installed
- At least 2GB of RAM available
- Internet connection for downloading dependencies

## Quick Deployment

### Option 1: Using Docker Compose (Recommended)

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd attendance-system
   ```

2. **Run the deployment script**:
   ```bash
   ./deploy.sh
   ```

3. **Access the application**:
   Open your browser and go to `http://localhost:5000`

### Option 2: Manual Docker Deployment

1. **Build the Docker image**:
   ```bash
   docker build -t attendance-system .
   ```

2. **Run the container**:
   ```bash
   docker run -d -p 5000:5000 --name attendance-app attendance-system
   ```

### Option 3: Local Development

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   python app.py
   ```

## Environment Variables

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Edit the `.env` file and set appropriate values:

```env
FLASK_ENV=production
SECRET_KEY=your-secure-secret-key-here
DATABASE_URL=attendance.db
HOST=0.0.0.0
PORT=5000
```

## Production Considerations

### Security
- Change the default secret key in production
- Use HTTPS in production
- Set up proper firewall rules
- Regularly update dependencies

### Performance
- Use a reverse proxy (nginx) in front of the application
- Set up proper logging
- Monitor resource usage
- Consider using a production database (PostgreSQL/MySQL)

### Data Persistence
- The SQLite database is stored in a Docker volume
- Backup the database regularly
- Consider using a more robust database for production

## Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   # Check what's using port 5000
   lsof -i :5000
   # Kill the process or change the port in docker-compose.yml
   ```

2. **Docker build fails**:
   ```bash
   # Clean Docker cache
   docker system prune -a
   # Rebuild
   docker-compose build --no-cache
   ```

3. **Application not starting**:
   ```bash
   # Check logs
   docker-compose logs
   # Restart the service
   docker-compose restart
   ```

### Logs

View application logs:
```bash
docker-compose logs -f attendance-app
```

### Stopping the Application

```bash
docker-compose down
```

### Updating the Application

```bash
git pull
docker-compose up --build -d
```

## Monitoring

### Health Check
The application includes a basic health check endpoint at `/health`.

### Resource Monitoring
Monitor CPU, memory, and disk usage:
```bash
docker stats attendance-app
```

## Backup and Restore

### Backup Database
```bash
docker cp attendance-app:/app/attendance.db ./backup_$(date +%Y%m%d_%H%M%S).db
```

### Restore Database
```bash
docker cp ./backup.db attendance-app:/app/attendance.db
docker-compose restart attendance-app
```

## Scaling

For high-traffic deployments, consider:
- Using multiple application instances behind a load balancer
- Implementing caching (Redis)
- Using a production-grade database
- Setting up monitoring and alerting

## Support

If you encounter issues:
1. Check the logs: `docker-compose logs`
2. Verify system requirements
3. Check network connectivity
4. Review the troubleshooting section above