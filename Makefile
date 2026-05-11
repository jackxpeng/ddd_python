# Makefile
IMAGE_NAME = allocation-api:latest
DEPLOYMENT_NAME = allocation-api

.PHONY: all build load restart clean infra bootstrap

# ==========================================
# 1. THE INNER DEV LOOP 
# Run `make` on every code change
# ==========================================
all: build load restart

build:
	@echo "🛠️  Building new Docker image..."
	docker build -t $(IMAGE_NAME) .

load:
	@echo "📦 Loading image into default kind cluster..."
	kind load docker-image $(IMAGE_NAME)

restart:
	@echo "🔄 Restarting API pods..."
	kubectl rollout restart deployment/$(DEPLOYMENT_NAME)
	kubectl rollout status deployment/$(DEPLOYMENT_NAME)


# ==========================================
# 2. THE NUKE & PAVE LOOP 
# Run `make bootstrap` when your cluster dies
# ==========================================
clean:
	@echo "💥 Nuking the zombie cluster..."
	kind delete cluster

infra:
	@echo "🌱 Creating fresh cluster..."
	kind create cluster
	@echo "🏗️  Applying base infrastructure..."
	kubectl apply -f k8s/postgres.yaml
	kubectl apply -f k8s/deployment.yaml
	# Apply any other files you need here, like services
	kubectl apply -f k8s/service.yaml

bootstrap: clean infra all