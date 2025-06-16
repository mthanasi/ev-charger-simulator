"use client";

import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { useSimulationConfigs, useCreateSimulationConfig } from "@/lib/api";
import { Skeleton } from "@/components/ui/skeleton";
import { SimulationConfigForm } from "@/components/simulation-config-form";
import { ConfigsTable } from "@/components/configs-table";

export default function ConfigurationsPage() {
  const { data: configs, isLoading } = useSimulationConfigs();
  const createConfig = useCreateSimulationConfig();

  if (isLoading) {
    return (
      <div className="flex flex-col gap-4 py-4 md:gap-6 md:py-6">
        <div className="px-4 lg:px-6">
          <Card>
            <CardHeader>
              <Skeleton className="h-6 w-48" />
            </CardHeader>
            <CardContent>
              <div className="grid gap-4">
                <div className="grid gap-2">
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-10 w-full" />
                </div>
                <div className="grid gap-2">
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-10 w-full" />
                </div>
                <div className="grid gap-2">
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-10 w-full" />
                </div>
                <Skeleton className="h-10 w-32" />
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-8 py-4 md:gap-10 md:py-8">
      <div className="px-4 lg:px-6">
        <h2 className="text-xl font-semibold mb-4">Create New Configuration</h2>
        <Card>
          <CardContent>
            <SimulationConfigForm
              onSubmit={createConfig.mutate}
              isSubmitting={createConfig.isPending}
            />
          </CardContent>
        </Card>
      </div>
      {configs && configs.length > 0 && (
        <div className="px-4 lg:px-6">
          <h2 className="text-xl font-semibold mb-4">All Configurations</h2>
          <ConfigsTable />
        </div>
      )}
    </div>
  );
}
