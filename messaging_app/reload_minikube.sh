#!/bin/bash
docker build -t messaging_app:latest ~/alx-backend-python/messaging_app
minikube image load messaging_app:latest
kubectl rollout restart deployment django-blue-deployment
kubectl rollout restart deployment django-green-deployment
kubectl get pods -l app=django-messaging -w
