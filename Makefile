# GZCTF platform — docker-compose helper targets.
# Pure platform ops; for challenge authoring use gzcli separately.

SUDO ?=
COMPOSE = ${SUDO} docker compose -f compose.yml -f compose.traefik.yml

.PHONY: help setup init-config platform-up platform-down platform-restart platform-clean \
        platform-logs gzctf-logs db-logs cache-logs traefik-logs traefik-restart \
        flush-cache init-admin pull

help:
	@echo "GZCTF platform make targets:"
	@echo ""
	@echo "  setup            One-time bootstrap: create the external `traefik` docker network"
	@echo "  init-config      Generate compose/appsettings.json from the example + .env (auto-runs on platform-up)"
	@echo "  platform-up      Start gzctf + db + cache + traefik (auto-runs init-config if config missing)"
	@echo "  platform-down    Stop everything (keeps volumes)"
	@echo "  platform-restart Restart all services"
	@echo "  platform-clean   Stop everything AND drop volumes (data loss)"
	@echo "  pull             Pull the latest image for every service"
	@echo ""
	@echo "  platform-logs    Tail logs for all services"
	@echo "  gzctf-logs       Tail gzctf only"
	@echo "  db-logs          Tail postgres only"
	@echo "  cache-logs       Tail redis only"
	@echo "  traefik-logs     Tail traefik only"
	@echo "  traefik-restart  Restart traefik only"
	@echo ""
	@echo "  init-admin       Promote the 'admin' user to Admin role after first login"
	@echo "  flush-cache      Flush redis (rebuilds scoreboard cache on next request)"
	@echo ""
	@echo "Before first 'platform-up':"
	@echo "  1. edit compose/.env (PUBLIC_ENTRY at minimum)"
	@echo "  2. make setup && make platform-up"
	@echo "  (init-config runs automatically; XorKey is generated; admin password is in the appsettings.json that gets created)"

setup:
	@echo "Creating the external 'traefik' docker network (idempotent)..."
	${SUDO} docker network inspect traefik >/dev/null 2>&1 \
		|| ${SUDO} docker network create traefik
	@echo "Done. Run 'make platform-up' to start the platform."

# Generates compose/appsettings.json from the shipped example on
# first run. Idempotent — bails silently if the file already exists.
init-config:
	@sh scripts/init-config.sh

platform-up: init-config
	(cd compose && ${COMPOSE} up -d)

platform-down:
	(cd compose && ${COMPOSE} down)

platform-restart: platform-down platform-up

platform-clean:
	(cd compose && ${COMPOSE} down -v)

pull:
	(cd compose && ${COMPOSE} pull)

platform-logs:
	(cd compose && ${COMPOSE} logs -f)

gzctf-logs:
	(cd compose && ${COMPOSE} logs -f gzctf)

db-logs:
	(cd compose && ${COMPOSE} logs -f db)

cache-logs:
	(cd compose && ${COMPOSE} logs -f cache)

traefik-logs:
	(cd compose && ${COMPOSE} logs -f traefik)

traefik-restart:
	(cd compose && ${COMPOSE} restart traefik)

flush-cache:
	(cd compose && ${COMPOSE} exec cache redis-cli FLUSHALL)

init-admin:
	@echo "Promoting 'admin' user to Admin role..."
	(cd compose && ${COMPOSE} exec db \
		psql -U postgres -d gzctf \
		-c "UPDATE \"AspNetUsers\" SET \"Role\"=3 WHERE \"UserName\"='admin';")
