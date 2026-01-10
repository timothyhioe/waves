# Waves Music Player - Deployment Guide

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Minikube Deployment](#minikube-deployment)
- [GCP GKE Production Deployment](#gcp-gke-production-deployment)
- [Managing GKE Cluster](#managing-gke-cluster)
- [Updating Code in Production](#updating-code-in-production)
- [Cost Management](#cost-management)
- [Troubleshooting](#troubleshooting)

---

## Overview

This application consists of three main components:

- **Frontend**: React app served by Nginx (port 80)
- **Backend**: Flask API (port 5000)
- **Database**: PostgreSQL 16 (port 5432)

**Deployment environments:**

1. Local development with Docker Compose
2. Local Kubernetes testing with Minikube
3. Production deployment on GCP GKE

**Current Production:**

- URL: http://34.96.102.237
- Region: europe-west3-a
- GCP Project: waves-music-483916
- Artifact Registry: europe-west3-docker.pkg.dev/waves-music-483916/waves-repo

---

## Prerequisites

### Required Tools

```bash
# Docker
docker --version

# kubectl
kubectl version --client

# gcloud CLI
gcloud --version

# Minikube (for local K8s)
minikube version

# GKE authentication plugin
gcloud components install gke-gcloud-auth-plugin
```

### GCP Setup

```bash
# Login to GCP
gcloud auth login

# Set project
gcloud config set project waves-music-483916

# Configure Docker for Artifact Registry
gcloud auth configure-docker europe-west3-docker.pkg.dev

# Get kubectl credentials for GKE
gcloud container clusters get-credentials waves-gke --zone europe-west3-a
```

---

## Local Development

### Using Docker Compose (Recommended for Development)

**Start all services:**

```bash
cd /home/tim/coding/Music_Player
docker-compose up --build
```

**Access:**

- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- Database: localhost:5432

**Stop services:**

```bash
docker-compose down
```

**View logs:**

```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

**Benefits:**

- Hot reload for frontend (changes appear instantly)
- Backend auto-restarts on code changes
- No Kubernetes complexity
- Free (no cloud costs)

---

## Minikube Deployment

### Initial Setup

**Start Minikube:**

```bash
minikube start --memory=4096 --cpus=2
```

**Enable Ingress addon:**

```bash
minikube addons enable ingress
```

**Point Docker to Minikube's daemon:**

```bash
eval $(minikube docker-env)
```

### Build Images in Minikube

**Backend:**

```bash
cd /home/tim/coding/Music_Player/backend
docker build -t waves-backend:v1.0.0 .
```

**Frontend:**

```bash
cd /home/tim/coding/Music_Player/frontend
docker build -f Dockerfile.prod --build-arg REACT_APP_API_URL="" -t waves-frontend:v1.0.0 .
```

### Deploy to Minikube

**Apply all Kubernetes configs:**

```bash
cd /home/tim/coding/Music_Player

# Create namespace
kubectl apply -f k8s/00-namespace.yaml

# Deploy PostgreSQL
kubectl apply -f k8s/postgres/

# Deploy backend
kubectl apply -f k8s/backend/

# Deploy frontend
kubectl apply -f k8s/frontend/

# Deploy Ingress
kubectl apply -f k8s/ingress/
```

**Update deployments to use local images:**

```bash
# Edit k8s/backend/03-deployment.yaml
# Change image to: waves-backend:v1.0.0
# Change imagePullPolicy to: Never

# Edit k8s/frontend/02-deployment.yaml
# Change image to: waves-frontend:v1.0.0
# Change imagePullPolicy to: Never

kubectl apply -f k8s/backend/03-deployment.yaml
kubectl apply -f k8s/frontend/02-deployment.yaml
```

### Access Minikube Application

**Get Ingress IP:**

```bash
minikube ip
```

**Add to /etc/hosts:**

```bash
echo "$(minikube ip) waves.local" | sudo tee -a /etc/hosts
```

**Start tunnel (required for Ingress to work):**

```bash
minikube tunnel
```

**Access:** https://waves.local

### Minikube Management

**Check status:**

```bash
kubectl get pods -n waves
kubectl get svc -n waves
kubectl get ingress -n waves
```

**View logs:**

```bash
kubectl logs -f deployment/backend -n waves
kubectl logs -f deployment/frontend -n waves
kubectl logs -f statefulset/postgres -n waves
```

**Stop Minikube:**

```bash
minikube stop
```

**Delete Minikube cluster:**

```bash
minikube delete
```

---

## GCP GKE Production Deployment

### Step 1: Create GKE Cluster

**Create cluster (one-time setup):**

```bash
gcloud container clusters create waves-gke \
  --zone europe-west3-a \
  --num-nodes 1 \
  --machine-type e2-medium \
  --disk-size 20 \
  --disk-type pd-standard \
  --enable-autoscaling \
  --min-nodes 1 \
  --max-nodes 2
```

**Get credentials:**

```bash
gcloud container clusters get-credentials waves-gke --zone europe-west3-a
```

**Verify connection:**

```bash
kubectl cluster-info
kubectl get nodes
```

### Step 2: Build and Push Images

**Build backend:**

```bash
cd /home/tim/coding/Music_Player/backend
docker build -t europe-west3-docker.pkg.dev/waves-music-483916/waves-repo/waves-backend:v1.0.1 .
```

**Build frontend:**

```bash
cd /home/tim/coding/Music_Player/frontend
docker build -f Dockerfile.prod \
  --build-arg REACT_APP_API_URL="" \
  -t europe-west3-docker.pkg.dev/waves-music-483916/waves-repo/waves-frontend:v1.0.3 .
```

**Push images to Artifact Registry:**

```bash
docker push europe-west3-docker.pkg.dev/waves-music-483916/waves-repo/waves-backend:v1.0.1
docker push europe-west3-docker.pkg.dev/waves-music-483916/waves-repo/waves-frontend:v1.0.3
```

### Step 3: Update Kubernetes Manifests

**Update image tags in deployment files:**

**k8s/backend/03-deployment.yaml:**

```yaml
spec:
  template:
    spec:
      containers:
        - name: backend
          image: europe-west3-docker.pkg.dev/waves-music-483916/waves-repo/waves-backend:v1.0.1
          imagePullPolicy: Always
```

**k8s/frontend/02-deployment.yaml:**

```yaml
spec:
  template:
    spec:
      containers:
        - name: frontend
          image: europe-west3-docker.pkg.dev/waves-music-483916/waves-repo/waves-frontend:v1.0.3
          imagePullPolicy: Always
```

### Step 4: Deploy to GKE

**Deploy all components:**

```bash
cd /home/tim/coding/Music_Player

# Create namespace
kubectl apply -f k8s/00-namespace.yaml

# Deploy PostgreSQL
kubectl apply -f k8s/postgres/

# Deploy backend
kubectl apply -f k8s/backend/

# Deploy frontend
kubectl apply -f k8s/frontend/

# Deploy default backend (required for GKE Ingress)
kubectl apply -f k8s/ingress/00-default-backend.yaml

# Deploy Ingress
kubectl apply -f k8s/ingress/02-ingress.yaml
```

### Step 5: Wait for Ingress IP

**Monitor Ingress creation:**

```bash
kubectl get ingress waves-ingress -n waves -w
```

**Check Ingress details:**

```bash
kubectl describe ingress waves-ingress -n waves
```

**Get external IP (takes 5-10 minutes):**

```bash
kubectl get ingress waves-ingress -n waves
```

The ADDRESS column will show the external IP (e.g., 34.96.102.237).

### Step 6: Verify Deployment

**Check all pods are running:**

```bash
kubectl get pods -n waves
```

Expected output:

```
NAME                        READY   STATUS    RESTARTS   AGE
backend-xxx                 1/1     Running   0          5m
frontend-xxx                1/1     Running   0          5m
postgres-0                  1/1     Running   0          5m
```

**Test health endpoints:**

```bash
# Get Ingress IP
INGRESS_IP=$(kubectl get ingress waves-ingress -n waves -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Test frontend
curl http://$INGRESS_IP

# Test backend API
curl http://$INGRESS_IP/api/health
```

**Access application:**
Open browser to: http://34.96.102.237

---

## Managing GKE Cluster

### Pause Cluster (Stop Billing)

**Option 1: Delete cluster (recommended for long pauses)**

```bash
# Save current state (optional)
kubectl get all -n waves -o yaml > waves-backup.yaml

# Delete cluster
gcloud container clusters delete waves-gke --zone europe-west3-a --quiet
```

**Cost savings:** Approximately $68/month

**To restore:**

```bash
# Recreate cluster (see Step 1 above)
gcloud container clusters create waves-gke \
  --zone europe-west3-a \
  --num-nodes 1 \
  --machine-type e2-medium \
  --disk-size 20

# Get credentials
gcloud container clusters get-credentials waves-gke --zone europe-west3-a

# Reapply all configurations
kubectl apply -f k8s/00-namespace.yaml
kubectl apply -f k8s/postgres/
kubectl apply -f k8s/backend/
kubectl apply -f k8s/frontend/
kubectl apply -f k8s/ingress/
```

**Option 2: Scale down nodes (minimal savings)**

```bash
# Scale to 0 nodes (still pays for control plane)
gcloud container clusters resize waves-gke \
  --num-nodes 0 \
  --zone europe-west3-a

# Scale back up
gcloud container clusters resize waves-gke \
  --num-nodes 1 \
  --zone europe-west3-a
```

Note: This only saves node costs, not control plane costs.

### Check Cluster Status

```bash
# Cluster info
gcloud container clusters list

# Node status
kubectl get nodes

# Resource usage
kubectl top nodes
kubectl top pods -n waves

# Cluster events
kubectl get events -n waves --sort-by='.lastTimestamp'
```

### View Logs

```bash
# Backend logs
kubectl logs -f deployment/backend -n waves

# Frontend logs
kubectl logs -f deployment/frontend -n waves

# PostgreSQL logs
kubectl logs -f statefulset/postgres -n waves

# Ingress controller logs
kubectl logs -n kube-system -l k8s-app=glbc --tail=50
```

---

## Updating Code in Production

### Quick Update Workflow (Using same image tag)

**For testing/development only - use :latest tag:**

1. **Build with latest tag:**

```bash
# Backend
cd /home/tim/coding/Music_Player/backend
docker build -t europe-west3-docker.pkg.dev/waves-music-483916/waves-repo/waves-backend:latest .
docker push europe-west3-docker.pkg.dev/waves-music-483916/waves-repo/waves-backend:latest

# Frontend
cd /home/tim/coding/Music_Player/frontend
docker build -f Dockerfile.prod --build-arg REACT_APP_API_URL="" \
  -t europe-west3-docker.pkg.dev/waves-music-483916/waves-repo/waves-frontend:latest .
docker push europe-west3-docker.pkg.dev/waves-music-483916/waves-repo/waves-frontend:latest
```

2. **Force pod restart:**

```bash
kubectl rollout restart deployment/backend -n waves
kubectl rollout restart deployment/frontend -n waves
```

3. **Wait for rollout:**

```bash
kubectl rollout status deployment/backend -n waves
kubectl rollout status deployment/frontend -n waves
```

### Proper Version Update Workflow (Recommended for Production)

**Use semantic versioning for production deployments:**

1. **Build with new version tag:**

```bash
# Increment version (e.g., v1.0.1 -> v1.0.2)
NEW_VERSION="v1.0.2"

# Backend
cd /home/tim/coding/Music_Player/backend
docker build -t europe-west3-docker.pkg.dev/waves-music-483916/waves-repo/waves-backend:$NEW_VERSION .
docker push europe-west3-docker.pkg.dev/waves-music-483916/waves-repo/waves-backend:$NEW_VERSION

# Frontend
cd /home/tim/coding/Music_Player/frontend
docker build -f Dockerfile.prod --build-arg REACT_APP_API_URL="" \
  -t europe-west3-docker.pkg.dev/waves-music-483916/waves-repo/waves-frontend:$NEW_VERSION .
docker push europe-west3-docker.pkg.dev/waves-music-483916/waves-repo/waves-frontend:$NEW_VERSION
```

2. **Update deployment manifests:**

Edit `k8s/backend/03-deployment.yaml`:

```yaml
image: europe-west3-docker.pkg.dev/waves-music-483916/waves-repo/waves-backend:v1.0.2
```

Edit `k8s/frontend/02-deployment.yaml`:

```yaml
image: europe-west3-docker.pkg.dev/waves-music-483916/waves-repo/waves-frontend:v1.0.2
```

3. **Apply changes:**

```bash
kubectl apply -f k8s/backend/03-deployment.yaml
kubectl apply -f k8s/frontend/02-deployment.yaml
```

4. **Verify rollout:**

```bash
kubectl rollout status deployment/backend -n waves
kubectl rollout status deployment/frontend -n waves

# Check pods are running new version
kubectl get pods -n waves
kubectl describe pod <pod-name> -n waves | grep Image:
```

### Rollback to Previous Version

**If deployment fails:**

```bash
# Rollback backend
kubectl rollout undo deployment/backend -n waves

# Rollback frontend
kubectl rollout undo deployment/frontend -n waves

# Or rollback to specific revision
kubectl rollout history deployment/backend -n waves
kubectl rollout undo deployment/backend -n waves --to-revision=2
```

### Zero-Downtime Updates

The current configuration supports zero-downtime updates:

- Rolling update strategy (1 pod at a time)
- Readiness probes ensure traffic only goes to healthy pods
- LoadBalancer automatically routes around updating pods

**Monitor rolling update:**

```bash
kubectl rollout status deployment/backend -n waves --watch
```

---

## Cost Management

### Current Monthly Costs (Approximate)

**GKE cluster running 24/7:**

- Control plane: Free (one zonal cluster per billing account)
- Compute Engine nodes: ~$25/month (1x e2-medium)
- Persistent disks: ~$2/month (30GB total)
- LoadBalancer (Ingress): ~$18/month
- Network egress: ~$5-10/month (depends on usage)
- **Total: ~$50-55/month**

### Cost Optimization Tips

1. **Delete cluster when not in use:**

```bash
gcloud container clusters delete waves-gke --zone europe-west3-a
```

2. **Use smaller machine types for testing:**

```bash
--machine-type e2-small  # Cheaper but may have resource constraints
```

3. **Reduce disk size:**

```bash
--disk-size 10  # 10GB instead of 20GB
```

4. **Set up billing alerts:**

```bash
# Via GCP Console: Billing -> Budgets & alerts
# Set alert at $20, $40, $60
```

5. **Monitor costs:**

```bash
gcloud billing accounts list
# View in GCP Console: Billing -> Reports
```

6. **Use preemptible nodes (not recommended for production):**

```bash
--preemptible  # Up to 80% cheaper but can be shut down at any time
```

---

## Troubleshooting

### Pods Not Starting

**Check pod status:**

```bash
kubectl get pods -n waves
kubectl describe pod <pod-name> -n waves
```

**Common issues:**

**1. ImagePullBackOff / ErrImagePull**

```bash
# Check image exists in registry
gcloud artifacts docker images list europe-west3-docker.pkg.dev/waves-music-483916/waves-repo

# Verify Docker authentication
gcloud auth configure-docker europe-west3-docker.pkg.dev
```

**2. CrashLoopBackOff**

```bash
# Check logs for errors
kubectl logs <pod-name> -n waves

# Check previous crashed container
kubectl logs <pod-name> -n waves --previous
```

**3. Pending (Insufficient resources)**

```bash
# Check events
kubectl describe pod <pod-name> -n waves

# Lower resource requests in deployment YAML
# Or scale up cluster
gcloud container clusters resize waves-gke --num-nodes 2 --zone europe-west3-a
```

**4. PVC not binding**

```bash
# Check PVC status
kubectl get pvc -n waves

# Check StorageClass
kubectl get storageclass

# Describe PVC for events
kubectl describe pvc <pvc-name> -n waves
```

### Ingress Not Working

**Check Ingress status:**

```bash
kubectl get ingress waves-ingress -n waves
kubectl describe ingress waves-ingress -n waves
```

**Common issues:**

**1. No external IP (ADDRESS empty)**

- Wait 5-10 minutes (GCP LoadBalancer provisioning is slow)
- Check events: `kubectl describe ingress waves-ingress -n waves`
- Verify default backend exists: `kubectl get deployment -n kube-system default-http-backend`

**2. 404 Not Found**

- Check backend services are running: `kubectl get svc -n waves`
- Verify Ingress paths match service ports
- Check backend logs: `kubectl logs deployment/backend -n waves`

**3. 502 Bad Gateway**

- Backend pods not healthy/ready
- Check health probes: `kubectl describe deployment backend -n waves`
- View backend logs for errors

**4. CORS errors**

- Verify backend CORS config includes Ingress IP
- Check browser console for specific CORS error
- Test with curl: `curl -v -H "Origin: http://<INGRESS_IP>" http://<INGRESS_IP>/api/login`

### Database Issues

**Check PostgreSQL status:**

```bash
kubectl get statefulset postgres -n waves
kubectl logs statefulset/postgres -n waves
```

**Connect to database:**

```bash
# Port forward to localhost
kubectl port-forward statefulset/postgres 5432:5432 -n waves

# Connect with psql
psql -h localhost -U waves_user -d waves_music
# Password: waves_password
```

**Check PVC:**

```bash
kubectl get pvc -n waves
kubectl describe pvc postgres-data-postgres-0 -n waves
```

### Network Issues

**Test connectivity between pods:**

```bash
# Get pod name
kubectl get pods -n waves

# Exec into backend pod
kubectl exec -it <backend-pod> -n waves -- /bin/sh

# Test connection to postgres
nc -zv postgres-service.waves.svc.cluster.local 5432

# Test DNS resolution
nslookup postgres-service.waves.svc.cluster.local
```

**Check services:**

```bash
kubectl get svc -n waves
kubectl get endpoints -n waves
```

### Performance Issues

**Check resource usage:**

```bash
kubectl top nodes
kubectl top pods -n waves
```

**Increase resources in deployment YAML:**

```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

**Scale deployment:**

```bash
# Increase replicas
kubectl scale deployment backend --replicas=2 -n waves
```

### View All Resources

```bash
# Everything in waves namespace
kubectl get all -n waves

# With more details
kubectl get all -n waves -o wide

# Include ConfigMaps, Secrets, PVCs
kubectl get all,cm,secret,pvc,ingress -n waves
```

---

## Additional Resources

**Kubernetes Documentation:**

- https://kubernetes.io/docs/home/

**GKE Documentation:**

- https://cloud.google.com/kubernetes-engine/docs

**Docker Documentation:**

- https://docs.docker.com/

**GCP Pricing Calculator:**

- https://cloud.google.com/products/calculator

**Useful kubectl commands:**

```bash
# Get help
kubectl --help
kubectl <command> --help

# Explain resource types
kubectl explain deployment
kubectl explain pod.spec.containers

# Edit resources directly
kubectl edit deployment backend -n waves

# Delete resources
kubectl delete pod <pod-name> -n waves
kubectl delete deployment backend -n waves

# Get resource YAML
kubectl get deployment backend -n waves -o yaml

# Apply from directory
kubectl apply -f k8s/ -R

# Watch resources
kubectl get pods -n waves --watch
```

---

## Quick Reference

### Daily Development Commands

```bash
# Start local development
docker-compose up

# Build and test in Minikube
eval $(minikube docker-env)
docker build -t waves-backend:dev backend/
kubectl set image deployment/backend backend=waves-backend:dev -n waves

# Deploy to GKE
docker build -t europe-west3-docker.pkg.dev/waves-music-483916/waves-repo/waves-backend:latest backend/
docker push europe-west3-docker.pkg.dev/waves-music-483916/waves-repo/waves-backend:latest
kubectl rollout restart deployment/backend -n waves

# Check logs
kubectl logs -f deployment/backend -n waves

# Get Ingress IP
kubectl get ingress waves-ingress -n waves
```

### Emergency Commands

```bash
# Delete crashed pod (will be recreated)
kubectl delete pod <pod-name> -n waves

# Restart deployment
kubectl rollout restart deployment/backend -n waves

# Rollback deployment
kubectl rollout undo deployment/backend -n waves

# Delete and recreate everything
kubectl delete namespace waves
kubectl apply -f k8s/ -R

# Check cluster costs
gcloud billing accounts list
```
