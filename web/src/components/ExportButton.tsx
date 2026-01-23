"use client";

import { Button } from "@/components/ui/button";
import { getExportUrl } from "@/lib/api";

interface ExportButtonProps {
  disabled?: boolean;
}

export function ExportButton({ disabled }: ExportButtonProps) {
  const handleExport = () => {
    window.open(getExportUrl(), "_blank");
  };

  return (
    <Button variant="outline" onClick={handleExport} disabled={disabled}>
      Export CSV
    </Button>
  );
}
