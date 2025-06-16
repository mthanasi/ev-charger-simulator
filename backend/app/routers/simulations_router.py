from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas import (
    EventChargerStatistics,
    EventPeriodStatistics,
    SimulationConfig,
    SimulationConfigCreate,
    SimulationResult,
    SimulationResultBase,
    SimulationResultResponse,
)
from app.core.session import get_db
from app.services.simulations_service import SimulationService

router = APIRouter()


@router.post("/configs", response_model=SimulationConfig)
async def create_config(
    config: SimulationConfigCreate, session: AsyncSession = Depends(get_db)
) -> SimulationConfig:
    """Create a new simulation configuration.

    Args:
        config: Simulation configuration to create
        session: Database session

    Returns:
        Created simulation configuration
    """
    service = SimulationService(session)
    return await service.create_config(config)


@router.get("/configs/{config_id}", response_model=SimulationConfig)
async def get_config(
    config_id: int, session: AsyncSession = Depends(get_db)
) -> SimulationConfig:
    """Get a simulation configuration by ID.

    Args:
        config_id: ID of the simulation configuration
        session: Database session

    Returns:
        Simulation configuration if found

    Raises:
        HTTPException: If configuration not found
    """
    service = SimulationService(session)
    config = await service.get_config(config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return config


@router.get("/configs", response_model=List[SimulationConfig])
async def list_configs(
    session: AsyncSession = Depends(get_db),
) -> List[SimulationConfig]:
    """List all simulation configurations.

    Args:
        session: Database session

    Returns:
        List of simulation configurations
    """
    service = SimulationService(session)
    return await service.list_configs()


@router.post("/configs/{config_id}/run", response_model=SimulationResultResponse)
async def run_simulation(
    config_id: int, session: AsyncSession = Depends(get_db)
) -> SimulationResultResponse:
    """Run a simulation with the given configuration.

    Args:
        config_id: ID of the simulation configuration
        session: Database session

    Returns:
        Simulation result

    Raises:
        HTTPException: If configuration not found or simulation fails
    """
    service = SimulationService(session)
    try:
        return await service.run_simulation(config_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/results/{result_id}", response_model=SimulationResult)
async def get_result(
    result_id: int, session: AsyncSession = Depends(get_db)
) -> SimulationResult:
    """Get a simulation result by ID.

    Args:
        result_id: ID of the simulation result
        session: Database session

    Returns:
        Simulation result if found

    Raises:
        HTTPException: If result not found
    """
    service = SimulationService(session)
    result = await service.get_result(result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return result


@router.get("/results", response_model=List[SimulationResultResponse])
async def list_results(
    config_id: int | None = None,
    session: SimulationResultResponse = Depends(get_db),
) -> List[SimulationResultBase]:
    """List all simulation results.

    Args:
        config_id: Optional ID of the simulation configuration to filter by
        session: Database session

    Returns:
        List of simulation results
    """
    service = SimulationService(session)
    return await service.list_results(config_id)


@router.get("/statistics/period", response_model=List[EventPeriodStatistics])
async def get_period_statistics(
    simulation_id: int | None = None,
    session: AsyncSession = Depends(get_db),
) -> List[EventPeriodStatistics]:
    """Get period statistics for simulation results.

    Args:
        simulation_id: Optional ID of the simulation result to filter by
        session: Database session

    Returns:
        List of period statistics
    """
    service = SimulationService(session)
    return await service.get_period_statistics(simulation_id)


@router.get("/statistics/charger", response_model=List[EventChargerStatistics])
async def get_charger_statistics(
    config_id: int | None = None,
    session: AsyncSession = Depends(get_db),
) -> List[EventChargerStatistics]:
    """Get charger statistics for simulation results.

    Args:
        config_id: Optional ID of the simulation configuration to filter by
        session: Database session

    Returns:
        List of charger statistics
    """
    service = SimulationService(session)
    return await service.get_charger_statistics(config_id)


@router.delete("/configs/{config_id}")
async def delete_config(
    config_id: int,
    session: AsyncSession = Depends(get_db),
) -> None:
    """Delete a simulation configuration and all related data.

    Args:
        config_id: ID of the simulation configuration to delete
        session: Database session

    Raises:
        HTTPException: If configuration not found
    """
    service = SimulationService(session)
    try:
        await service.delete_config(config_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
