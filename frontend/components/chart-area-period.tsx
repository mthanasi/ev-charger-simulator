"use client";

import * as React from "react";
import { Area, AreaChart, CartesianGrid, XAxis, YAxis } from "recharts";
import { usePeriodStatistics } from "@/lib/api";
import { format, parseISO, isValid } from "date-fns";

import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  ChartConfig,
  ChartContainer,
  ChartLegend,
  ChartLegendContent,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { Skeleton } from "@/components/ui/skeleton";

export const description =
  "An interactive area chart showing simulation results";

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

interface ChartDataPoint {
  date: string;
  total_events: number;
  total_power_kw: number;
}

interface ChartAreaPeriodProps {
  resultId: number;
}

export function ChartAreaPeriod({ resultId }: ChartAreaPeriodProps) {
  const [periodType, setPeriodType] = React.useState<
    "by_day" | "by_week" | "by_month"
  >("by_day");
  const { data: statistics, isLoading } = usePeriodStatistics(resultId);

  const chartData = React.useMemo(() => {
    if (!statistics || statistics.length === 0) return [];

    const filteredStats = statistics
      .filter((stat) => stat.period_type === periodType)
      .sort((a, b) => {
        if (periodType === "by_day") {
          return (
            new Date(a.period_value).getTime() -
            new Date(b.period_value).getTime()
          );
        }
        // for week and month, sort by numeric value
        return Number(a.period_value) - Number(b.period_value);
      });

    // for daily view, just return the data as is
    if (periodType === "by_day") {
      return filteredStats.map(
        (stat): ChartDataPoint => ({
          date: stat.period_value,
          total_events: stat.total_events,
          total_power_kw: stat.total_power_kw,
        })
      );
    }

    return filteredStats.map((stat): ChartDataPoint => {
      let date: string;

      if (periodType === "by_week") {
        // store the week number in the date field for proper sorting and display
        date = `Week ${stat.period_value}`;
      } else {
        // for monthly view, use the first day of the month
        const monthNumber = parseInt(stat.period_value);
        date = format(
          new Date(new Date().getFullYear(), monthNumber - 1, 1),
          "yyyy-MM-dd"
        );
      }

      return {
        date,
        total_events: stat.total_events,
        total_power_kw: stat.total_power_kw,
      };
    });
  }, [statistics, periodType]);

  const formatDate = (date: string) => {
    try {
      if (periodType === "by_week") {
        // for weekly view, just return the week number as is
        return date;
      }

      const parsedDate = parseISO(date);
      if (!isValid(parsedDate)) {
        console.warn("Invalid date:", date);
        return date;
      }

      switch (periodType) {
        case "by_day":
          return format(parsedDate, "MMM d");
        case "by_month":
          return format(parsedDate, "MMM yyyy");
        default:
          return format(parsedDate, "MMM d");
      }
    } catch (error) {
      console.error("Error formatting date:", error);
      return date;
    }
  };

  if (isLoading || !statistics || statistics.length === 0) {
    return (
      <Card className="@container/card">
        <CardHeader className="flex items-center gap-2 space-y-0 border-b py-5 sm:flex-row">
          <div className="grid flex-1 gap-1">
            <Skeleton className="h-6 w-48" />
            <Skeleton className="h-4 w-72" />
          </div>
          <CardAction>
            <Skeleton className="h-9 w-40" />
          </CardAction>
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
      </Card>
    );
  }

  return (
    <Card className="@container/card">
      <CardHeader className="flex items-center gap-2 space-y-0 border-b py-5 sm:flex-row">
        <div className="grid flex-1 gap-1">
          <CardTitle>Simulation Results</CardTitle>
          <CardDescription>
            <span className="hidden @[540px]/card:block">
              Total events and power consumption over time
            </span>
            <span className="@[540px]/card:hidden">
              Events and power over time
            </span>
          </CardDescription>
        </div>
        <CardAction>
          <ToggleGroup
            type="single"
            value={periodType}
            onValueChange={(value) =>
              value && setPeriodType(value as typeof periodType)
            }
            variant="outline"
            className="hidden *:data-[slot=toggle-group-item]:!px-4 @[767px]/card:flex"
          >
            <ToggleGroupItem value="by_day">Daily</ToggleGroupItem>
            <ToggleGroupItem value="by_week">Weekly</ToggleGroupItem>
            <ToggleGroupItem value="by_month">Monthly</ToggleGroupItem>
          </ToggleGroup>
          <Select
            value={periodType}
            onValueChange={(value) => setPeriodType(value as typeof periodType)}
          >
            <SelectTrigger
              className="flex w-40 **:data-[slot=select-value]:block **:data-[slot=select-value]:truncate @[767px]/card:hidden"
              size="sm"
              aria-label="Select period type"
            >
              <SelectValue placeholder="Select period" />
            </SelectTrigger>
            <SelectContent className="rounded-xl">
              <SelectItem value="by_day" className="rounded-lg">
                Daily
              </SelectItem>
              <SelectItem value="by_week" className="rounded-lg">
                Weekly
              </SelectItem>
              <SelectItem value="by_month" className="rounded-lg">
                Monthly
              </SelectItem>
            </SelectContent>
          </Select>
        </CardAction>
      </CardHeader>
      <CardContent className="px-2 pt-4 sm:px-6 sm:pt-6">
        <ChartContainer
          config={chartConfig}
          className="aspect-auto h-[250px] w-full"
        >
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="fillEvents" x1="0" y1="0" x2="0" y2="1">
                <stop
                  offset="5%"
                  stopColor="var(--color-total_events)"
                  stopOpacity={0.1}
                />
                <stop
                  offset="95%"
                  stopColor="var(--color-total_events)"
                  stopOpacity={0}
                />
              </linearGradient>
              <linearGradient id="fillPower" x1="0" y1="0" x2="0" y2="1">
                <stop
                  offset="5%"
                  stopColor="var(--color-total_power_kw)"
                  stopOpacity={0.1}
                />
                <stop
                  offset="95%"
                  stopColor="var(--color-total_power_kw)"
                  stopOpacity={0}
                />
              </linearGradient>
            </defs>
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="date"
              tickFormatter={formatDate}
              tickLine={false}
              tickMargin={8}
              axisLine={false}
              minTickGap={32}
            />
            <YAxis
              yAxisId="events"
              orientation="left"
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              domain={[0, (dataMax: number) => dataMax * 5]}
              scale="linear"
              tickFormatter={(value) => value.toLocaleString()}
            />
            <YAxis
              yAxisId="power"
              orientation="right"
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              domain={[0, "auto"]}
              scale="linear"
              tickFormatter={(value) => value.toLocaleString()}
            />
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent indicator="dashed" />}
            />
            <Area
              type="monotone"
              dataKey="total_events"
              stroke="var(--color-total_events)"
              fill="url(#fillEvents)"
              strokeWidth={2}
              yAxisId="events"
            />
            <Area
              type="monotone"
              dataKey="total_power_kw"
              stroke="var(--color-total_power_kw)"
              fill="url(#fillPower)"
              strokeWidth={2}
              yAxisId="power"
            />
            <ChartLegend content={<ChartLegendContent />} />
          </AreaChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}
