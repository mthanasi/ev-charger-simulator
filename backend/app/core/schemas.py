from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ChargerConfigBase(BaseModel):
    """Base schema for charger configuration.

    Attributes:
        power_kw: Power rating in kW
        count: Number of chargers of this type
    """

    power_kw: float = Field(..., description="Power rating in kW")
    count: int = Field(..., description="Number of chargers of this type")


class ChargerConfigCreate(ChargerConfigBase):
    """Schema for creating a charger configuration."""

    pass


class ChargerConfig(ChargerConfigBase):
    """Schema for charger configuration.

    Attributes:
        id: Primary key
        config_id: Foreign key to simulation config
    """

    id: int
    config_id: int

    model_config = ConfigDict(from_attributes=True)


class ChargerTypeStats(BaseModel):
    """Schema for charger type statistics.

    Attributes:
        count: Number of events
        total_power_kw: Total power in kW
        avg_power_kw: Average power in kW
    """

    count: int = Field(..., description="Number of events")
    total_power_kw: float = Field(..., description="Total power in kW")
    avg_power_kw: float = Field(..., description="Average power in kW")


class ChargingEventBase(BaseModel):
    """Base schema for charging event.

    Attributes:
        charger_type: Power rating of the charger in kW
        start_time: Start time of charging
        energy_kwh: Energy consumed
        power_kw: Power rating of the charger in kW
    """

    charger_type: float = Field(..., description="Power rating of the charger in kW")
    start_time: datetime = Field(..., description="Start time of charging")
    energy_kwh: float = Field(..., description="Energy consumed")
    power_kw: float = Field(..., description="Power rating of the charger in kW")


class ChargingEventCreate(ChargingEventBase):
    """Schema for creating a charging event."""

    pass


class ChargingEvent(ChargingEventBase):
    """Schema for charging event.

    Attributes:
        id: Primary key
        result_id: Foreign key to simulation result
    """

    id: int
    result_id: int

    model_config = ConfigDict(from_attributes=True)


class EventPeriodStatisticsBase(BaseModel):
    """Base schema for event period statistics.

    Attributes:
        period_type: Type of period (day/week/month/year)
        period_value: Value of the period (date/week number/month/year)
        total_events: Total number of events
        total_power_kw: Total power in kW
    """

    period_type: str = Field(..., description="Type of period (day/week/month/year)")
    period_value: str = Field(
        ..., description="Value of the period (date/week number/month/year)"
    )
    total_events: int = Field(..., description="Total number of events")
    total_power_kw: float = Field(..., description="Total power in kW")


class EventPeriodStatisticsCreate(EventPeriodStatisticsBase):
    """Schema for creating event period statistics."""

    pass


class EventPeriodStatistics(EventPeriodStatisticsBase):
    """Schema for event period statistics.

    Attributes:
        id: Primary key
        simulation_id: Foreign key to simulation result
    """

    id: int
    simulation_id: int

    model_config = ConfigDict(from_attributes=True)


class EventChargerStatisticsBase(BaseModel):
    """Base schema for event charger statistics.

    Attributes:
        charger_type: Power rating of the charger in kW
        total_events: Total number of events
        total_power_kw: Total power in kW
        avg_power_kw: Average power in kW
    """

    charger_type: float = Field(..., description="Power rating of the charger in kW")
    total_events: int = Field(..., description="Total number of events")
    total_power_kw: float = Field(..., description="Total power in kW")
    avg_power_kw: float = Field(..., description="Average power in kW")


class EventChargerStatisticsCreate(EventChargerStatisticsBase):
    """Schema for creating event charger statistics."""

    pass


class EventChargerStatistics(EventChargerStatisticsBase):
    """Schema for event charger statistics.

    Attributes:
        id: Primary key
        simulation_id: Foreign key to simulation result
    """

    id: int
    result_id: int

    model_config = ConfigDict(from_attributes=True)


class SimulationConfigBase(BaseModel):
    """Base schema for simulation configuration.

    Attributes:
        arrival_multiplier: Arrival probability multiplier
        energy_per_km: Energy consumption per km
        year: Year to simulate (for DST calculations)
        seed: Random seed for reproducibility
    """

    arrival_multiplier: float = Field(
        default=1.0, description="Arrival probability multiplier"
    )
    energy_per_km: float = Field(
        default=18, description="Energy consumption per 100 km"
    )
    year: int = Field(
        default=2023, description="Year to simulate (for DST calculations)"
    )
    seed: Optional[int] = Field(
        default=None, description="Random seed for reproducibility"
    )


class SimulationConfigCreate(SimulationConfigBase):
    """Schema for creating a simulation configuration.

    Attributes:
        chargers: List of charger configurations
    """

    chargers: List[ChargerConfigCreate] = Field(
        ..., description="List of charger configurations"
    )


class SimulationConfig(SimulationConfigBase):
    """Schema for simulation configuration.

    Attributes:
        id: Primary key
        created_at: Creation timestamp
        chargers: List of charger configurations
        results: List of simulation results
    """

    id: int
    created_at: datetime
    chargers: List[ChargerConfig] = Field(
        ..., description="List of charger configurations"
    )
    results: Optional[List["SimulationResult"]] = Field(
        default=None, description="List of simulation results"
    )

    model_config = ConfigDict(from_attributes=True)


class SimulationResultBase(BaseModel):
    """Base schema for simulation result.

    Attributes:
        total_energy_kwh: Total energy consumed in kilowatt-hours
        theoretical_max_kw: Theoretical maximum power in kilowatts
        actual_max_kw: Actual maximum power in kilowatts
        concurrency_factor: Factor representing concurrent charging
        total_charging_events: Total number of charging events
    """

    total_energy_kwh: float
    theoretical_max_kw: float
    actual_max_kw: float
    concurrency_factor: float
    total_charging_events: int


class SimulationResultResponse(SimulationResultBase):
    """Schema for simulation result response with only essential fields.

    Attributes:
        id: Unique identifier for the simulation result
        config_id: ID of the simulation configuration
        created_at: Timestamp when the result was created
    """

    id: int
    config_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SimulationResultCreate(SimulationResultBase):
    """Schema for creating a simulation result.

    Attributes:
        charging_events: List of charging events
        event_period_statistics: List of event period statistics
        event_charger_statistics: List of event charger statistics
    """

    charging_events: List[ChargingEventCreate]
    event_period_statistics: List[EventPeriodStatisticsCreate]
    event_charger_statistics: List[EventChargerStatisticsCreate]


class SimulationResult(SimulationResultBase):
    """Schema for simulation result with ID and relationships.

    Attributes:
        id: Unique identifier for the simulation result
        config_id: ID of the simulation configuration
        created_at: Timestamp when the result was created
        charging_events: List of charging events
        event_period_statistics: List of event period statistics
        event_charger_statistics: List of event charger statistics
    """

    id: int
    config_id: int
    created_at: datetime
    event_period_statistics: List[EventPeriodStatistics]
    event_charger_statistics: List[EventChargerStatistics]

    model_config = ConfigDict(from_attributes=True)


# Update forward references
SimulationConfig.model_rebuild()
SimulationResult.model_rebuild()
