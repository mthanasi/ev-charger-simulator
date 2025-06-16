"use client";

import { SimulationStats } from "@/components/simulation-stats";
import { MetricsTabs } from "@/components/metrics-tabs";
import { useSimulationConfigs, useSimulationResults } from "@/lib/api";
import Link from "next/link";
import { NoConfigFound } from "@/components/no-config-found";
import { selectedConfigIdAtom } from "@/lib/atoms";
import { useAtom } from "jotai";

export default function Page() {
  const { data: configs } = useSimulationConfigs();
  const [selectedConfigId] = useAtom(selectedConfigIdAtom);
  const { data: results } = useSimulationResults(selectedConfigId);

  if (configs?.length === 0) {
    return <NoConfigFound />;
  }

  if (results?.length === 0)
    return (
      <div className="flex flex-col gap-4 py-4 md:gap-6 md:py-6">
        <div className="px-4 lg:px-6">
          <div className="text-lg font-semibold">No simulations found.</div>
          <div className="text-sm text-muted-foreground">
            You can create a new simulation in the{" "}
            <Link href="/simulations" className="text-blue-500">
              simulations
            </Link>{" "}
            page.
          </div>
        </div>
      </div>
    );

  return (
    <div className="flex flex-col gap-4 py-4 md:gap-6 md:py-6">
      <SimulationStats />
      <div className="px-4 lg:px-6">
        <MetricsTabs />
      </div>
    </div>
  );
}
