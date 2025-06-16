"""Core simulation module for EV charging station simulation.

This module provides the core functionality for simulating EV charging stations.
It can be used both as a library and as a command-line tool.
"""
from __future__ import annotations

import datetime
import random
from collections import defaultdict
from dataclasses import dataclass
from typing import List, TypedDict


class SimulationResult(TypedDict):
    """Result of a simulation run.

    Attributes:
        total_energy_kwh: Total energy delivered in kWh
        theoretical_max_kw: Theoretical maximum power in kW
        actual_max_kw: Actual maximum power observed in kW
        concurrency_factor: Ratio of actual to theoretical maximum power
        total_charging_events: Total number of charging events
        events_statistics: Detailed statistics by time period
    """

    total_energy_kwh: float
    theoretical_max_kw: float
    actual_max_kw: float
    concurrency_factor: float
    total_charging_events: int
    events_statistics: dict[str, dict[str, dict[str, dict[str, float | int]]]]


@dataclass
class Charger:
    """Configuration for a single charger type.

    Attributes:
        power_kw: Power rating in kW
        count: Number of chargers of this type
    """

    power_kw: float
    count: int

    @property
    def energy_per_tick_kwh(self) -> float:
        """Calculate energy delivered per 15-minute tick."""
        return self.power_kw * 0.25  # 15-minute tick


@dataclass
class SimulationConfig:
    """Configuration for a simulation run.

    Attributes:
        chargers: List of charger configurations
        arrival_multiplier: Scales all arrival probabilities (1.0 → table values, 1.5 → +50%)
        energy_per_km: Energy consumption per km in kWh
        seed: Random seed for repeatability
        year: Year to simulate (for DST calculations)
    """

    chargers: List[Charger]
    arrival_multiplier: float = 1.0
    energy_per_km: float = 0.18  # 18 kWh / 100 km
    seed: int | None = None
    year: int = 2023


class ChargingEvent:
    """Represents a single charging event.

    Attributes:
        charger_type: Power rating of the charger in kW
        energy_kwh: Total energy needed in kWh
        start_time: When the charging started
        power_kw: Power rating of the charger in kW
    """

    def __init__(
        self,
        charger_type: float,
        energy_kwh: float,
        start_time: datetime.datetime,
        power_kw: float,
    ):
        self.charger_type = charger_type
        self.energy_kwh = energy_kwh
        self.start_time = start_time
        self.power_kw = power_kw

    def to_dict(self) -> dict:
        """Convert the charging event to a dictionary for JSON serialization.

        Returns:
            dict: Dictionary representation of the charging event
        """
        return {
            "charger_type": self.charger_type,
            "energy_kwh": self.energy_kwh,
            "start_time": self.start_time.isoformat(),
            "power_kw": self.power_kw,
        }


# Hour of day arrival probabilities (percent of *free* chargers that get a car
# during that hour). Source: table T1. Index 0 → 00:00 - 01:00, …, 23 → 23:00 - 24:00
_ARRIVAL_PCT_PER_HOUR: list[float] = [
    0.94,
    0.94,
    0.94,
    0.94,
    0.94,
    0.94,
    0.94,
    0.94,  # 00 - 08
    2.83,
    2.83,  # 08 - 10
    5.66,
    5.66,
    5.66,  # 10 - 13
    7.55,
    7.55,
    7.55,  # 13 - 16
    10.38,
    10.38,
    10.38,  # 16 - 19
    4.72,
    4.72,
    4.72,  # 19 - 22
    0.94,
    0.94,  # 22 - 24
]

# Cumulative demand distribution [(cumulative prob, km)]
_DEMAND_CUMULATIVE: list[tuple[float, int]] = []
_temp = 0.0
for pct, km in [
    (34.31, 0),
    (4.90, 5),
    (9.80, 10),
    (11.76, 20),
    (8.82, 30),
    (11.76, 50),
    (10.78, 100),
    (4.90, 200),
    (2.94, 300),
]:
    _temp += pct / 100.0
    _DEMAND_CUMULATIVE.append((_temp, km))

# Constants
TICKS_PER_HOUR = 4  # 15 minute granularity


def _sample_km() -> int:
    """Return a km demand drawn from the cumulative table (0 means no charge).

    Returns:
        int: Kilometers of range needed (0 means no charging needed)
    """
    r = random.random()
    for threshold, km in _DEMAND_CUMULATIVE:
        if r <= threshold:
            return km
    return 0


def _last_sunday(year: int, month: int) -> datetime.date:
    """Find the last Sunday of a given month.

    Args:
        year: Year
        month: Month (0-11)

    Returns:
        datetime.date: Last Sunday of the month
    """
    d = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
    while d.weekday() != 6:
        d -= datetime.timedelta(days=1)
    return d


