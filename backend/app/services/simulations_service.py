from collections import defaultdict
from typing import Any, Dict, List, Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.models import (
    ChargerConfig,
    ChargingEvent,
    EventChargerStatistics,
    EventPeriodStatistics,
    SimulationConfig,
    SimulationResult,
)
from app.core.schemas import (
    ChargingEventCreate,
    EventChargerStatisticsCreate,
    EventPeriodStatisticsCreate,
    SimulationConfigCreate,
    SimulationResultCreate,
)
from packages.simulation.core import (
    Charger,
    run_simulation,
)
from packages.simulation.core import (
    SimulationConfig as SimConfig,
)


class SimulationService:
    """Service for managing EV charger simulations.

    Attributes:
        session: SQLAlchemy async session
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the service.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def create_config(self, config: SimulationConfigCreate) -> Dict[str, Any]:
        """Create a new simulation configuration.

        Args:
            config: Simulation configuration to create

        Returns:
            Created simulation configuration as a dictionary
        """
        db_config = SimulationConfig(
            arrival_multiplier=config.arrival_multiplier,
            energy_per_km=config.energy_per_km,
            year=config.year,
            seed=config.seed,
        )
        self.session.add(db_config)
        await self.session.flush()

        # Create charger configs
        for charger in config.chargers:
            db_charger = ChargerConfig(
                power_kw=charger.power_kw,
                count=charger.count,
                config_id=db_config.id,
            )
            self.session.add(db_charger)

        await self.session.commit()

        # Reload the config with relationships
        stmt = (
            select(SimulationConfig)
            .options(selectinload(SimulationConfig.chargers))
            .where(SimulationConfig.id == db_config.id)
        )
        result = await self.session.execute(stmt)
        db_config = result.scalar_one()

        # Convert to dict for response
        return {
            "id": db_config.id,
            "arrival_multiplier": db_config.arrival_multiplier,
            "energy_per_km": db_config.energy_per_km,
            "year": db_config.year,
            "seed": db_config.seed,
            "created_at": db_config.created_at,
            "chargers": [
                {
                    "id": c.id,
                    "power_kw": c.power_kw,
                    "count": c.count,
                    "config_id": c.config_id,
                }
                for c in db_config.chargers
            ],
            "results": [],
        }

    async def get_config(self, config_id: int) -> Optional[Dict[str, Any]]:
        """Get a simulation configuration by ID.

        Args:
            config_id: ID of the simulation configuration

        Returns:
            Simulation configuration as a dictionary if found, None otherwise
        """
        stmt = (
            select(SimulationConfig)
            .options(selectinload(SimulationConfig.chargers))
            .where(SimulationConfig.id == config_id)
        )
        result = await self.session.execute(stmt)
        db_config = result.scalar_one_or_none()

        if not db_config:
            return None

        return {
            "id": db_config.id,
            "arrival_multiplier": db_config.arrival_multiplier,
            "energy_per_km": db_config.energy_per_km,
            "year": db_config.year,
            "seed": db_config.seed,
            "created_at": db_config.created_at,
            "chargers": [
                {
                    "id": c.id,
                    "power_kw": c.power_kw,
                    "count": c.count,
                    "config_id": c.config_id,
                }
                for c in db_config.chargers
            ],
            "results": [],
        }

    async def list_configs(self) -> List[Dict[str, Any]]:
        """List all simulation configurations.

        Returns:
            List of simulation configurations as dictionaries
        """
        stmt = select(SimulationConfig).options(selectinload(SimulationConfig.chargers))
        result = await self.session.execute(stmt)
        configs = result.scalars().all()

        return [
            {
                "id": config.id,
                "arrival_multiplier": config.arrival_multiplier,
                "energy_per_km": config.energy_per_km,
                "year": config.year,
                "seed": config.seed,
                "created_at": config.created_at,
                "chargers": [
                    {
                        "id": c.id,
                        "power_kw": c.power_kw,
                        "count": c.count,
                        "config_id": c.config_id,
                    }
                    for c in config.chargers
                ],
                "results": [],
            }
            for config in configs
        ]

    async def create_result(
        self, config_id: int, result: SimulationResultCreate
    ) -> Dict[str, Any]:
        """Create a new simulation result.

        Args:
            config_id: ID of the simulation configuration
            result: Simulation result to create

        Returns:
            Created simulation result as a dictionary
        """
        db_result = SimulationResult(
            config_id=config_id,
            total_energy_kwh=result.total_energy_kwh,
            theoretical_max_kw=result.theoretical_max_kw,
            actual_max_kw=result.actual_max_kw,
            concurrency_factor=result.concurrency_factor,
            total_charging_events=result.total_charging_events,
        )
        self.session.add(db_result)
        await self.session.flush()

        for event in result.charging_events:
            db_event = ChargingEvent(
                charger_type=event.charger_type,
                start_time=event.start_time,
                energy_kwh=event.energy_kwh,
                power_kw=event.power_kw,
                result_id=db_result.id,
            )
            self.session.add(db_event)

        for stat in result.event_period_statistics:
            db_stat = EventPeriodStatistics(
                period_type=stat.period_type,
                period_value=stat.period_value,
                total_events=stat.total_events,
                total_power_kw=stat.total_power_kw,
                result_id=db_result.id,
            )
            self.session.add(db_stat)

        for stat in result.event_charger_statistics:
            db_stat = EventChargerStatistics(
                charger_type=stat.charger_type,
                total_events=stat.total_events,
                total_power_kw=stat.total_power_kw,
                avg_power_kw=stat.avg_power_kw,
                result_id=db_result.id,
            )
            self.session.add(db_stat)

        await self.session.commit()

        stmt = (
            select(SimulationResult)
            .options(
                selectinload(SimulationResult.charging_events),
                selectinload(SimulationResult.event_period_statistics),
                selectinload(SimulationResult.event_charger_statistics),
            )
            .where(SimulationResult.id == db_result.id)
        )
        result = await self.session.execute(stmt)
        db_result = result.scalar_one()

        return {
            "id": db_result.id,
            "config_id": db_result.config_id,
            "total_energy_kwh": db_result.total_energy_kwh,
            "theoretical_max_kw": db_result.theoretical_max_kw,
            "actual_max_kw": db_result.actual_max_kw,
            "concurrency_factor": db_result.concurrency_factor,
            "total_charging_events": db_result.total_charging_events,
            "created_at": db_result.created_at,
            "charging_events": [
                {
                    "id": e.id,
                    "charger_type": e.charger_type,
                    "start_time": e.start_time,
                    "energy_kwh": e.energy_kwh,
                    "power_kw": e.power_kw,
                    "result_id": e.result_id,
                }
                for e in db_result.charging_events
            ],
            "event_period_statistics": [
                {
                    "id": s.id,
                    "period_type": s.period_type,
                    "period_value": s.period_value,
                    "total_events": s.total_events,
                    "total_power_kw": s.total_power_kw,
                    "result_id": s.result_id,
                }
                for s in db_result.event_period_statistics
            ],
            "event_charger_statistics": [
                {
                    "id": s.id,
                    "charger_type": s.charger_type,
                    "total_events": s.total_events,
                    "total_power_kw": s.total_power_kw,
                    "avg_power_kw": s.avg_power_kw,
                    "result_id": s.result_id,
                }
                for s in db_result.event_charger_statistics
            ],
        }

    async def get_result(self, result_id: int) -> Optional[Dict[str, Any]]:
        """Get a simulation result by ID.

        Args:
            result_id: ID of the simulation result

        Returns:
            Simulation result as a dictionary if found, None otherwise
        """
        stmt = (
            select(SimulationResult)
            .options(
                selectinload(SimulationResult.charging_events),
                selectinload(SimulationResult.event_period_statistics),
                selectinload(SimulationResult.event_charger_statistics),
            )
            .where(SimulationResult.id == result_id)
        )
        result = await self.session.execute(stmt)
        db_result = result.scalar_one_or_none()

        if not db_result:
            return None

        return {
            "id": db_result.id,
            "config_id": db_result.config_id,
            "total_energy_kwh": db_result.total_energy_kwh,
            "theoretical_max_kw": db_result.theoretical_max_kw,
            "actual_max_kw": db_result.actual_max_kw,
            "concurrency_factor": db_result.concurrency_factor,
            "total_charging_events": db_result.total_charging_events,
            "created_at": db_result.created_at,
            "charging_events": [
                {
                    "id": e.id,
                    "charger_type": e.charger_type,
                    "start_time": e.start_time,
                    "energy_kwh": e.energy_kwh,
                    "power_kw": e.power_kw,
                    "result_id": e.result_id,
                }
                for e in db_result.charging_events
            ],
            "event_period_statistics": [
                {
                    "id": s.id,
                    "period_type": s.period_type,
                    "period_value": s.period_value,
                    "total_events": s.total_events,
                    "total_power_kw": s.total_power_kw,
                    "result_id": s.result_id,
                }
                for s in db_result.event_period_statistics
            ],
            "event_charger_statistics": [
                {
                    "id": s.id,
                    "charger_type": s.charger_type,
                    "total_events": s.total_events,
                    "total_power_kw": s.total_power_kw,
                    "avg_power_kw": s.avg_power_kw,
                    "result_id": s.result_id,
                }
                for s in db_result.event_charger_statistics
            ],
        }

    async def list_results(self, config_id: int | None = None) -> List[Dict[str, Any]]:
        """List all simulation results.

        Args:
            config_id: Optional ID of the simulation configuration to filter by

        Returns:
            List of simulation results as dictionaries
        """
        stmt = select(SimulationResult)

        if config_id is not None:
            stmt = stmt.where(SimulationResult.config_id == config_id)

        result = await self.session.execute(stmt)
        results = result.scalars().all()

        return [
            {
                "id": r.id,
                "config_id": r.config_id,
                "total_energy_kwh": r.total_energy_kwh,
                "theoretical_max_kw": r.theoretical_max_kw,
                "actual_max_kw": r.actual_max_kw,
                "concurrency_factor": r.concurrency_factor,
                "total_charging_events": r.total_charging_events,
                "created_at": r.created_at,
            }
            for r in results
        ]

    async def get_period_statistics(
        self, simulation_id: int | None = None
    ) -> List[Dict[str, Any]]:
        """Get period statistics for simulation results.

        Args:
            simulation_id: Optional ID of the simulation result to filter by

        Returns:
            List of period statistics as dictionaries
        """
        stmt = select(EventPeriodStatistics).options(
            selectinload(EventPeriodStatistics.result)
        )

        if simulation_id is not None:
            stmt = stmt.where(EventPeriodStatistics.result_id == simulation_id)

        result = await self.session.execute(stmt)
        stats = result.scalars().all()

        return [
            {
                "id": s.id,
                "period_type": s.period_type,
                "period_value": s.period_value,
                "total_events": s.total_events,
                "total_power_kw": s.total_power_kw,
                "simulation_id": s.result_id,
                "config_id": s.result.config_id,
            }
            for s in stats
        ]

    async def get_charger_statistics(
        self, config_id: int | None = None
    ) -> List[EventChargerStatistics]:
        """Get charger statistics for simulation results.

        Args:
            config_id: Optional ID of the simulation configuration to filter by

        Returns:
            List of charger statistics
        """
        stmt = (
            select(EventChargerStatistics)
            .join(SimulationResult)
            .options(selectinload(EventChargerStatistics.result))
            .order_by(
                EventChargerStatistics.charger_type, EventChargerStatistics.result_id
            )
        )

        if config_id is not None:
            stmt = stmt.where(SimulationResult.config_id == config_id)

        result = await self.session.execute(stmt)
        stats = result.scalars().all()

        return [
            EventChargerStatistics(
                id=s.id,
                result_id=s.result_id,
                charger_type=s.charger_type,
                total_events=s.total_events,
                total_power_kw=s.total_power_kw,
                avg_power_kw=s.avg_power_kw,
            )
            for s in stats
        ]

    async def run_simulation(self, config_id: int) -> Dict[str, Any]:
        """Run a simulation with the given configuration.

        Args:
            config_id: ID of the simulation configuration

        Returns:
            Created simulation result as a dictionary with only essential data
        """
        # Get config
        config = await self.get_config(config_id)
        if not config:
            raise ValueError(f"Simulation config {config_id} not found")

        # Convert config to simulation format
        chargers = [
            Charger(power_kw=c["power_kw"], count=c["count"])
            for c in config["chargers"]
        ]
        sim_config = SimConfig(
            chargers=chargers,
            arrival_multiplier=config["arrival_multiplier"],
            energy_per_km=config["energy_per_km"] / 100,
            year=config["year"],
            seed=config["seed"],
        )

        sim_result = run_simulation(sim_config)

        charger_type_stats = defaultdict(
            lambda: {"count": 0, "total_power_kw": 0.0, "avg_power_kw": 0.0}
        )
        for event in sim_result["charging_events"]:
            charger_type = str(event.charger_type)
            charger_type_stats[charger_type]["count"] += 1
            charger_type_stats[charger_type]["total_power_kw"] += event.power_kw

        for stats in charger_type_stats.values():
            if stats["count"] > 0:
                stats["avg_power_kw"] = stats["total_power_kw"] / stats["count"]

        result = SimulationResultCreate(
            total_energy_kwh=sim_result["total_energy_kwh"],
            theoretical_max_kw=sim_result["theoretical_max_kw"],
            actual_max_kw=sim_result["actual_max_kw"],
            concurrency_factor=sim_result["concurrency_factor"],
            total_charging_events=sim_result["total_charging_events"],
            charging_events=[
                ChargingEventCreate(
                    charger_type=event.charger_type,
                    start_time=event.start_time,
                    energy_kwh=event.energy_kwh,
                    power_kw=event.power_kw,
                )
                for event in sim_result["charging_events"]
            ],
            event_period_statistics=[
                EventPeriodStatisticsCreate(
                    period_type=period_type,
                    period_value=str(period_value),
                    total_events=stats["total_events"],
                    total_power_kw=stats["total_power_kw"],
                )
                for period_type, periods in sim_result["events_statistics"].items()
                for period_value, stats in periods.items()
            ],
            event_charger_statistics=[
                EventChargerStatisticsCreate(
                    charger_type=float(charger_type),
                    total_events=stats["count"],
                    total_power_kw=stats["total_power_kw"],
                    avg_power_kw=stats["avg_power_kw"],
                )
                for charger_type, stats in charger_type_stats.items()
            ],
        )

        db_result = await self.create_result(config_id, result)

        return {
            "id": db_result["id"],
            "config_id": db_result["config_id"],
            "total_energy_kwh": db_result["total_energy_kwh"],
            "theoretical_max_kw": db_result["theoretical_max_kw"],
            "actual_max_kw": db_result["actual_max_kw"],
            "concurrency_factor": db_result["concurrency_factor"],
            "total_charging_events": db_result["total_charging_events"],
            "created_at": db_result["created_at"],
        }

    async def delete_config(self, config_id: int) -> None:
        """Delete a simulation configuration and all related data.

        Args:
            config_id: ID of the simulation configuration to delete

        Raises:
            ValueError: If configuration not found
        """

        stmt = delete(ChargerConfig).where(ChargerConfig.config_id == config_id)
        await self.session.execute(stmt)

        stmt = delete(SimulationConfig).where(SimulationConfig.id == config_id)
        result = await self.session.execute(stmt)

        if result.rowcount == 0:
            raise ValueError(f"Simulation config {config_id} not found")

        await self.session.commit()
