# Deployment Guide

This guide covers the complete deployment process for the IP Reversal Web Application using CI/CD, Docker, and Kubernetes.

## Prerequisites

### 1. GitHub Repository Setup
- Create a GitHub repository for the project
- Enable GitHub Actions
- Configure repository secrets:
  - `KUBE_CONFIG_STAGING`: Base64 encoded kubeconfig for staging cluster
  - `KUBE_CONFIG_PROD`: Base64 encoded kubeconfig for production cluster

### 2. Container Registry
- GitHub Container Registry (ghcr.io) is used by default
- Update the image repository in `values.yaml` and CI/CD pipeline

### 3. Kubernetes Cluster
- GKE (Google Kubernetes Engine) recommended
- Minimum 3 nodes with 2 vCPU and 4GB RAM each
- Enable Workload Identity for better security

### 4. Required Tools
- `kubectl` - Kubernetes command-line tool
- `helm` - Helm package manager
- `argocd` - ArgoCD CLI (optional)

## Phase 1: Local Development

### 1. Start the Application Locally
```bash
# Clone the repository
git clone https://github.com/your-username/ip-reversal-app.git
cd ip-reversal-app

# Start with Docker Compose
docker-compose up -d

# Access the application
open http://localhost:8000
```

### 2. Test the Application
```bash
# Run the test script
python test_app.py

# Or test manually
curl http://localhost:8000/api/health
curl http://localhost:8000/api/ip
```

## Phase 2: Containerization

### 1. Build Docker Images
```bash
# Build development image
docker build -f Dockerfile.dev -t ip-reversal-app:dev .

# Build production image
docker build -f Dockerfile -t ip-reversal-app:latest .

# Test the production image
docker run -d -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:password@host:5432/db \
  ip-reversal-app:latest
```

### 2. Push to Container Registry
```bash
# Tag for your registry
docker tag ip-reversal-app:latest ghcr.io/your-username/ip-reversal-app:latest

# Push to registry
docker push ghcr.io/your-username/ip-reversal-app:latest
```

## Phase 3: CI/CD Pipeline

### 1. Configure GitHub Secrets
Go to your GitHub repository → Settings → Secrets and variables → Actions:

```
KUBE_CONFIG_STAGING=<base64-encoded-staging-kubeconfig>
KUBE_CONFIG_PROD=<base64-encoded-production-kubeconfig>
```

### 2. Update Configuration Files
Update the following files with your specific values:

- `.github/workflows/ci-cd.yml` - Update image repository
- `helm-chart/values.yaml` - Update database and ingress settings
- `argocd/application.yaml` - Update repository URL and parameters

### 3. Trigger the Pipeline
```bash
# Push to main branch to trigger deployment
git add .
git commit -m "Initial deployment setup"
git push origin main
```

## Phase 4: Kubernetes Deployment

### 1. Install ArgoCD
```bash
# Add ArgoCD Helm repository
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update

# Install ArgoCD
helm install argocd argo/argo-cd \
  --namespace argocd \
  --create-namespace \
  --set server.ingress.enabled=true \
  --set server.ingress.hosts[0]=argocd.yourdomain.com
```

### 2. Deploy the Application
```bash
# Apply ArgoCD applications
kubectl apply -f argocd/application-staging.yaml
kubectl apply -f argocd/application.yaml

# Or deploy directly with Helm
helm install ip-reversal-staging ./helm-chart \
  --namespace staging \
  --create-namespace \
  --set image.tag=latest

helm install ip-reversal ./helm-chart \
  --namespace production \
  --create-namespace \
  --set image.tag=latest
```

### 3. Verify Deployment
```bash
# Check application status
kubectl get pods -n staging
kubectl get pods -n production

# Check services
kubectl get svc -n staging
kubectl get svc -n production

# Check ingress
kubectl get ingress -n staging
kubectl get ingress -n production
```

## Phase 5: Monitoring Setup

### 1. Install Prometheus Stack
```bash
# Add Prometheus Helm repository
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install kube-prometheus-stack
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set grafana.enabled=true \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false
```

