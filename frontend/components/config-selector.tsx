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
import { useSimulationConfigs } from "@/lib/api";
import { selectedConfigIdAtom } from "@/lib/atoms";
import { useEffect } from "react";

export function ConfigSelector() {
  const [selectedConfigId, setSelectedConfigId] = useAtom(selectedConfigIdAtom);
  const { data: configs } = useSimulationConfigs();

  useEffect(() => {
    if (configs && configs.length > 0 && selectedConfigId === undefined) {
      setSelectedConfigId(configs[0].id);
    }
  }, [configs, selectedConfigId, setSelectedConfigId]);

  if (!configs || configs.length === 0) {
    return null;
  }

  return (
    <Select
      value={selectedConfigId?.toString()}
      onValueChange={(value) => setSelectedConfigId(parseInt(value))}
    >
      <SelectTrigger className="w-[180px]">
        <SelectValue placeholder="Select config" />
      </SelectTrigger>
      <SelectContent>
        {configs.map((config) => (
          <SelectItem key={config.id} value={config.id.toString()}>
            Config {config.id}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
