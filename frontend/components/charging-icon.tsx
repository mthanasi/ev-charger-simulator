import * as React from "react";

interface ChargingIconProps extends React.SVGProps<SVGSVGElement> {
  size?: number;
}

export function ChargingIcon({
  size = 24,
  className,
  ...props
}: ChargingIconProps) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      {...props}
    >
      <rect width="14" height="20" x="5" y="2" rx="2" ry="2" />
      <path d="M12.667 8 10 12h4l-2.667 4" />
    </svg>
  );
}