def run_simulation(config: SimulationConfig) -> SimulationResult:
    """Run the 1 year simulation and return headline KPIs.

    The simulation models multiple charger types for one calendar year at
    15 minute resolution, with proper DST handling.

    Args:
        config: Simulation configuration

    Returns:
        SimulationResult: Dictionary containing simulation results

    Raises:
        ValueError: If any charger count is less than 1
    """
    if not config.chargers or any(c.count < 1 for c in config.chargers):
        raise ValueError("All chargers must have count >= 1")

    random.seed(config.seed)

    # per tick arrival probability after scaling
    p_tick: list[float] = [
        min(
            1 - (1 - p * config.arrival_multiplier / 100.0) ** (1 / TICKS_PER_HOUR), 1.0
        )
        for p in _ARRIVAL_PCT_PER_HOUR
    ]

    # find DST transition days (Europe/Berlin)
    spring_forward = _last_sunday(config.year, 3)  # March
    fall_back = _last_sunday(config.year, 10)  # October

    charger_states = []
    for charger in config.chargers:
        for _ in range(charger.count):
            charger_states.append(
                {
                    "power_kw": charger.power_kw,
                    "remaining": 0.0,
                    "energy_per_tick": charger.energy_per_tick_kwh,
                }
            )

    total_energy = 0.0
    actual_max_kw = 0.0
    charging_events = []

    # statistics tracking
    events_by_day = defaultdict(
        lambda: defaultdict(lambda: {"count": 0, "total_power": 0.0})
    )
    events_by_week = defaultdict(
        lambda: defaultdict(lambda: {"count": 0, "total_power": 0.0})
    )
    events_by_month = defaultdict(
        lambda: defaultdict(lambda: {"count": 0, "total_power": 0.0})
    )
    events_by_year = defaultdict(
        lambda: defaultdict(lambda: {"count": 0, "total_power": 0.0})
    )

    start_date = datetime.date(config.year, 1, 1)
    for day in range(365):
        date = start_date + datetime.timedelta(days=day)
        if date == spring_forward:
            ticks_today = 23 * TICKS_PER_HOUR  # 92
        elif date == fall_back:
            ticks_today = 25 * TICKS_PER_HOUR  # 100
        else:
            ticks_today = 24 * TICKS_PER_HOUR  # 96

        for tick_in_day in range(ticks_today):
            hour_idx = (tick_in_day // TICKS_PER_HOUR) % 24
            p_arrival = p_tick[hour_idx]
            current_time = datetime.datetime.combine(
                date,
                datetime.time(
                    hour=hour_idx, minute=(tick_in_day % TICKS_PER_HOUR) * 15
                ),
            )

            occupied_this_tick = 0
            free_indices = []

            # serve existing sessions
            for i, charger in enumerate(charger_states):
                if charger["remaining"] > 0:
                    delivered = min(charger["energy_per_tick"], charger["remaining"])
                    charger["remaining"] -= delivered
                    total_energy += delivered
                    if charger["remaining"] < 1e-9:
                        charger["remaining"] = 0.0
                    occupied_this_tick += 1
                else:
                    free_indices.append(i)

            # new arrivals
            for i in free_indices:
                if random.random() < p_arrival:
                    km = _sample_km()
                    if km == 0:
                        continue
                    energy_need = km * config.energy_per_km
                    charger_states[i]["remaining"] = energy_need
                    delivered = min(charger_states[i]["energy_per_tick"], energy_need)
                    charger_states[i]["remaining"] -= delivered
                    total_energy += delivered

                    # record charging event
                    charger_type = charger_states[i]["power_kw"]
                    power_kw = charger_states[i]["power_kw"]
                    event = ChargingEvent(
                        charger_type=charger_type,
                        energy_kwh=energy_need,
                        start_time=current_time,
                        power_kw=power_kw,
                    )
                    charging_events.append(event)

                    # update period statistics
                    events_by_day[date][charger_type]["count"] += 1
                    events_by_day[date][charger_type]["total_power"] += power_kw

                    events_by_week[date.isocalendar()[1]][charger_type]["count"] += 1
                    events_by_week[date.isocalendar()[1]][charger_type][
                        "total_power"
                    ] += power_kw

                    events_by_month[date.month][charger_type]["count"] += 1
                    events_by_month[date.month][charger_type]["total_power"] += power_kw

                    events_by_year[date.year][charger_type]["count"] += 1
                    events_by_year[date.year][charger_type]["total_power"] += power_kw

                    if charger_states[i]["remaining"] < 1e-9:
                        charger_states[i]["remaining"] = 0.0
                    occupied_this_tick += 1

            load_kw = sum(
                charger["power_kw"]
                for i, charger in enumerate(charger_states)
                if charger["remaining"] > 0
            )
            actual_max_kw = max(actual_max_kw, load_kw)

    theoretical_max_kw = sum(
        charger.power_kw * charger.count for charger in config.chargers
    )
    concurrency_factor = (
        actual_max_kw / theoretical_max_kw if theoretical_max_kw else 0.0
    )

    def calculate_statistics(events_dict):
        result = {}
        for period, charger_stats in events_dict.items():
            total_count = sum(stats["count"] for stats in charger_stats.values())
            total_power = sum(stats["total_power"] for stats in charger_stats.values())
            result[str(period)] = {
                "total_events": total_count,
                "total_power_kw": round(total_power, 2),
            }
        return result

    events_stats = {
        "by_day": calculate_statistics(events_by_day),
        "by_week": calculate_statistics(events_by_week),
        "by_month": calculate_statistics(events_by_month),
        "by_year": calculate_statistics(events_by_year),
    }

    return {
        "total_energy_kwh": round(total_energy, 2),
        "theoretical_max_kw": theoretical_max_kw,
        "actual_max_kw": actual_max_kw,
        "concurrency_factor": round(concurrency_factor, 3),
        "total_charging_events": len(charging_events),
        "charging_events": charging_events,
        "events_statistics": events_stats,
    }
