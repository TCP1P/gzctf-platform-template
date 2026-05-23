# GZCTF platform — docker-compose helper targets.
# Pure platform ops; for challenge authoring use gzcli separately.

SUDO ?=
COMPOSE = ${SUDO} docker compose -f compose.yml -f compose.traefik.yml

.PHONY: help setup platform-up platform-down platform-restart platform-clean \
        platform-logs gzctf-logs db-logs cache-logs traefik-logs traefik-restart \
        flush-cache init-admin pull

help:
	@echo "GZCTF platform make targets:"
	@echo ""
	@echo "  setup            One-time bootstrap: create the external `traefik` docker network"
	@echo "  platform-up      Start gzctf + db + cache + traefik"
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
	@echo "  1. cp .gzctf/appsettings.example.json .gzctf/appsettings.json"
	@echo "  2. edit .gzctf/.env (WORKSPACE + PUBLIC_ENTRY + ACME email)"
	@echo "  3. edit .gzctf/appsettings.json (admin seed password + secrets)"
	@echo "  4. make setup && make platform-up"

setup:
	@echo "Creating the external 'traefik' docker network (idempotent)..."
	${SUDO} docker network inspect traefik >/dev/null 2>&1 \
		|| ${SUDO} docker network create traefik
	@echo "Done. Run 'make platform-up' to start the platform."

platform-up:
	(cd .gzctf && ${COMPOSE} up -d)

platform-down:
	(cd .gzctf && ${COMPOSE} down)

platform-restart: platform-down platform-up

platform-clean:
	(cd .gzctf && ${COMPOSE} down -v)

pull:
	(cd .gzctf && ${COMPOSE} pull)

platform-logs:
	(cd .gzctf && ${COMPOSE} logs -f)

gzctf-logs:
	(cd .gzctf && ${COMPOSE} logs -f gzctf)

db-logs:
	(cd .gzctf && ${COMPOSE} logs -f db)

cache-logs:
	(cd .gzctf && ${COMPOSE} logs -f cache)

traefik-logs:
	(cd .gzctf && ${COMPOSE} logs -f traefik)

traefik-restart:
	(cd .gzctf && ${COMPOSE} restart traefik)

flush-cache:
	(cd .gzctf && ${COMPOSE} exec cache redis-cli FLUSHALL)

init-admin:
	@echo "Promoting 'admin' user to Admin role..."
	(cd .gzctf && ${COMPOSE} exec db \
		psql -U postgres -d gzctf \
		-c "UPDATE \"AspNetUsers\" SET \"Role\"=3 WHERE \"UserName\"='admin';")
