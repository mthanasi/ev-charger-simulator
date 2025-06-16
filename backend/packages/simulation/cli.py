"""Command-line interface for the EV charging station simulator."""
from __future__ import annotations

import argparse
import json
from typing import List

from .core import Charger, SimulationConfig, run_simulation


def parse_chargers(charger_spec: str) -> List[Charger]:
    """Parse charger specification string into list of Charger objects.

    Args:
        charger_spec: String in format 'NxP' where N is count and P is power in kW.
                     Multiple chargers separated by comma (e.g. '5x11,3x22,1x50')

    Returns:
        List[Charger]: List of charger configurations

    Raises:
        ValueError: If charger specification is invalid
    """
    chargers = []
    for spec in charger_spec.split(","):
        try:
            count, power = spec.split("x")
            chargers.append(Charger(power_kw=float(power), count=int(count)))
        except ValueError as e:
            raise ValueError(f"Invalid charger specification '{spec}': {e}")
    return chargers


def main() -> None:
    """Run the EV charger simulator from command line."""
    parser = argparse.ArgumentParser(
        description="EV‑charger utilisation simulator with multiple charger types (DST-aware)"
    )
    parser.add_argument(
        "--chargers",
        type=str,
        default="20x11",
        help="List of chargers in format 'NxP' where N is count and P is power in kW. "
        "Multiple chargers separated by comma (e.g. '5x11,3x22,1x50')",
    )
    parser.add_argument(
        "-m",
        "--mult",
        type=float,
        default=1.0,
        help="arrival multiplier, e.g. 1.2 = +20%",
    )
    parser.add_argument(
        "-s",
        "--seed",
        type=int,
        help="random seed for repeatable runs",
    )
    parser.add_argument(
        "--year",
        type=int,
        default=2023,
        help="year to simulate (for DST calculations)",
    )
    parser.add_argument(
        "--consumption",
        type=float,
        default=18.0,
        help="Vehicle energy consumption in kWh per 100km (default: 18.0 kWh/100km)",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file for simulation results (JSON format)",
    )
    parser.add_argument(
        "--quick_test",
        action="store_true",
        help="Run a quick test with varying charger counts",
    )
    parser.add_argument(
        "--test-min",
        type=int,
        default=1,
        help="Minimum number of chargers for quick test",
    )
    parser.add_argument(
        "--test-max",
        type=int,
        default=30,
        help="Maximum number of chargers for quick test",
    )
    parser.add_argument(
        "--test-step",
        type=int,
        default=1,
        help="Step size for charger count in quick test",
    )

    args = parser.parse_args()

    # parse charger configuration
    chargers = parse_chargers(args.chargers)

    if args.quick_test:
        # for quick test, we'll vary the count of the first charger type
        base_chargers = chargers[1:] if len(chargers) > 1 else []
        results = []
        for count in range(args.test_min, args.test_max + 1, args.test_step):
            test_chargers = [
                Charger(power_kw=chargers[0].power_kw, count=count)
            ] + base_chargers
            result = run_simulation(
                SimulationConfig(
                    chargers=test_chargers,
                    arrival_multiplier=args.mult,
                    seed=args.seed,
                    year=args.year,
                    energy_per_km=args.consumption / 100.0,
                )
            )
            results.append(
                {
                    "chargers": test_chargers,
                    "multiplier": args.mult,
                    "actual_max_kw": result["actual_max_kw"],
                    "theoretical_max_kw": result["theoretical_max_kw"],
                    "concurrency_factor": result["concurrency_factor"],
                }
            )
            print(
                f"[DST] Chargers: {test_chargers}, "
                f"Multiplier: {args.mult}, "
                f"Actual Max: {result['actual_max_kw']}, "
                f"Theoretical Max: {result['theoretical_max_kw']}, "
                f"Concurrency: {result['concurrency_factor']}"
            )
        if args.output:
            with open(args.output, "w") as f:
                json.dump(results, f, indent=2)
    else:
        result = run_simulation(
            SimulationConfig(
                chargers=chargers,
                arrival_multiplier=args.mult,
                seed=args.seed,
                year=args.year,
                energy_per_km=args.consumption / 100.0,
            )
        )
        # convert charging events to dict for JSON serialization
        serializable_result = {
            **result,
            "charging_events": [event.to_dict() for event in result["charging_events"]],
        }
        print(json.dumps(serializable_result, indent=2))
        if args.output:
            with open(args.output, "w") as f:
                json.dump(serializable_result, f, indent=2)


if __name__ == "__main__":
    main()
