"use client";

import * as React from "react";
import { format } from "date-fns";
import { Trash2 } from "lucide-react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useSimulationConfigs, useDeleteSimulationConfig } from "@/lib/api";

export function ConfigsTable() {
  const { data: configs, isLoading } = useSimulationConfigs();
  const deleteConfig = useDeleteSimulationConfig();

  const handleDelete = async (id: number) => {
    try {
      await deleteConfig.mutateAsync(id);
      toast.success("Configuration deleted successfully");
    } catch (error: unknown) {
      console.error("Failed to delete configuration:", error);
      toast.error("Failed to delete configuration");
    }
  };

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>ID</TableHead>
            <TableHead>Arrival Multiplier</TableHead>
            <TableHead>Energy per km</TableHead>
            <TableHead>Year</TableHead>
            <TableHead>Chargers</TableHead>
            <TableHead>Created</TableHead>
            <TableHead className="w-[50px]"></TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {configs?.map((config) => (
            <TableRow key={config.id}>
              <TableCell>{config.id}</TableCell>
              <TableCell>{config.arrival_multiplier}</TableCell>
              <TableCell>{config.energy_per_km} kWh</TableCell>
              <TableCell>{config.year}</TableCell>
              <TableCell>
                <div className="flex flex-wrap gap-1">
                  {config.chargers.map((charger) => (
                    <Badge key={charger.id} variant="outline">
                      {charger.count}x {charger.power_kw}kW
                    </Badge>
                  ))}
                </div>
              </TableCell>
              <TableCell>
                {format(new Date(config.created_at), "yyyy-MM-dd HH:mm")}
              </TableCell>
              <TableCell>
                <Button
                  variant="outline"
                  size="icon"
                  className="text-inherit hover:bg-white hover:text-destructive"
                  onClick={() => handleDelete(config.id)}
                  disabled={deleteConfig.isPending}
                  aria-label="Delete configuration"
                >
                  <Trash2 className="size-4" />
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
