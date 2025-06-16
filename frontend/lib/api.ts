"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import axios from "axios";

// Types based on backend models
export interface ChargerConfig {
  id: number;
  power_kw: number;
  count: number;
  config_id: number;
}

export interface ChargerConfigCreate {
  power_kw: number;
  count: number;
}

export interface ChargingEvent {
  id: number;
  charger_type: number;
  start_time: string;
  energy_kwh: number;
  power_kw: number;
  result_id: number;
}

export interface EventPeriodStatistics {
  id: number;
  period_type: string;
  period_value: string;
  total_events: number;
  total_power_kw: number;
  simulation_id: number;
}

export interface EventChargerStatistics {
  charger_type: number;
  total_events: number;
  total_power_kw: number;
  result_id: string;
}

export interface SimulationConfig {
  id: number;
  arrival_multiplier: number;
  energy_per_km: number;
  year: number;
  seed: number | null;
  created_at: string;
  chargers: ChargerConfig[];
  results: SimulationResult[] | null;
}

export interface SimulationConfigCreate {
  arrival_multiplier: number;
  energy_per_km: number;
  year: number;
  seed: number | null;
  chargers: ChargerConfigCreate[];
}

export interface SimulationResult {
  id: number;
  config_id: number;
  total_energy_kwh: number;
  theoretical_max_kw: number;
  actual_max_kw: number;
  concurrency_factor: number;
  total_charging_events: number;
  created_at: string;
  charging_events: ChargingEvent[];
  event_period_statistics: EventPeriodStatistics[];
  event_charger_statistics: EventChargerStatistics[];
}

export interface SimulationResultResponse {
  id: number;
  config_id: number;
  total_energy_kwh: number;
  theoretical_max_kw: number;
  actual_max_kw: number;
  concurrency_factor: number;
  total_charging_events: number;
  created_at: string;
}

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
});

export const useSimulationConfigs = () => {
  return useQuery({
    queryKey: ["simulationConfigs"],
    queryFn: async () => {
      const { data } = await api.get<SimulationConfig[]>(
        "/api/v1/simulations/configs"
      );
      return data;
    },
  });
};

export const useSimulationConfig = (configId: number) => {
  return useQuery({
    queryKey: ["simulationConfig", configId],
    queryFn: async () => {
      const { data } = await api.get<SimulationConfig>(
        `/api/v1/simulations/configs/${configId}`
      );
      return data;
    },
  });
};

export const useSimulationResults = (configId?: number) => {
  return useQuery({
    queryKey: ["simulationResults", configId],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (configId) {
        params.append("config_id", configId.toString());
      }
      const { data } = await api.get<SimulationResultResponse[]>(
        `/api/v1/simulations/results?${params.toString()}`
      );
      return data;
    },
  });
};

export const useSimulationResult = (resultId: number) => {
  return useQuery({
    queryKey: ["simulationResult", resultId],
    queryFn: async () => {
      const { data } = await api.get<SimulationResult>(
        `/api/v1/simulations/results/${resultId}`
      );
      return data;
    },
  });
};

export const usePeriodStatistics = (simulationId?: number) => {
  return useQuery({
    queryKey: ["periodStatistics", simulationId],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (simulationId) {
        params.append("simulation_id", simulationId.toString());
      }
      const { data } = await api.get<EventPeriodStatistics[]>(
        `/api/v1/simulations/statistics/period?${params.toString()}`
      );
      return data;
    },
  });
};

export const useChargerStatistics = (configId?: number) => {
  return useQuery({
    queryKey: ["chargerStatistics", configId],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (configId) {
        params.append("config_id", configId.toString());
      }
      const { data } = await api.get<EventChargerStatistics[]>(
        `/api/v1/simulations/statistics/charger?${params.toString()}`
      );
      return data;
    },
  });
};

export const useCreateSimulationConfig = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (config: SimulationConfigCreate) => {
      const { data } = await api.post<SimulationConfig>(
        "/api/v1/simulations/configs",
        config
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["simulationConfigs"] });
    },
  });
};

export const useRunSimulation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (configId: number) => {
      const { data } = await api.post<SimulationResultResponse>(
        `/api/v1/simulations/configs/${configId}/run`
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["simulationResults"] });
      queryClient.invalidateQueries({ queryKey: ["periodStatistics"] });
      queryClient.invalidateQueries({ queryKey: ["chargerStatistics"] });
    },
  });
};

export const useDeleteSimulationConfig = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (configId: number) => {
      await api.delete(`/api/v1/simulations/configs/${configId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["simulationConfigs"] });
    },
  });
};
