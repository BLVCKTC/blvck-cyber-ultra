import { Badge } from "@/components/ui/badge";
import type { Severity } from "@/lib/threat-data";
import { severityMeta } from "@/lib/threat-data";
import { cn } from "@/lib/utils";

export function SeverityBadge({
  severity,
}: {
  severity: Severity;
}) {

  const meta = severityMeta[severity];

  return (
    <Badge
      variant={
        severity === "critical"
          ? "destructive"
          : "outline"
      }
      className={cn(
        severity === "high" &&
          "border-chart-3/50 text-chart-3",

        severity === "warning" &&
          "border-primary/40 text-primary",

        severity === "info" &&
          "text-muted-foreground"
      )}
    >
      {meta.label}
    </Badge>
  );
}