### 2. Configure Blackbox Exporter
```bash
# Create Blackbox Exporter configuration
kubectl apply -f monitoring/blackbox-exporter.yaml

# Create monitoring rules
kubectl apply -f monitoring/prometheus-rules.yaml
```

### 3. Access Grafana
```bash
# Port forward Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Default credentials: admin / prom-operator
open http://localhost:3000
```

## Configuration

### Environment Variables
The application uses the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `DEBUG` | Enable debug mode | `false` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |

### Helm Values
Key configuration options in `helm-chart/values.yaml`:

```yaml
# Database configuration
database:
  external:
    enabled: true
    host: "your-postgres-host"
    password: "your-password"

# Ingress configuration
ingress:
  enabled: true
  hosts:
    - host: ip-reversal.yourdomain.com

# Resource limits
resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi

# Autoscaling
hpa:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check database connectivity
   kubectl exec -it <pod-name> -- nc -zv <db-host> 5432
   
   # Check database URL in secrets
   kubectl get secret ip-reversal-secrets -o yaml
   ```

2. **Image Pull Failed**
   ```bash
   # Check image pull policy
   kubectl describe pod <pod-name>
   
   # Verify image exists
   docker pull ghcr.io/your-username/ip-reversal-app:latest
   ```

3. **Ingress Not Working**
   ```bash
   # Check ingress controller
   kubectl get pods -n ingress-nginx
   
   # Check ingress status
   kubectl describe ingress <ingress-name>
   ```

4. **Health Checks Failing**
   ```bash
   # Check application logs
   kubectl logs <pod-name>
   
   # Test health endpoint directly
   kubectl exec -it <pod-name> -- curl http://localhost:8000/api/health
   ```

### Useful Commands

```bash
# Get application URL
kubectl get ingress -n production

# View application logs
kubectl logs -f deployment/ip-reversal -n production

# Scale application
kubectl scale deployment ip-reversal --replicas=3 -n production

# Update application
helm upgrade ip-reversal ./helm-chart -n production --set image.tag=v1.1.0

# Rollback deployment
kubectl rollout undo deployment/ip-reversal -n production
```

## Security Considerations

1. **Secrets Management**
   - Use Kubernetes secrets for sensitive data
   - Consider using external secret managers (AWS Secrets Manager, HashiCorp Vault)

2. **Network Policies**
   - Enable network policies to restrict pod communication
   - Use service mesh for advanced traffic management

3. **RBAC**
   - Configure proper service accounts and roles
   - Use least privilege principle

4. **Container Security**
   - Scan images for vulnerabilities
   - Use non-root users in containers
   - Enable security contexts

## Monitoring and Alerting

### Prometheus Metrics
The application exposes the following metrics:
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request duration
- `up` - Application health status

### Grafana Dashboards
Import the provided dashboard JSON files:
- `monitoring/grafana-dashboard.json` - Application metrics
- `monitoring/grafana-node-exporter.json` - Node metrics

### Alerting Rules
Configure alerts for:
- Application down
- High error rate
- High response time
- Database connection issues

## Backup and Recovery

### Database Backup
```bash
# Create backup job
kubectl apply -f backup/postgres-backup-job.yaml

# Restore from backup
kubectl apply -f backup/postgres-restore-job.yaml
```

### Application Backup
```bash
# Backup Helm releases
helm list -n production -o yaml > backup/releases.yaml

# Backup secrets
kubectl get secrets -n production -o yaml > backup/secrets.yaml
```

## Performance Optimization

1. **Resource Optimization**
   - Monitor resource usage and adjust limits
   - Use horizontal pod autoscaling
   - Configure pod disruption budgets

2. **Database Optimization**
   - Use connection pooling
   - Optimize queries
   - Consider read replicas for high traffic

3. **Caching**
   - Implement Redis for session storage
   - Use CDN for static assets
   - Enable application-level caching

## Support and Maintenance

### Regular Maintenance Tasks
- Update dependencies monthly
- Rotate secrets quarterly
- Review and update security policies
- Monitor and optimize performance

### Support Channels
- GitHub Issues for bug reports
- Documentation updates
- Community forums

### SLA and Monitoring
- 99.9% uptime target
- < 200ms response time
- Automated health checks every 30 seconds
- 24/7 monitoring and alerting 