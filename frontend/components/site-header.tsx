"use client";

import * as React from "react";
import { usePathname } from "next/navigation";
import { ThemeSwitcher } from "@/components/theme-switcher";
import { Separator } from "@/components/ui/separator";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { ConfigSelector } from "@/components/config-selector";

export function SiteHeader() {
  const pathname = usePathname();
  const isRootPath = pathname === "/";

  const getPageTitle = () => {
    switch (pathname) {
      case "/":
        return "Dashboard";
      case "/configurations":
        return "Configurations";
      case "/simulations":
        return "Simulations";
      case "/not-found":
        return "Not Found";
      default:
        return "";
    }
  };

  return (
    <header className="flex h-(--header-height) shrink-0 items-center gap-2 border-b transition-[width,height] ease-linear group-has-data-[collapsible=icon]/sidebar-wrapper:h-(--header-height)">
      <div className="flex w-full items-center gap-1 px-4 lg:gap-2 lg:px-6">
        <SidebarTrigger className="-ml-1" />
        <Separator
          orientation="vertical"
          className="mx-2 data-[orientation=vertical]:h-4"
        />
        <h1 className="text-base font-medium">{getPageTitle()}</h1>
        <div className="ml-auto flex items-center gap-2">
          {isRootPath && <ConfigSelector />}
          <ThemeSwitcher />
        </div>
      </div>
    </header>
  );
}
