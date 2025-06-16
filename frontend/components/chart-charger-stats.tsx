"use client";

import { TrendingUp } from "lucide-react";
import { Bar, BarChart, CartesianGrid, XAxis } from "recharts";
import { useChargerStatistics } from "@/lib/api";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  ChartLegend,
  ChartLegendContent,
} from "@/components/ui/chart";
import { Skeleton } from "@/components/ui/skeleton";

const chartConfig = {
  total_events: {
    label: "Total Events",
    color: "var(--chart-1)",
  },
  total_power_kw: {
    label: "Total Power (kW)",
    color: "var(--primary)",
  },
} satisfies ChartConfig;

interface ChartChargerStatsProps {
  configId: number;
  resultId: number;
}

export function ChartChargerStats({
  configId,
  resultId,
}: ChartChargerStatsProps) {
  const { data: stats, isLoading } = useChargerStatistics(configId);

  if (isLoading || !stats || stats.length === 0) {
    return (
      <Card className="@container/card">
        <CardHeader className="flex items-center gap-2 space-y-0 border-b py-5 sm:flex-row">
          <div className="grid flex-1 gap-1">
            <Skeleton className="h-6 w-48" />
            <Skeleton className="h-4 w-72" />
          </div>
        </CardHeader>
        <CardContent className="px-2 pt-4 sm:px-6 sm:pt-6">
          <div className="flex h-[250px] w-full flex-col gap-4">
            <div className="flex items-center justify-between">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-4 w-32" />
            </div>
            <Skeleton className="h-[200px] w-full" />
          </div>
        </CardContent>
        <CardFooter className="flex-col items-start gap-2 text-sm">
          <Skeleton className="h-4 w-48" />
          <Skeleton className="h-4 w-72" />
        </CardFooter>
      </Card>
    );
  }

  const filteredStats = stats.filter(
    (stat) => stat.result_id.toString() === resultId.toString()
  );

  const chartData = filteredStats.map((stat) => ({
    name: `${stat.charger_type}kW`,
    total_events: stat.total_events,
    total_power_kw: stat.total_power_kw,
  }));

  const totalPower = filteredStats.reduce(
    (sum, stat) => sum + stat.total_power_kw,
    0
  );
  const totalEvents = filteredStats.reduce(
    (sum, stat) => sum + stat.total_events,
    0
  );

  return (
    <Card className="@container/card">
      <CardHeader className="flex items-center gap-2 space-y-0 border-b py-5 sm:flex-row">
        <div className="grid flex-1 gap-1">
          <CardTitle>Charger Statistics</CardTitle>
          <CardDescription>
            <span className="hidden @[540px]/card:block">
              Total events and power consumption by charger type
            </span>
            <span className="@[540px]/card:hidden">
              Events and power by charger
            </span>
          </CardDescription>
        </div>
      </CardHeader>
      <CardContent className="px-2 pt-4 sm:px-6 sm:pt-6">
        <ChartContainer
          config={chartConfig}
          className="aspect-auto h-[250px] w-full"
        >
          <BarChart data={chartData}>
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="name"
              tickLine={false}
              tickMargin={8}
              axisLine={false}
              minTickGap={32}
            />
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent indicator="dashed" />}
            />
            <Bar
              dataKey="total_events"
              fill="var(--color-total_events)"
              opacity={0.75}
              radius={4}
            />
            <Bar
              dataKey="total_power_kw"
              fill="var(--color-total_power_kw)"
              opacity={0.75}
              radius={4}
            />
            <ChartLegend content={<ChartLegendContent />} />
          </BarChart>
        </ChartContainer>
      </CardContent>
      <CardFooter className="flex-col items-start gap-2 text-sm">
        <div className="flex gap-2 leading-none font-medium">
          Total Power: {totalPower.toLocaleString()} kW{" "}
          <TrendingUp className="h-4 w-4" />
        </div>
        <div className="text-muted-foreground leading-none">
          {totalEvents.toLocaleString()} total charging events across{" "}
          {filteredStats.length} charger types
        </div>
      </CardFooter>
    </Card>
  );
}
