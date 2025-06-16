"use client";

import { TrendingDown, TrendingUp } from "lucide-react";
import { useAtom } from "jotai";
import { useSimulationResults } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Card,
  CardAction,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { selectedConfigIdAtom } from "@/lib/atoms";

export function SimulationStats() {
  const [selectedConfigId] = useAtom(selectedConfigIdAtom);
  const { data: results, isLoading } = useSimulationResults(selectedConfigId);

  if (isLoading || !results || results.length === 0) {
    return (
      <div className="*:data-[slot=card]:from-primary/5 *:data-[slot=card]:to-card dark:*:data-[slot=card]:bg-card grid grid-cols-1 gap-4 px-4 *:data-[slot=card]:bg-gradient-to-t *:data-[slot=card]:shadow-xs lg:px-6 @xl/main:grid-cols-2 @5xl/main:grid-cols-4">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i} className="@container/card">
            <CardHeader>
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-8 w-32 mt-2" />
              <CardAction>
                <Skeleton className="h-6 w-16" />
              </CardAction>
            </CardHeader>
            <CardFooter className="flex-col items-start gap-1.5">
              <Skeleton className="h-4 w-48" />
              <Skeleton className="h-4 w-32" />
            </CardFooter>
          </Card>
        ))}
      </div>
    );
  }

  const sortedResults = [...results].sort(
    (a, b) =>
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );
  const latestResult = sortedResults[0];
  const previousResult = sortedResults[1];

  const calculateDifference = (
    current: number,
    previous: number | undefined
  ) => {
    if (!previous) return { value: 0, isPositive: true };
    const diff = ((current - previous) / previous) * 100;
    return {
      value: Math.abs(diff).toFixed(1),
      isPositive: diff >= 0,
    };
  };

  const totalEnergyDiff = calculateDifference(
    latestResult.total_energy_kwh,
    previousResult?.total_energy_kwh
  );

  const actualMaxDiff = calculateDifference(
    latestResult.actual_max_kw,
    previousResult?.actual_max_kw
  );

  const concurrencyDiff = calculateDifference(
    latestResult.concurrency_factor,
    previousResult?.concurrency_factor
  );

  const eventsDiff = calculateDifference(
    latestResult.total_charging_events,
    previousResult?.total_charging_events
  );

  return (
    <div className="*:data-[slot=card]:from-primary/5 *:data-[slot=card]:to-card dark:*:data-[slot=card]:bg-card grid grid-cols-1 gap-4 px-4 *:data-[slot=card]:bg-gradient-to-t *:data-[slot=card]:shadow-xs lg:px-6 @xl/main:grid-cols-2 @5xl/main:grid-cols-4">
      <Card className="@container/card">
        <CardHeader>
          <CardDescription>Total Energy</CardDescription>
          <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
            {latestResult.total_energy_kwh.toFixed(1)} kWh
          </CardTitle>
          <CardAction>
            <Badge variant="outline">
              {totalEnergyDiff.isPositive ? (
                <TrendingUp className="size-4" />
              ) : (
                <TrendingDown className="size-4" />
              )}
              {totalEnergyDiff.value}%
            </Badge>
          </CardAction>
        </CardHeader>
        <CardFooter className="flex-col items-start gap-1.5 text-sm">
          <div className="line-clamp-1 flex gap-2 font-medium">
            {totalEnergyDiff.isPositive ? "Increased" : "Decreased"} from
            previous simulation
          </div>
          <div className="text-muted-foreground">
            Total energy delivered to vehicles
          </div>
        </CardFooter>
      </Card>

      <Card className="@container/card">
        <CardHeader>
          <CardDescription>Peak Power</CardDescription>
          <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
            {latestResult.actual_max_kw.toFixed(1)} kW
          </CardTitle>
          <CardAction>
            <Badge variant="outline">
              {actualMaxDiff.isPositive ? (
                <TrendingUp className="size-4" />
              ) : (
                <TrendingDown className="size-4" />
              )}
              {actualMaxDiff.value}%
            </Badge>
          </CardAction>
        </CardHeader>
        <CardFooter className="flex-col items-start gap-1.5 text-sm">
          <div className="line-clamp-1 flex gap-2 font-medium">
            {actualMaxDiff.isPositive ? "Higher" : "Lower"} peak power demand
          </div>
          <div className="text-muted-foreground">
            Maximum power drawn from grid
          </div>
        </CardFooter>
      </Card>

      <Card className="@container/card">
        <CardHeader>
          <CardDescription>Concurrency Factor</CardDescription>
          <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
            {latestResult.concurrency_factor.toFixed(2)}
          </CardTitle>
          <CardAction>
            <Badge variant="outline">
              {concurrencyDiff.isPositive ? (
                <TrendingUp className="size-4" />
              ) : (
                <TrendingDown className="size-4" />
              )}
              {concurrencyDiff.value}%
            </Badge>
          </CardAction>
        </CardHeader>
        <CardFooter className="flex-col items-start gap-1.5 text-sm">
          <div className="line-clamp-1 flex gap-2 font-medium">
            {concurrencyDiff.isPositive ? "Improved" : "Reduced"} charger
            utilization
          </div>
          <div className="text-muted-foreground">
            Ratio of actual to theoretical max power
          </div>
        </CardFooter>
      </Card>

      <Card className="@container/card">
        <CardHeader>
          <CardDescription>Total Events</CardDescription>
          <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
            {latestResult.total_charging_events}
          </CardTitle>
          <CardAction>
            <Badge variant="outline">
              {eventsDiff.isPositive ? (
                <TrendingUp className="size-4" />
              ) : (
                <TrendingDown className="size-4" />
              )}
              {eventsDiff.value}%
            </Badge>
          </CardAction>
        </CardHeader>
        <CardFooter className="flex-col items-start gap-1.5 text-sm">
          <div className="line-clamp-1 flex gap-2 font-medium">
            {eventsDiff.isPositive ? "More" : "Fewer"} charging sessions
          </div>
          <div className="text-muted-foreground">
            Total number of charging events
          </div>
        </CardFooter>
      </Card>
    </div>
  );
}
