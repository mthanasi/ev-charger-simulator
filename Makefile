DC   := docker compose
ARGS ?=

.DEFAULT_GOAL := help

# -------------------------------------------------------------------
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS = ":.*##"; printf "\nUsage: make <target>\n\nTargets:\n"} \
	       {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}' ; \
	echo "\n  Tip: use \033[36mmake sim-help\033[0m for simulator flags.\n"

# ------------------------------------------------------------------
build:         ## Build (or rebuild) all images
	$(DC) build

up:            ## Start the stack in detached mode
	$(DC) up -d

down:          ## Stop & remove containers (volumes survive)
	$(DC) down

logs:          ## Tail all service logs
	$(DC) logs -f --tail=100

# ------------------------------------------------------------------
# Simulation CLI
# ------------------------------------------------------------------
sim:           ## Exec: run the simulation CLI
	$(DC) exec backend uv run simulator $(ARGS)

# -------------------------------------------------------------------
# Simulator flag reference
# -------------------------------------------------------------------
sim-help: ## List every simulator CLI flag
	@echo "\nSimulation CLI flags:"
	@printf "  \033[36m--chargers\033[0m    List of chargers in format 'NxP' where N is count and P is power in kW.\n"
	@printf "                Multiple chargers separated by comma (e.g. '5x11,3x22,1x50')\n"
	@printf "  \033[36m-m\033[0m, \033[36m--mult\033[0m    Arrival-rate multiplier (default: 1.0)\n"
	@printf "  \033[36m--year\033[0m       Year to simulate (for DST calculations, default: 2023)\n"
	@printf "  \033[36m--consumption\033[0m Vehicle energy consumption in kWh per 100km (default: 18.0)\n"
	@printf "  \033[36m-s\033[0m, \033[36m--seed\033[0m    Random seed for repeatable runs\n"
	@printf "  \033[36m--output\033[0m     Output file for simulation results (JSON format)\n"
	@printf "  \033[36m--quick_test\033[0m Run a quick test with varying charger counts from 1 to 30\n"
	@printf "  \033[36m--test-min\033[0m   Minimum number of chargers for quick test (default: 1)\n"
	@printf "  \033[36m--test-max\033[0m   Maximum number of chargers for quick test (default: 30)\n"
	@printf "  \033[36m--test-step\033[0m  Step size for charger count in quick test (default: 1)\n"
	@echo "\nExample:"
	@echo "  make sim ARGS=\"--chargers '5x11,3x22,1x50' -m 1.25 --year 2024 --consumption 20.0 -s 42\"\n"

.PHONY: help build up down logs api sim run sim-help