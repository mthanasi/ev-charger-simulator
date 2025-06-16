from datetime import datetime
from typing import List

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.session import Base


class ChargerConfig(Base):
    """Charger configuration model.

    Attributes:
        id: Primary key
        power_kw: Power rating in kW
        count: Number of chargers of this type
        config_id: Foreign key to simulation config
        config: Related simulation config
    """

    __tablename__ = "charger_configs"

    id: Mapped[int] = mapped_column(primary_key=True)
    power_kw: Mapped[float] = mapped_column()
    count: Mapped[int] = mapped_column()
    config_id: Mapped[int] = mapped_column(
        ForeignKey("simulation_configs.id", ondelete="CASCADE")
    )
    config: Mapped["SimulationConfig"] = relationship(back_populates="chargers")


class ChargingEvent(Base):
    """Charging event model.

    Attributes:
        id: Primary key
        charger_type: Power rating of the charger in kW
        start_time: Start time of charging
        energy_kwh: Energy consumed
        power_kw: Power rating of the charger in kW
        result_id: Foreign key to simulation result
        result: Related simulation result
    """

    __tablename__ = "charging_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    charger_type: Mapped[float] = mapped_column()
    start_time: Mapped[datetime] = mapped_column()
    energy_kwh: Mapped[float] = mapped_column()
    power_kw: Mapped[float] = mapped_column()
    result_id: Mapped[int] = mapped_column(
        ForeignKey("simulation_results.id", ondelete="CASCADE")
    )
    result: Mapped["SimulationResult"] = relationship(back_populates="charging_events")


class EventPeriodStatistics(Base):
    """Event period statistics model.

    Attributes:
        id: Primary key
        period_type: Type of period (day/week/month/year)
        period_value: Value of the period (date/week number/month/year)
        total_events: Total number of events
        total_power_kw: Total power in kW
        result_id: Foreign key to simulation result
        result: Related simulation result
    """

    __tablename__ = "event_period_statistics"

    id: Mapped[int] = mapped_column(primary_key=True)
    period_type: Mapped[str] = mapped_column(String(10))
    period_value: Mapped[str] = mapped_column(String(20))
    total_events: Mapped[int] = mapped_column()
    total_power_kw: Mapped[float] = mapped_column()
    result_id: Mapped[int] = mapped_column(
        ForeignKey("simulation_results.id", ondelete="CASCADE")
    )
    result: Mapped["SimulationResult"] = relationship(
        back_populates="event_period_statistics"
    )


class EventChargerStatistics(Base):
    """Event charger statistics model.

    Attributes:
        id: Primary key
        charger_type: Power rating of the charger in kW
        total_events: Total number of events
        total_power_kw: Total power in kW
        avg_power_kw: Average power in kW
        result_id: Foreign key to simulation result
        result: Related simulation result
    """

    __tablename__ = "event_charger_statistics"

    id: Mapped[int] = mapped_column(primary_key=True)
    charger_type: Mapped[float] = mapped_column()
    total_events: Mapped[int] = mapped_column()
    total_power_kw: Mapped[float] = mapped_column()
    avg_power_kw: Mapped[float] = mapped_column()
    result_id: Mapped[int] = mapped_column(
        ForeignKey("simulation_results.id", ondelete="CASCADE")
    )
    result: Mapped["SimulationResult"] = relationship(
        back_populates="event_charger_statistics"
    )


class SimulationConfig(Base):
    """Simulation configuration model.

    Attributes:
        id: Primary key
        arrival_multiplier: Arrival probability multiplier
        energy_per_km: Energy consumption per km
        year: Year to simulate (for DST calculations)
        seed: Random seed for reproducibility
        created_at: Creation timestamp
        chargers: List of charger configurations
        results: List of simulation results
    """

    __tablename__ = "simulation_configs"

    id: Mapped[int] = mapped_column(primary_key=True)
    arrival_multiplier: Mapped[float] = mapped_column()
    energy_per_km: Mapped[float] = mapped_column()
    year: Mapped[int] = mapped_column()
    seed: Mapped[int | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    chargers: Mapped[List[ChargerConfig]] = relationship(back_populates="config")
    results: Mapped[List["SimulationResult"]] = relationship(back_populates="config")


class SimulationResult(Base):
    """Simulation result model.

    Attributes:
        id: Primary key
        config_id: Foreign key to simulation config
        total_energy_kwh: Total energy consumed
        theoretical_max_kw: Theoretical maximum power
        actual_max_kw: Actual maximum power
        concurrency_factor: Concurrency factor
        total_charging_events: Total number of charging events
        created_at: Creation timestamp
        config: Related simulation config
        event_period_statistics: List of event period statistics
        event_charger_statistics: List of event charger statistics
        charging_events: List of charging events
    """

    __tablename__ = "simulation_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    config_id: Mapped[int] = mapped_column(
        ForeignKey("simulation_configs.id", ondelete="CASCADE")
    )
    total_energy_kwh: Mapped[float] = mapped_column()
    theoretical_max_kw: Mapped[float] = mapped_column()
    actual_max_kw: Mapped[float] = mapped_column()
    concurrency_factor: Mapped[float] = mapped_column()
    total_charging_events: Mapped[int] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    config: Mapped[SimulationConfig] = relationship(back_populates="results")
    event_period_statistics: Mapped[List[EventPeriodStatistics]] = relationship(
        back_populates="result"
    )
    event_charger_statistics: Mapped[List[EventChargerStatistics]] = relationship(
        back_populates="result"
    )
    charging_events: Mapped[List[ChargingEvent]] = relationship(back_populates="result")
