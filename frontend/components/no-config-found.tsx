import Link from "next/link";

export function NoConfigFound() {
  return (
    <div className="flex flex-col gap-4 py-4 md:gap-6 md:py-6">
      <div className="px-4 lg:px-6">
        <div className="text-lg font-semibold">No configurations found.</div>
        <div className="text-sm text-muted-foreground">
          You can create a new configuration in the{" "}
          <Link href="/configurations" className="text-blue-500">
            configurations
          </Link>{" "}
          page.
        </div>
      </div>
    </div>
  );
}
