"use client";

import * as React from "react";
import { MoonIcon, SunIcon } from "lucide-react";
import { useTheme } from "next-themes";

import { Button } from "@/components/ui/button";

export function ThemeSwitcher() {
  const { setTheme, resolvedTheme } = useTheme();

  const toggleTheme = React.useCallback(() => {
    setTheme(resolvedTheme === "dark" ? "light" : "dark");
  }, [resolvedTheme, setTheme]);

  return (
    <Button
      variant="outline"
      className="group/toggle size-8.5 px-0"
      onClick={toggleTheme}
    >
      <SunIcon className="hidden dark:block" />
      <MoonIcon className="block dark:hidden" />
      <span className="sr-only">Toggle theme</span>
    </Button>
  );
}
