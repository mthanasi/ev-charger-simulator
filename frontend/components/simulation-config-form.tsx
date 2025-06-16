"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm, useFieldArray, ControllerRenderProps } from "react-hook-form";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Plus, Trash2 } from "lucide-react";
import { SimulationConfigCreate } from "@/lib/api";

const chargerSchema = z.object({
  power_kw: z.number().min(1).max(350),
  count: z.number().min(1).max(100),
});

const formSchema = z.object({
  arrival_multiplier: z.number().min(0.1).max(10),
  energy_per_km: z.number().min(1).max(100),
  year: z.number().min(2020).max(2100),
  seed: z.number().nullable(),
  chargers: z.array(chargerSchema).min(1),
});

type FormValues = z.infer<typeof formSchema>;

interface SimulationConfigFormProps {
  onSubmit: (data: SimulationConfigCreate) => void;
  isSubmitting?: boolean;
}

export function SimulationConfigForm({
  onSubmit,
  isSubmitting = false,
}: SimulationConfigFormProps) {
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      arrival_multiplier: 1.0,
      energy_per_km: 18,
      year: new Date().getFullYear(),
      seed: null,
      chargers: [{ power_kw: 11, count: 20 }],
    },
  });

  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: "chargers",
  });

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="grid gap-4">
        <FormField
          control={form.control}
          name="arrival_multiplier"
          render={({
            field,
          }: {
            field: ControllerRenderProps<FormValues, "arrival_multiplier">;
          }) => (
            <FormItem>
              <FormLabel>Arrival Multiplier</FormLabel>
              <FormControl>
                <Input
                  type="number"
                  step="0.1"
                  min="0.1"
                  max="10"
                  {...field}
                  value={field.value || ""}
                  onChange={(e) => {
                    const value =
                      e.target.value === "" ? "" : parseFloat(e.target.value);
                    field.onChange(value === "" ? 0 : value);
                  }}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="energy_per_km"
          render={({
            field,
          }: {
            field: ControllerRenderProps<FormValues, "energy_per_km">;
          }) => (
            <FormItem>
              <FormLabel>Energy per km (kWh)</FormLabel>
              <FormControl>
                <Input
                  type="number"
                  step="1"
                  min="1"
                  max="100"
                  {...field}
                  value={field.value || ""}
                  onChange={(e) => {
                    const value =
                      e.target.value === "" ? "" : parseInt(e.target.value);
                    field.onChange(value === "" ? 0 : value);
                  }}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="year"
          render={({
            field,
          }: {
            field: ControllerRenderProps<FormValues, "year">;
          }) => (
            <FormItem>
              <FormLabel>Year</FormLabel>
              <FormControl>
                <Input
                  type="number"
                  min="2020"
                  max="2100"
                  {...field}
                  value={field.value || ""}
                  onChange={(e) => {
                    const value =
                      e.target.value === "" ? "" : parseInt(e.target.value);
                    field.onChange(value === "" ? 0 : value);
                  }}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="grid gap-2">
          <div className="flex items-center justify-between">
            <FormLabel>Chargers</FormLabel>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => append({ power_kw: 50, count: 1 })}
            >
              <Plus className="h-4 w-4" />
              Add Charger
            </Button>
          </div>
          <div className="grid gap-4">
            {fields.map((field, index) => (
              <div key={field.id} className="flex items-end gap-4">
                <FormField
                  control={form.control}
                  name={`chargers.${index}.power_kw`}
                  render={({
                    field,
                  }: {
                    field: ControllerRenderProps<
                      FormValues,
                      `chargers.${number}.power_kw`
                    >;
                  }) => (
                    <FormItem className="flex-1">
                      <FormLabel>Power (kW)</FormLabel>
                      <FormControl>
                        <Input
                          type="number"
                          min="1"
                          max="350"
                          {...field}
                          value={field.value || ""}
                          onChange={(e) => {
                            const value =
                              e.target.value === ""
                                ? ""
                                : parseInt(e.target.value);
                            field.onChange(value === "" ? 0 : value);
                          }}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name={`chargers.${index}.count`}
                  render={({
                    field,
                  }: {
                    field: ControllerRenderProps<
                      FormValues,
                      `chargers.${number}.count`
                    >;
                  }) => (
                    <FormItem className="flex-1">
                      <FormLabel>Count</FormLabel>
                      <FormControl>
                        <Input
                          type="number"
                          min="1"
                          max="100"
                          {...field}
                          value={field.value || ""}
                          onChange={(e) => {
                            const value =
                              e.target.value === ""
                                ? ""
                                : parseInt(e.target.value);
                            field.onChange(value === "" ? 0 : value);
                          }}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  onClick={() => remove(index)}
                  disabled={fields.length === 1}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
        </div>

        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Creating..." : "Create Configuration"}
        </Button>
      </form>
    </Form>
  );
}
