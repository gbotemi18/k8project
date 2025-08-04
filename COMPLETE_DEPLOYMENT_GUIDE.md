# 🚀 Complete Deployment Guide - All Options

This guide covers all deployment options for the IP Reversal Application, from local development to production Kubernetes deployment.

## 📋 Prerequisites Checklist

### Required Tools
- [ ] **Docker Desktop** - For containerization
- [ ] **kubectl** - Kubernetes command-line tool
- [ ] **helm** - Kubernetes package manager
- [ ] **Git** - Version control
- [ ] **Kubernetes Cluster** - For production deployment

### Optional Tools
- [ ] **ArgoCD CLI** - For GitOps deployment
- [ ] **GitHub Account** - For CI/CD pipeline

---

## 🏠 **Option A: Local Development (5 minutes)**

### Step 1: Start Docker Desktop
1. Open Docker Desktop application
2. Wait for Docker to start (green icon in system tray)
3. Verify Docker is running:
   ```bash
   docker --version
   docker ps
   ```

### Step 2: Start Application
```bash
# Navigate to project directory
cd "K8S PROJECT"

# Start with Docker Compose
docker-compose up -d

# Check if services are running
docker-compose ps
```

### Step 3: Access Application
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/api/health

### Step 4: Test Application
```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Test IP reversal
curl http://localhost:8000/api/ip

# Run automated tests
python test_app.py
```

### Step 5: View Logs
```bash
# View application logs
docker-compose logs app

# View database logs
docker-compose logs postgres

# Follow logs in real-time
docker-compose logs -f app
```

### Step 6: Stop Application
```bash
# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## ☸️ **Option B: Kubernetes Deployment (15 minutes)**

### Step 1: Install Required Tools

#### Install kubectl
```bash
# Windows (using Chocolatey)
choco install kubernetes-cli

# Windows (using winget)
winget install Kubernetes.kubectl

# Or download from: https://kubernetes.io/docs/tasks/tools/install-kubectl/
```

#### Install Helm
```bash
# Windows (using Chocolatey)
choco install kubernetes-helm

# Windows (using winget)
winget install Helm.Helm

# Or download from: https://helm.sh/docs/intro/install/
```

### Step 2: Configure Kubernetes Access
```bash
# Check if you have access to a cluster
kubectl cluster-info

# If using minikube
minikube start

# If using Docker Desktop Kubernetes
# Enable Kubernetes in Docker Desktop settings
```

### Step 3: Automated Deployment
```bash
# Make deployment script executable
chmod +x deploy.sh

# Run the deployment
./deploy.sh
```

### Step 4: Manual Deployment (Alternative)
```bash
# Create namespaces
kubectl create namespace production
kubectl create namespace staging
kubectl create namespace monitoring

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

### Step 5: Verify Deployment
```bash
# Check pods
kubectl get pods -n production
kubectl get pods -n staging

# Check services
kubectl get svc -n production
kubectl get svc -n staging

# Check ingress
kubectl get ingress -n production
```

### Step 6: Access Application
```bash
# Port forward for local access
kubectl port-forward -n production svc/ip-reversal 8080:80

# Access at: http://localhost:8080
```

---

## 🔄 **Option C: CI/CD Pipeline Setup**

### Step 1: GitHub Repository Setup
1. Create a new GitHub repository
2. Push your code to the repository:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/your-username/ip-reversal-app.git
   git push -u origin main
   ```

### Step 2: Configure GitHub Secrets
Go to your repository → Settings → Secrets and variables → Actions:

Add these secrets:
```
KUBE_CONFIG_STAGING=<base64-encoded-staging-kubeconfig>
KUBE_CONFIG_PROD=<base64-encoded-production-kubeconfig>
```

### Step 3: Update Configuration Files
Update these files with your specific values:

#### Update `.github/workflows/ci-cd.yml`
```yaml
env:
  REGISTRY: ghcr.io
  IMAGE_NAME: your-username/ip-reversal-app
```

#### Update `helm-chart/values.yaml`
```yaml
image:
  repository: ghcr.io/your-username/ip-reversal-app
```

#### Update `argocd/application.yaml`
```yaml
source:
  repoURL: https://github.com/your-username/ip-reversal-app.git
