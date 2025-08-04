# 🚀 Quick Start Guide

Get the IP Reversal Application up and running in minutes!

## Prerequisites

- **Docker** and **Docker Compose** (for local development)
- **kubectl** and **helm** (for Kubernetes deployment)
- **Git** (for cloning the repository)

## Option 1: Local Development (5 minutes)

### 1. Clone and Navigate
```bash
git clone <your-repo-url>
cd K8S\ PROJECT
```

### 2. Start with Docker Compose
```bash
docker-compose up -d
```

### 3. Access the Application
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/api/health

### 4. Test the Application
```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Test IP reversal
curl http://localhost:8000/api/ip

# Run automated tests
python test_app.py
```

## Option 2: Kubernetes Deployment (15 minutes)

### 1. Prerequisites Check
```bash
# Check if you have access to a Kubernetes cluster
kubectl cluster-info

# Check if Helm is installed
helm version
```

### 2. Automated Deployment
```bash
# Make deployment script executable
chmod +x deploy.sh

# Run the deployment
./deploy.sh
```

### 3. Access the Application
```bash
# Get service URLs
kubectl get svc -n production
kubectl get svc -n staging

# Port forward for local access
kubectl port-forward -n production svc/ip-reversal 8080:80
```

### 4. Access Monitoring
```bash
# Port forward Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Port forward ArgoCD
kubectl port-forward -n argocd svc/argocd-server 8080:443
```

## Option 3: Manual Kubernetes Deployment

### 1. Create Namespaces
```bash
kubectl create namespace production
kubectl create namespace staging
kubectl create namespace monitoring
```

### 2. Deploy Application
```bash
# Deploy to staging
helm install ip-reversal-staging ./helm-chart \
  --namespace staging \
  --set image.tag=latest \
  --set replicaCount=1

# Deploy to production
helm install ip-reversal ./helm-chart \
  --namespace production \
  --set image.tag=latest \
  --set replicaCount=2
```

### 3. Verify Deployment
```bash
# Check pods
kubectl get pods -n production
kubectl get pods -n staging

# Check services
kubectl get svc -n production
kubectl get svc -n staging
```

## 🧪 Testing the Application

### API Endpoints
```bash
# Health check
curl http://localhost:8000/api/health

# Get reversed IP
curl http://localhost:8000/api/ip

# Get IP history
curl http://localhost:8000/api/history

# Get statistics
curl http://localhost:8000/api/stats
```

### Web Interface
1. Open http://localhost:8000 in your browser
2. You'll see your IP address and its reversed version
3. View application statistics and history

### Database Verification
```bash
# Connect to database (if using Docker Compose)
docker exec -it ip_reversal_db psql -U user -d ip_reversal_db

# Check IP addresses table
SELECT * FROM ip_addresses ORDER BY timestamp DESC LIMIT 10;
```

## 📊 Monitoring Access

### Grafana Dashboard
- **URL**: http://localhost:3000
- **Username**: admin
- **Password**: admin123
- **Dashboard**: Import `monitoring/grafana-dashboard.json`

### ArgoCD (GitOps)
- **URL**: http://localhost:8080
- **Username**: admin
- **Password**: Get with: `kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d`

## 🔧 Configuration

### Environment Variables
```bash
# Database connection
DATABASE_URL=postgresql://user:password@localhost:5432/ip_reversal_db

# Application settings
DEBUG=false
HOST=0.0.0.0
PORT=8000
```

### Helm Values
Key configuration options in `helm-chart/values.yaml`:
```yaml
# Replica count
replicaCount: 2

# Resource limits
resources:
  limits:
    cpu: 500m
    memory: 512Mi

# Autoscaling
hpa:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Docker Compose Issues
```bash
# Check if Docker is running
docker ps

# Restart services
docker-compose down
docker-compose up -d

# Check logs
docker-compose logs app
docker-compose logs postgres
```

#### 2. Kubernetes Issues
```bash
# Check pod status
kubectl get pods -n production
kubectl describe pod <pod-name> -n production

# Check logs
kubectl logs <pod-name> -n production

# Check events
kubectl get events -n production --sort-by='.lastTimestamp'
```

#### 3. Database Connection Issues
```bash
# Test database connectivity
kubectl exec -it <pod-name> -n production -- nc -zv <db-host> 5432

# Check database URL in secrets
kubectl get secret ip-reversal-secrets -n production -o yaml
```

### Useful Commands
```bash
# Scale application
kubectl scale deployment ip-reversal --replicas=3 -n production

# Update application
helm upgrade ip-reversal ./helm-chart -n production --set image.tag=latest

# Rollback deployment
kubectl rollout undo deployment/ip-reversal -n production

# View application logs
kubectl logs -f deployment/ip-reversal -n production
```

## 📚 Next Steps

1. **Customize Configuration**: Update `helm-chart/values.yaml` for your environment
2. **Set Up Monitoring**: Import Grafana dashboards and configure alerts
3. **Configure CI/CD**: Update GitHub Actions workflow with your repository
4. **Security Hardening**: Review and update security policies
5. **Performance Tuning**: Optimize resource limits and scaling parameters

## 🆘 Support

- **Documentation**: See `README.md` and `DEPLOYMENT.md`
- **Issues**: Check troubleshooting section above
- **Configuration**: Review `helm-chart/values.yaml` for all options

---

**Ready to deploy!** 🚀

The application is now ready for production use with full monitoring, scaling, and automation capabilities. 