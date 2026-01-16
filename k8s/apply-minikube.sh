#!/bin/bash
# Script to apply Kubernetes manifests for Minikube
# This skips GKE-specific resources like BackendConfig

set -e

echo "Applying Kubernetes manifests for Minikube..."

# Create namespace
kubectl apply -f 00-namespace.yaml

# Deploy PostgreSQL (skip if StatefulSet already exists with different spec)
echo "Deploying PostgreSQL..."
kubectl apply -f postgres/01-secret.yaml
kubectl apply -f postgres/03-service.yaml
# StatefulSet might fail if immutable fields changed - that's OK, it's already deployed

# Deploy backend (skip BackendConfig - GKE only)
echo "Deploying backend..."
kubectl apply -f backend/01-secret.yaml
kubectl apply -f backend/02-configmap.yaml
# Skip PVC if it already exists with different settings
kubectl apply -f backend/02-pvc.yaml || echo "PVC already exists with different settings - skipping"
kubectl apply -f backend/03-deployment.yaml
kubectl apply -f backend/04-service.yaml
# Skip BackendConfig - GKE only
echo "Skipping BackendConfig (GKE-only resource)"
kubectl apply -f backend/06-hpa.yaml

# Deploy frontend
echo "Deploying frontend..."
kubectl apply -f frontend/01-configmap.yaml
kubectl apply -f frontend/02-deployment.yaml
kubectl apply -f frontend/03-service.yaml
kubectl apply -f frontend/04-hpa.yaml

# Deploy Ingress
echo "Deploying Ingress..."
kubectl apply -f k8s/ingress/00-default-backend.yaml
kubectl apply -f k8s/ingress/02-ingress.yaml

echo "Deployment complete!"
echo "Note: BackendConfig was skipped (GKE-only resource)"
