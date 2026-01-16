#!/bin/bash
# Script to apply Kubernetes manifests for GKE
# Includes GKE-specific resources like BackendConfig

set -e

echo "Applying Kubernetes manifests for GKE..."

# Verify we're on GKE
CONTEXT=$(kubectl config current-context)
if [[ ! "$CONTEXT" =~ "gke" ]]; then
    echo "WARNING: Current context doesn't appear to be GKE: $CONTEXT"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create namespace
echo "Creating namespace..."
kubectl apply -f 00-namespace.yaml

# Deploy PostgreSQL
echo "Deploying PostgreSQL..."
kubectl apply -f postgres/

# Deploy backend (includes BackendConfig for GKE)
echo "Deploying backend..."
kubectl apply -f backend/

# Deploy frontend
echo "Deploying frontend..."
kubectl apply -f frontend/

# Deploy default backend (required for GKE Ingress)
echo "Deploying default backend..."
kubectl apply -f ingress/00-default-backend.yaml

# Deploy Ingress
echo "Deploying Ingress..."
kubectl apply -f ingress/02-ingress.yaml

echo ""
echo "Deployment complete!"
echo ""
echo "Waiting for Ingress IP (this may take 5-10 minutes)..."
echo "Run this command to check: kubectl get ingress waves-ingress -n waves -w"
echo ""
echo "To get the IP address:"
echo "  kubectl get ingress waves-ingress -n waves -o jsonpath='{.status.loadBalancer.ingress[0].ip}'"