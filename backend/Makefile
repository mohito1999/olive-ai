SHELL := /bin/bash

-include ./.env

services:
	@docker-compose up olive-db --force-recreate --remove-orphans

start:
	@docker-compose up --force-recreate --remove-orphans

watch:
	@docker-compose watch --no-up & docker-compose up olive-db --force-recreate --remove-orphans

rebuild:
	@docker-compose build

local.install:
	@chmod +x ./scripts/init.sh
	@./scripts/init.sh

local.server:
	@source venv/bin/activate;
	@python src/run_uvicorn.py

##################################################
# Database
##################################################
database.connect: ## Connect to database
	docker-compose exec olive-db psql -U ${POSTGRES_USER} --db ${POSTGRES_DB}

database.create.migration: ## Create alembic migration file
	alembic revision --autogenerate

database.upgrade: ## Upgrade to latest migration
	alembic upgrade head

database.downgrade: ## Downgrade latest migration
	alembic downgrade -1

database.fastapi.migrate: ## Run custom command as passed in $ARGS
	alembic $(ARGS)

format:
	@black ./src

##################################################
# Build and deploy
##################################################
build.server:
	@docker build -f docker/server/Dockerfile -t olive-server:latest .

build.worker:
	@docker build -f docker/worker/Dockerfile -t olive-worker:latest .

build.beat:
	@docker build -f docker/beat/Dockerfile -t olive-beat:latest .

aws.login:
	@aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 402963518398.dkr.ecr.us-east-1.amazonaws.com

push.server:
	@docker tag olive-server:latest 402963518398.dkr.ecr.us-east-1.amazonaws.com/olive-backend:latest
	@docker push 402963518398.dkr.ecr.us-east-1.amazonaws.com/olive-backend:latest

push.worker:
	@docker tag olive-worker:latest 402963518398.dkr.ecr.us-east-1.amazonaws.com/olive-worker:latest
	@docker push 402963518398.dkr.ecr.us-east-1.amazonaws.com/olive-worker:latest

push.beat:
	@docker tag olive-beat:latest 402963518398.dkr.ecr.us-east-1.amazonaws.com/olive-scheduler:latest
	@docker push 402963518398.dkr.ecr.us-east-1.amazonaws.com/olive-scheduler:latest

build-and-push-all:
	@make build.server
	@make build.worker
	@make build.beat
	@make push.server
	@make push.worker
	@make push.beat
