# GZCTF platform — docker-compose helper targets.
# Pure platform ops; for challenge authoring use gzcli separately.

SUDO ?=
COMPOSE = ${SUDO} docker compose -f compose.yml -f compose.traefik.yml

.PHONY: help wizard setup init-config platform-up platform-down platform-restart platform-clean \
        platform-logs gzctf-logs db-logs cache-logs traefik-logs traefik-restart \
        flush-cache pull

help:
	@echo "GZCTF platform make targets:"
	@echo ""
	@echo "  wizard           Interactive first-time setup (writes .env + appsettings.json)"
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
	@echo "  flush-cache      Flush redis (rebuilds scoreboard cache on next request)"
	@echo ""
	@echo "First-time setup:"
	@echo "  make wizard && make setup && make platform-up"
	@echo "  (the wizard prompts for PUBLIC_ENTRY + optional SMTP/captcha, generates an admin password)"

wizard:
	@sh scripts/wizard.sh

setup:
	@echo "Creating external docker networks 'traefik' + 'challenges' (idempotent)..."
	@${SUDO} docker network inspect traefik >/dev/null 2>&1 \
		|| ${SUDO} docker network create traefik
	@${SUDO} docker network inspect challenges >/dev/null 2>&1 \
		|| ${SUDO} docker network create challenges
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
