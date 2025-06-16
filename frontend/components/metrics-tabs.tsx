"use client";

import * as React from "react";
import { useAtom } from "jotai";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ChartAreaPeriod } from "./chart-area-period";
import { ChartChargerStats } from "./chart-charger-stats";
import { selectedConfigIdAtom, selectedResultIdAtom } from "@/lib/atoms";
import { useSimulationResults } from "@/lib/api";
import { useEffect } from "react";

export function MetricsTabs() {
  const [selectedConfigId] = useAtom(selectedConfigIdAtom);
  const [selectedResultId, setSelectedResultId] = useAtom(selectedResultIdAtom);
  const { data: results } = useSimulationResults(selectedConfigId);

  useEffect(() => {
    if (results && results.length > 0 && selectedResultId === undefined) {
      setSelectedResultId(results[0].id);
    }
  }, [results, selectedResultId, setSelectedResultId]);

  if (!selectedConfigId || !results) {
    return null;
  }

  return (
    <div className="space-y-4">
      <Tabs defaultValue="period" className="w-full">
        <div className="flex items-center justify-between">
          <TabsList>
            <TabsTrigger value="period">Period Statistics</TabsTrigger>
            <TabsTrigger value="charger">Charger Statistics</TabsTrigger>
          </TabsList>
          <Select
            value={selectedResultId?.toString()}
            onValueChange={(value) => setSelectedResultId(parseInt(value))}
          >
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Select result" />
            </SelectTrigger>
            <SelectContent>
              {results.map((result) => (
                <SelectItem key={result.id} value={result.id.toString()}>
                  Simulation {result.id}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <TabsContent value="period">
          {selectedResultId && <ChartAreaPeriod resultId={selectedResultId} />}
        </TabsContent>
        <TabsContent value="charger">
          {selectedResultId && (
            <ChartChargerStats
              configId={selectedConfigId}
              resultId={selectedResultId}
            />
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
