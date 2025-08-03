.PHONY: help build run stop clean test deploy

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Build the Docker image
	docker-compose build

run: ## Start the application
	docker-compose up -d

stop: ## Stop the application
	docker-compose down

clean: ## Clean up Docker containers and images
	docker-compose down -v
	docker system prune -f

test: ## Run the test suite
	python3 test_app.py

deploy: ## Deploy the application
	./deploy.sh

logs: ## View application logs
	docker-compose logs -f

status: ## Check application status
	@echo "Checking application status..."
	@curl -f http://localhost/health > /dev/null 2>&1 && echo "✅ Application is running" || echo "❌ Application is not running"

backup: ## Backup the database
	@echo "Creating database backup..."
	@docker cp attendance-app:/app/attendance.db ./backup_$(shell date +%Y%m%d_%H%M%S).db
	@echo "Backup created successfully"

restart: ## Restart the application
	docker-compose restart

update: ## Update and restart the application
	git pull
	docker-compose up --build -d