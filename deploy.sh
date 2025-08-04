#!/bin/bash

# IP Reversal Application Kubernetes Deployment Script
# This script automates the complete deployment process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE_PRODUCTION="production"
NAMESPACE_STAGING="staging"
NAMESPACE_MONITORING="monitoring"
NAMESPACE_ARGOCD="argocd"

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command_exists kubectl; then
        print_error "kubectl is not installed. Please install kubectl first."
        exit 1
    fi
    
    if ! command_exists helm; then
        print_error "helm is not installed. Please install helm first."
        exit 1
    fi
    
    # Check if kubectl can connect to cluster
    if ! kubectl cluster-info >/dev/null 2>&1; then
        print_error "Cannot connect to Kubernetes cluster. Please check your kubeconfig."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Function to create namespaces
create_namespaces() {
    print_status "Creating namespaces..."
    
    kubectl create namespace $NAMESPACE_PRODUCTION --dry-run=client -o yaml | kubectl apply -f -
    kubectl create namespace $NAMESPACE_STAGING --dry-run=client -o yaml | kubectl apply -f -
    kubectl create namespace $NAMESPACE_MONITORING --dry-run=client -o yaml | kubectl apply -f -
    kubectl create namespace $NAMESPACE_ARGOCD --dry-run=client -o yaml | kubectl apply -f -
    
    print_success "Namespaces created"
}

# Function to install ArgoCD
install_argocd() {
    print_status "Installing ArgoCD..."
    
    # Add ArgoCD Helm repository
    helm repo add argo https://argoproj.github.io/argo-helm
    helm repo update
    
    # Install ArgoCD
    helm upgrade --install argocd argo/argo-cd \
        --namespace $NAMESPACE_ARGOCD \
        --create-namespace \
        --set server.ingress.enabled=true \
        --set server.ingress.hosts[0]=argocd.local \
        --wait --timeout=10m
    
    print_success "ArgoCD installed"
}

# Function to install Prometheus Stack
install_prometheus() {
    print_status "Installing Prometheus Stack..."
    
    # Add Prometheus Helm repository
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update
    
    # Install kube-prometheus-stack
    helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
        --namespace $NAMESPACE_MONITORING \
        --create-namespace \
        --set grafana.enabled=true \
        --set grafana.adminPassword=admin123 \
        --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
        --wait --timeout=10m
    
    print_success "Prometheus Stack installed"
}

# Function to deploy monitoring components
deploy_monitoring() {
    print_status "Deploying monitoring components..."
    
    # Apply Blackbox Exporter
    kubectl apply -f monitoring/blackbox-exporter.yaml
    
    # Apply Prometheus rules
    kubectl apply -f monitoring/prometheus-rules.yaml
    
    # Wait for Blackbox Exporter to be ready
    kubectl wait --for=condition=available --timeout=300s deployment/blackbox-exporter -n $NAMESPACE_MONITORING
    
    print_success "Monitoring components deployed"
}

# Function to deploy application to staging
deploy_staging() {
    print_status "Deploying application to staging..."
    
    # Deploy using Helm
    helm upgrade --install ip-reversal-staging ./helm-chart \
        --namespace $NAMESPACE_STAGING \
        --create-namespace \
        --set image.tag=latest \
        --set replicaCount=1 \
        --set hpa.enabled=false \
        --set ingress.enabled=false \
        --set service.type=LoadBalancer \
        --wait --timeout=10m
    
    # Wait for deployment to be ready
    kubectl wait --for=condition=available --timeout=300s deployment/ip-reversal-staging -n $NAMESPACE_STAGING
    
    print_success "Application deployed to staging"
}

# Function to deploy application to production
deploy_production() {
    print_status "Deploying application to production..."
    
    # Deploy using Helm
    helm upgrade --install ip-reversal ./helm-chart \
        --namespace $NAMESPACE_PRODUCTION \
        --create-namespace \
        --set image.tag=latest \
        --set replicaCount=2 \
        --set hpa.enabled=true \
        --set ingress.enabled=true \
        --wait --timeout=10m
    
    # Wait for deployment to be ready
    kubectl wait --for=condition=available --timeout=300s deployment/ip-reversal -n $NAMESPACE_PRODUCTION
    
    print_success "Application deployed to production"
}

# Function to deploy ArgoCD applications
deploy_argocd_apps() {
    print_status "Deploying ArgoCD applications..."
    
    # Apply ArgoCD applications
    kubectl apply -f argocd/application-staging.yaml
    kubectl apply -f argocd/application.yaml
    
    print_success "ArgoCD applications deployed"
}

