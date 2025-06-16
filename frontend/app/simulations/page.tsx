"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  useSimulationConfigs,
  useSimulationResults,
  useRunSimulation,
} from "@/lib/api";
import { useState } from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { format } from "date-fns";
import { Skeleton } from "@/components/ui/skeleton";

import { NoConfigFound } from "@/components/no-config-found";

export default function SimulationsPage() {
  const { data: configs, isLoading: configsLoading } = useSimulationConfigs();
  const [selectedConfigId, setSelectedConfigId] = useState<
    number | undefined
  >();
  const { data: results, isLoading: resultsLoading } =
    useSimulationResults(selectedConfigId);
  const runSimulation = useRunSimulation();

  if (configsLoading || resultsLoading) {
    return (
      <div className="flex flex-col gap-4 py-4 md:gap-6 md:py-6">
        <div className="px-4 lg:px-6">
          <Skeleton className="h-6 w-48" />
        </div>
      </div>
    );
  }

  if (configs?.length === 0) {
    return <NoConfigFound />;
  }

  return (
    <div className="flex flex-col gap-8 py-4 md:gap-10 md:py-8">
      <div className="px-4 lg:px-6">
        <Card>
          <CardHeader>
            <CardTitle>Run New Simulation</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4">
              <Select
                value={selectedConfigId?.toString()}
                onValueChange={(value) => setSelectedConfigId(parseInt(value))}
              >
                <SelectTrigger className="w-[200px]">
                  <SelectValue placeholder="Select configuration" />
                </SelectTrigger>
                <SelectContent>
                  {configs?.map((config) => (
                    <SelectItem key={config.id} value={config.id.toString()}>
                      Configuration {config.id}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button
                onClick={() =>
                  selectedConfigId && runSimulation.mutate(selectedConfigId)
                }
                disabled={!selectedConfigId}
              >
                Run Simulation
              </Button>
            </div>
          </CardContent>
        </Card>

        {results && results.length > 0 && (
          <div className="mt-8">
            <h2 className="text-xl font-semibold mb-4">Simulation Results</h2>
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>ID</TableHead>
                    <TableHead>Configuration</TableHead>
                    <TableHead>Total Energy</TableHead>
                    <TableHead>Max Power</TableHead>
                    <TableHead>Concurrency Factor</TableHead>
                    <TableHead>Total Events</TableHead>
                    <TableHead>Created</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {results?.map((result) => (
                    <TableRow key={result.id}>
                      <TableCell>{result.id}</TableCell>
                      <TableCell> Config {result.config_id}</TableCell>
                      <TableCell>
                        {result.total_energy_kwh.toFixed(2)} kWh
                      </TableCell>
                      <TableCell>
                        {result.actual_max_kw.toFixed(2)} kW
                      </TableCell>
                      <TableCell>
                        {result.concurrency_factor.toFixed(2)}
                      </TableCell>
                      <TableCell>{result.total_charging_events}</TableCell>
                      <TableCell>
                        {format(
                          new Date(result.created_at),
                          "yyyy-MM-dd HH:mm"
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
