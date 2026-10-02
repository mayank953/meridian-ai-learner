import React, { useState, useEffect, useCallback, useRef } from "react";
import { getSystemStatus, type SystemStatus } from "@/lib/api";

function StatusRow({ label, value, mono, tag }: { label: string; value?: string | null; mono?: boolean; tag?: "ok" | "warn" | "error" | "info" }) {
  const tagStyles: Record<string, string> = {
    ok: "bg-success/10 text-success",
    warn: "bg-warning/10 text-warning",
    error: "bg-danger/10 text-danger",
    info: "bg-accent/10 text-accent",
  };

  return (
    <div className="flex items-start justify-between py-2.5 border-b border-border last:border-0 gap-3">
      <span className="text-xs text-muted-foreground shrink-0">{label}</span>
      {tag ? (
        <span className={`text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full ${tagStyles[tag] || ""}`}>
          {value ?? "—"}
        </span>
      ) : (
        <span className={`text-sm text-card-foreground text-right break-all ${mono ? "font-mono text-xs" : ""}`}>
          {value ?? "—"}
        </span>
      )}
    </div>
  );
}

function StatusSection({ title, icon, children }: { title: string; icon: string; children: React.ReactNode }) {
  return (
    <div className="rounded-lg border border-border bg-card overflow-hidden">
      <div className="px-5 py-3 border-b border-border bg-muted/30 flex items-center gap-2.5">
        <span className="text-base">{icon}</span>
        <span className="text-sm font-semibold font-heading text-card-foreground">{title}</span>
      </div>
      <div className="px-5 py-1">{children}</div>
    </div>
  );
}

export default function SystemStatusTab() {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const fetchStatus = useCallback(async () => {
    try {
      const data = await getSystemStatus();
      setStatus(data);
      setError(null);
    } catch (e: any) {
      setError(e.message);
      setStatus(null);
    } finally {
      setLoading(false);
      setLastUpdated(new Date().toLocaleTimeString());
    }
  }, []);

  useEffect(() => {
    fetchStatus();
    intervalRef.current = setInterval(fetchStatus, 5000);
    return () => { if (intervalRef.current) clearInterval(intervalRef.current); };
  }, [fetchStatus]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-muted-foreground animate-fade-in">
        <span className="w-8 h-8 border-3 border-border border-t-accent rounded-full animate-spin mb-3" />
        <span className="text-sm">Loading system status…</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg border border-danger/30 bg-danger/5 p-6 animate-fade-in">
        <p className="text-sm text-danger font-semibold">Backend Unreachable</p>
        <p className="text-sm text-danger mt-1">{error}</p>
      </div>
    );
  }

  const s = status!;
  const shortId = (id?: string) => id ? id.split("/").pop() : "—";

  return (
    <div className="animate-fade-in">
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-2.5">
          <span className="w-2.5 h-2.5 rounded-full bg-success shadow-[0_0_6px_hsl(var(--success))]" />
          <span className="text-sm font-semibold font-heading text-card-foreground">Meridian AI — All systems operational</span>
        </div>
        <span className="text-[11px] text-muted-foreground">Auto-refreshes every 5s · Last: {lastUpdated}</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <StatusSection title="Backend" icon="⚙️">
          <StatusRow label="Status" value={s.backend?.status} tag="ok" />
          <StatusRow label="Uptime" value={s.backend?.uptime} mono />
          <StatusRow label="Python" value={s.backend?.python_version} mono />
          <StatusRow label="Platform" value={s.backend?.platform} />
        </StatusSection>

        <StatusSection title="Google Cloud Platform" icon="☁️">
          <StatusRow label="Project ID" value={s.gcp?.project_id} mono />
          <StatusRow label="Region" value={s.gcp?.region} mono />
        </StatusSection>

        <StatusSection title="Cloud Storage (GCS)" icon="🗂️">
          <StatusRow label="Bucket" value={s.storage?.gcs_bucket} mono />
          <StatusRow label="Prefix" value={s.storage?.gcs_prefix} mono />
        </StatusSection>

        <StatusSection title="Vertex AI Vector Search" icon="🔍">
          <StatusRow label="Index ID" value={shortId(s.vector_search?.index_id)} mono />
          <StatusRow label="Endpoint ID" value={shortId(s.vector_search?.endpoint_id)} mono />
          <StatusRow label="Stream Update" value={s.vector_search?.stream_update ? "Enabled" : "Disabled"} tag={s.vector_search?.stream_update ? "ok" : "warn"} />
        </StatusSection>

        <StatusSection title="AI Models" icon="🤖">
          <StatusRow label="Embedding" value={s.models?.embedding} mono />
          <StatusRow label="LLM" value={s.models?.llm} mono />
          <StatusRow label="Framework" value={s.models?.llm_framework} />
        </StatusSection>

        <StatusSection title="Session Stats" icon="📊">
          <StatusRow label="Uploads (session)" value={String(s.ingestion?.uploads_this_session ?? 0)} tag="info" />
        </StatusSection>
      </div>
    </div>
  );
}