```

### Step 4: Trigger Pipeline
```bash
# Push changes to trigger CI/CD
git add .
git commit -m "Configure CI/CD pipeline"
git push origin main
```

### Step 5: Monitor Pipeline
1. Go to GitHub repository → Actions tab
2. Monitor the pipeline execution
3. Check deployment status in Kubernetes

---

## ⚙️ **Option D: Configuration Customization**

### Step 1: Environment Configuration

#### Update Database Settings
Edit `helm-chart/values.yaml`:
```yaml
database:
  external:
    enabled: true
    host: "your-postgres-host"
    port: 5432
    name: "ip_reversal_db"
    user: "your-user"
    password: "your-password"
```

#### Update Application Settings
```yaml
config:
  debug: false
  host: "0.0.0.0"
  port: 8000

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi
```

### Step 2: Scaling Configuration
```yaml
# Horizontal Pod Autoscaler
hpa:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80
```

### Step 3: Ingress Configuration
```yaml
ingress:
  enabled: true
  className: "nginx"
  hosts:
    - host: ip-reversal.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: ip-reversal-tls
      hosts:
        - ip-reversal.yourdomain.com
```

### Step 4: Monitoring Configuration
```yaml
monitoring:
  enabled: true
  serviceMonitor:
    enabled: true
    interval: 30s
    scrapeTimeout: 10s
```

---

## 🧪 **Testing All Deployments**

### Local Development Testing
```bash
# Test API endpoints
curl http://localhost:8000/api/health
curl http://localhost:8000/api/ip
curl http://localhost:8000/api/stats

# Test web interface
open http://localhost:8000
```

### Kubernetes Testing
```bash
# Test production deployment
kubectl port-forward -n production svc/ip-reversal 8080:80
curl http://localhost:8080/api/health

# Test staging deployment
kubectl port-forward -n staging svc/ip-reversal-staging 8081:80
curl http://localhost:8081/api/health
```

### Monitoring Testing
```bash
# Access Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
# Open http://localhost:3000 (admin/admin123)

# Access ArgoCD
kubectl port-forward -n argocd svc/argocd-server 8080:443
# Open https://localhost:8080
```

---

## 🚨 **Troubleshooting**

### Docker Issues
```bash
# Check Docker status
docker ps

# Restart Docker Desktop
# Check Docker logs
docker system info
```

### Kubernetes Issues
```bash
# Check cluster status
kubectl cluster-info

# Check node status
kubectl get nodes

# Check pod status
kubectl get pods --all-namespaces

# Check events
kubectl get events --all-namespaces --sort-by='.lastTimestamp'
```

### Application Issues
```bash
# Check application logs
kubectl logs -f deployment/ip-reversal -n production

# Check database connectivity
kubectl exec -it <pod-name> -n production -- nc -zv <db-host> 5432

# Check secrets
kubectl get secrets -n production
```

---

## 📊 **Monitoring & Observability**

### Access Grafana Dashboards
1. Port forward Grafana: `kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80`
2. Open http://localhost:3000
3. Login: admin/admin123
4. Import dashboard: `monitoring/grafana-dashboard.json`

### Access Prometheus
1. Port forward Prometheus: `kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090`
2. Open http://localhost:9090

### Access ArgoCD
1. Port forward ArgoCD: `kubectl port-forward -n argocd svc/argocd-server 8080:443`
2. Open https://localhost:8080
3. Login: admin/$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)

---

## 🎯 **Success Criteria**

### ✅ Local Development
- [ ] Application starts with Docker Compose
- [ ] Web interface accessible at http://localhost:8000
- [ ] API endpoints respond correctly
- [ ] Database stores IP addresses

### ✅ Kubernetes Deployment
- [ ] All pods are running
- [ ] Services are accessible
- [ ] Ingress routes traffic correctly
- [ ] HPA scales based on load

### ✅ CI/CD Pipeline
- [ ] Pipeline runs on code push
- [ ] Images are built and pushed
- [ ] Staging deployment succeeds
- [ ] Production deployment succeeds

### ✅ Monitoring
- [ ] Prometheus collects metrics
- [ ] Grafana displays dashboards
- [ ] Alerts are configured
- [ ] Blackbox exporter monitors health

---

## 🚀 **Next Steps**

1. **Start with Option A** (Local Development) to test the application
2. **Move to Option B** (Kubernetes) for production-like environment
3. **Configure Option C** (CI/CD) for automated deployments
4. **Customize Option D** (Configuration) for your specific needs

---

**Your IP Reversal Application is now ready for production deployment!** 🎉

For additional support, refer to:
- `README.md` - General project information
- `DEPLOYMENT.md` - Detailed deployment instructions
- `QUICK_START.md` - Quick start guide
- `PROJECT_SUMMARY.md` - Complete project overview 