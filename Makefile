DC = docker compose
API_CONTAINER = backend_api
.PHONY: up down bash
up:
	${DC} up
down:
	${DC} down

bash:
	${DC} exec -it backend_api bash