# Function to run smoke tests
run_smoke_tests() {
    print_status "Running smoke tests..."
    
    # Test staging
    STAGING_SERVICE=$(kubectl get svc ip-reversal-staging -n $NAMESPACE_STAGING -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
    if [ -n "$STAGING_SERVICE" ]; then
        print_status "Testing staging service at $STAGING_SERVICE"
        if curl -f http://$STAGING_SERVICE/api/health >/dev/null 2>&1; then
            print_success "Staging health check passed"
        else
            print_warning "Staging health check failed"
        fi
    fi
    
    # Test production
    PROD_SERVICE=$(kubectl get svc ip-reversal -n $NAMESPACE_PRODUCTION -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
    if [ -n "$PROD_SERVICE" ]; then
        print_status "Testing production service at $PROD_SERVICE"
        if curl -f http://$PROD_SERVICE/api/health >/dev/null 2>&1; then
            print_success "Production health check passed"
        else
            print_warning "Production health check failed"
        fi
    fi
}

# Function to display deployment information
show_deployment_info() {
    print_status "Deployment completed successfully!"
    echo
    echo "=== Deployment Information ==="
    echo
    
    echo "Namespaces:"
    kubectl get namespaces | grep -E "(production|staging|monitoring|argocd)"
    echo
    
    echo "Production Pods:"
    kubectl get pods -n $NAMESPACE_PRODUCTION
    echo
    
    echo "Staging Pods:"
    kubectl get pods -n $NAMESPACE_STAGING
    echo
    
    echo "Monitoring Pods:"
    kubectl get pods -n $NAMESPACE_MONITORING
    echo
    
    echo "ArgoCD Pods:"
    kubectl get pods -n $NAMESPACE_ARGOCD
    echo
    
    echo "=== Access Information ==="
    echo
    
    # Get service URLs
    STAGING_URL=$(kubectl get svc ip-reversal-staging -n $NAMESPACE_STAGING -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "Not available")
    PROD_URL=$(kubectl get svc ip-reversal -n $NAMESPACE_PRODUCTION -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "Not available")
    
    echo "Staging URL: http://$STAGING_URL"
    echo "Production URL: http://$PROD_URL"
    echo "Grafana: http://localhost:3000 (admin/admin123)"
    echo "ArgoCD: http://localhost:8080 (admin/$(kubectl -n $NAMESPACE_ARGOCD get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d))"
    echo
    
    echo "=== Useful Commands ==="
    echo "View logs: kubectl logs -f deployment/ip-reversal -n $NAMESPACE_PRODUCTION"
    echo "Scale app: kubectl scale deployment ip-reversal --replicas=3 -n $NAMESPACE_PRODUCTION"
    echo "Port forward Grafana: kubectl port-forward -n $NAMESPACE_MONITORING svc/prometheus-grafana 3000:80"
    echo "Port forward ArgoCD: kubectl port-forward -n $NAMESPACE_ARGOCD svc/argocd-server 8080:443"
}

# Function to clean up (for testing)
cleanup() {
    print_warning "Cleaning up deployment..."
    
    # Delete Helm releases
    helm uninstall ip-reversal -n $NAMESPACE_PRODUCTION 2>/dev/null || true
    helm uninstall ip-reversal-staging -n $NAMESPACE_STAGING 2>/dev/null || true
    helm uninstall prometheus -n $NAMESPACE_MONITORING 2>/dev/null || true
    helm uninstall argocd -n $NAMESPACE_ARGOCD 2>/dev/null || true
    
    # Delete namespaces
    kubectl delete namespace $NAMESPACE_PRODUCTION 2>/dev/null || true
    kubectl delete namespace $NAMESPACE_STAGING 2>/dev/null || true
    kubectl delete namespace $NAMESPACE_MONITORING 2>/dev/null || true
    kubectl delete namespace $NAMESPACE_ARGOCD 2>/dev/null || true
    
    print_success "Cleanup completed"
}

# Main deployment function
main() {
    echo "=========================================="
    echo "IP Reversal Application Deployment Script"
    echo "=========================================="
    echo
    
    # Check if cleanup is requested
    if [ "$1" = "cleanup" ]; then
        cleanup
        exit 0
    fi
    
    # Run deployment steps
    check_prerequisites
    create_namespaces
    install_argocd
    install_prometheus
    deploy_monitoring
    deploy_staging
    deploy_production
    deploy_argocd_apps
    run_smoke_tests
    show_deployment_info
    
    print_success "Deployment completed successfully!"
}

# Run main function with all arguments
main "$@" 