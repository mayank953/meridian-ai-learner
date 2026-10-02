import React, { useState } from "react";
import {
  ShieldCheck,
  Play,
  FileText,
  CheckCircle,
  XCircle,
  Copy,
  Check,
  ChevronDown,
  Loader2,
  AlertTriangle,
  Activity,
} from "lucide-react";
import { runAudit } from "@/lib/api";

import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";

const DEFAULT_REQUEST = `Purchase Request — Aldermoor Industries Global Procurement:
- Vendor: Takumi Controls Europe B.V. (Netherlands)
- Item: Industrial PLC Controllers + HMI Panels (Qty: 200 units) for the Aldermoor filling line production
- Total Cost: 480,000 EUR
- Origin: JP (Japan — manufactured)
- Destination: DE (Aldermoor Industries, Hamburg, Germany)
- FX Rate quoted: 1 EUR = 163.5 JPY
- Cost Centre: Production Hamburg (Plant 1)
- Requested by: Global Procurement — Electronics & Automation Category`;

interface Phase {
  name: string;
  status: "pending" | "running" | "done" | "error";
  content: string | null;
}

export default function AuditTab() {
  const [request, setRequest] = useState(DEFAULT_REQUEST);
  const [loading, setLoading] = useState(false);
  const [phases, setPhases] = useState<Phase[]>([]);
  const [memo, setMemo] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [expandedPhase, setExpandedPhase] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const handleRun = async () => {
    if (!request.trim() || loading) return;
    setLoading(true);
    setMemo(null);
    setError(null);
    setExpandedPhase(null);
    setPhases([
      { name: "Risk & Compliance", status: "running", content: null },
      { name: "Tax & Treasury", status: "pending", content: null },
      { name: "Financial Control", status: "pending", content: null },
      { name: "CFO Synthesis", status: "pending", content: null },
    ]);

    const timer1 = setTimeout(() => {
      setPhases((p) => p.map((ph, i) => (i === 0 ? { ...ph, status: "done" } : i === 1 ? { ...ph, status: "running" } : ph)));
    }, 3000);
    const timer2 = setTimeout(() => {
      setPhases((p) => p.map((ph, i) => (i <= 1 ? { ...ph, status: "done" } : i === 2 ? { ...ph, status: "running" } : ph)));
    }, 6000);
    const timer3 = setTimeout(() => {
      setPhases((p) => p.map((ph, i) => (i <= 2 ? { ...ph, status: "done" } : i === 3 ? { ...ph, status: "running" } : ph)));
    }, 9000);

    try {
      const data = await runAudit(request);
      setPhases([
        { name: "Risk & Compliance", status: "done", content: data.risk_result },
        { name: "Tax & Treasury", status: "done", content: data.tax_result },
        { name: "Financial Control", status: "done", content: data.control_result },
        { name: "CFO Synthesis", status: "done", content: data.cfo_memo },
      ]);
      setMemo(data.cfo_memo);
      setExpandedPhase("CFO Synthesis");
    } catch (err: any) {
      setError(err.message);
      setPhases((p) => p.map((ph) => (ph.status === "running" ? { ...ph, status: "error" } : ph)));
    } finally {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (memo) {
      navigator.clipboard.writeText(memo);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const completedCount = phases.filter((p) => p.status === "done").length;
  const progressPct = phases.length > 0 ? Math.round((completedCount / phases.length) * 100) : 0;
  const allDone = phases.length > 0 && completedCount === phases.length;

  return (
    <div className="space-y-6 animate-fade-in">

      {/* ── Row 1: Input ────────────────────────────────────── */}
      <Card className="shadow-md">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-primary/20 to-accent/10 shadow-sm">
                <ShieldCheck className="h-5 w-5 text-primary" />
              </div>
              <div>
                <CardTitle className="text-lg">Procurement Audit</CardTitle>
                <CardDescription>Aldermoor Industries — Risk · Tax & Treasury · IFRS Control · CFO Audit Memorandum</CardDescription>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setRequest(DEFAULT_REQUEST);
                  setPhases([]);
                  setMemo(null);
                  setError(null);
                  setExpandedPhase(null);
                }}
              >
                Reset
              </Button>
              <Button
                size="sm"
                disabled={!request.trim() || loading}
                onClick={handleRun}
                className="shadow-sm"
              >
                {loading ? (
                  <><Loader2 className="h-4 w-4 animate-spin" /> Running…</>
                ) : (
                  <><Play className="h-4 w-4" /> Execute Audit</>
                )}
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Textarea
            className="font-mono text-sm min-h-[140px] resize-none"
            value={request}
            onChange={(e) => setRequest(e.target.value)}
            placeholder="Describe the procurement request…"
          />
        </CardContent>
      </Card>

      {/* ── Row 2: Pipeline + Output ────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6 items-stretch">

        {/* ━━━━ Left: Agent Pipeline (2 cols) ━━━━ */}
        <div className="lg:col-span-2 flex flex-col">
          <Card className={`flex flex-col flex-1 min-h-[520px] shadow-md transition-shadow duration-300 hover:shadow-lg overflow-hidden ${phases.length === 0 ? "border-dashed" : ""}`}>
            {/* Accent stripe at top */}
            <div className="h-[2px] w-full bg-gradient-to-r from-primary via-accent to-primary opacity-60" />

            <CardHeader className="pb-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-primary/15 to-accent/10 shadow-sm">
                    <Activity className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <CardTitle className="text-sm font-semibold">Agent Pipeline</CardTitle>
                    <CardDescription className="text-xs">Sequential compliance agents</CardDescription>
                  </div>
                </div>
                {phases.length > 0 && (
                  <Badge variant="secondary" className="text-[10px] font-mono tabular-nums px-2.5 py-0.5">
                    {completedCount}/{phases.length}
                  </Badge>
                )}
              </div>

              {/* Progress bar */}
              {phases.length > 0 && (
                <div className="mt-3 h-2 w-full rounded-full bg-secondary/60 overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-700 ease-out ${allDone ? "bg-gradient-to-r from-primary to-accent" : "animate-shimmer"} animate-progress-glow`}
                    style={{ width: `${progressPct}%` }}
                  />
                </div>
              )}
            </CardHeader>

            <Separator />

            <CardContent className="flex-1 pt-4">
              {phases.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full py-12 text-center text-muted-foreground">
                  <div className="flex h-14 w-14 items-center justify-center rounded-full border-2 border-dashed border-border mb-4">
                    <ShieldCheck className="h-7 w-7 opacity-25" />
                  </div>
                  <p className="text-sm font-medium">Execute an audit to see the agent pipeline status.</p>
                  <p className="text-xs text-muted-foreground/60 mt-1">Risk, Tax, and IFRS Control agents process sequentially before CFO synthesis.</p>
                </div>
              ) : (
                <div className="relative">
                  {/* Timeline vertical track */}
                  <div className="absolute left-[18px] top-3 bottom-3 w-[2px] bg-gradient-to-b from-border via-border/60 to-border rounded-full" />

                  <div className="space-y-0">
                    {phases.map((ph, i) => {
                      const isDone = ph.status === "done";
                      const isRunning = ph.status === "running";
                      const isError = ph.status === "error";
                      const canExpand = isDone && !!ph.content;
                      const isExpanded = expandedPhase === ph.name;

                      return (
                        <div key={ph.name}>
                          <button
                            type="button"
                            onClick={() => canExpand && setExpandedPhase(isExpanded ? null : ph.name)}
                            className={`w-full flex items-center gap-3 rounded-lg px-2 py-3 text-left transition-all duration-200 relative z-10
                              ${canExpand ? "hover:bg-muted/50 cursor-pointer" : "cursor-default"}
                              ${isExpanded ? "bg-muted/50" : ""}`}
                          >
                            {/* Status Circle (over the timeline track) */}
                            <div className={`flex h-[30px] w-[30px] shrink-0 items-center justify-center rounded-full border-2 bg-card transition-all duration-300
                              ${isDone    ? "border-success bg-success/10 shadow-[0_0_8px_hsl(var(--success)/0.25)]" :
                                isRunning ? "border-primary bg-primary/10 shadow-[0_0_8px_hsl(var(--primary)/0.25)]" :
                                isError   ? "border-destructive bg-destructive/10" :
                                            "border-border bg-muted"}`}>
                              {isDone   && <CheckCircle className="h-3.5 w-3.5 text-success" />}
                              {isRunning && <Loader2 className="h-3.5 w-3.5 text-primary animate-spin" />}
                              {isError  && <XCircle className="h-3.5 w-3.5 text-destructive" />}
                              {ph.status === "pending" && (
                                <span className="text-[10px] font-bold text-muted-foreground">{i + 1}</span>
                              )}
                            </div>

                            {/* Label */}
                            <div className="flex-1 min-w-0">
                              <span className={`block text-sm font-medium truncate
                                ${ph.status === "pending" ? "text-muted-foreground" : "text-card-foreground"}`}>
                                {ph.name}
                              </span>
                              {isRunning && (
                                <span className="text-[10px] font-semibold text-primary animate-pulse">Processing…</span>
                              )}
                              {isDone && (
                                <span className="text-[10px] text-success/80">Complete</span>
                              )}
                              {isError && (
                                <span className="text-[10px] text-destructive/80">Failed</span>
                              )}
                            </div>

                            {/* Expand chevron */}
                            {canExpand && (
                              <ChevronDown className={`h-4 w-4 text-muted-foreground transition-transform duration-200 shrink-0 ${isExpanded ? "rotate-180" : ""}`} />
                            )}
                          </button>

                          {/* Expanded content */}
                          {isExpanded && ph.content && (
                            <div className="ml-[42px] mr-2 mb-2 animate-fade-in">
                              <div className="max-h-[220px] overflow-y-auto rounded-lg border bg-background/80 p-4 shadow-inner">
                                <pre className="whitespace-pre-wrap font-mono text-xs leading-relaxed text-muted-foreground">
                                  {ph.content}
                                </pre>
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </CardContent>

            {/* Pipeline footer */}
            {allDone && (
              <CardFooter className="border-t pt-4 pb-4 mt-auto">
                <div className="flex w-full items-center justify-between text-[10px] font-semibold uppercase tracking-widest text-muted-foreground/50">
                  <span>4 Agents · Sequential</span>
                  <div className="flex items-center gap-1.5">
                    <span className="h-1.5 w-1.5 rounded-full bg-success animate-pulse" />
                    All Passed
                  </div>
                </div>
              </CardFooter>
            )}
          </Card>
        </div>

        {/* ━━━━ Right: CFO Memo (3 cols) ━━━━ */}
        <div className="lg:col-span-3 flex flex-col">
          <Card className="flex flex-col flex-1 h-[520px] shadow-md transition-shadow duration-300 hover:shadow-lg overflow-hidden">
            {/* Accent stripe at top */}
            <div className="h-[2px] w-full bg-gradient-to-r from-accent via-primary to-accent opacity-60" />

            <CardHeader className="pb-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-primary/15 to-accent/10 shadow-sm">
                    <FileText className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <CardTitle className="text-sm font-semibold">CFO Audit Memorandum</CardTitle>
                    <CardDescription className="text-xs">Synthesised output from all specialist agents</CardDescription>
                  </div>
                </div>
                {memo && (
                  <Button variant="outline" size="sm" onClick={handleCopy} className="shadow-sm">
                    {copied ? <><Check className="h-3.5 w-3.5" /> Copied</> : <><Copy className="h-3.5 w-3.5" /> Copy</>}
                  </Button>
                )}
              </div>
            </CardHeader>

            <Separator />

            <CardContent className="flex-1 pt-0 pb-6 flex flex-col relative w-full">
              {memo ? (
                <div className="relative flex-1 w-full mt-4">
                  <div className="absolute inset-0 rounded-lg border bg-muted/20 p-5 shadow-inner overflow-y-auto animate-slide-in-right">
                    <pre className="whitespace-pre-wrap font-mono text-[13px] leading-[1.75] text-card-foreground">
                      {memo}
                    </pre>
                  </div>
                </div>
              ) : error ? (
                <div className="flex flex-col items-center justify-center h-full py-12 text-center animate-fade-in">
                  <div className="flex h-14 w-14 items-center justify-center rounded-full bg-destructive/10 mb-4">
                    <AlertTriangle className="h-7 w-7 text-destructive" />
                  </div>
                  <p className="text-sm font-semibold text-destructive mb-1">Audit Failed</p>
                  <p className="text-sm text-muted-foreground max-w-xs">{error}</p>
                </div>
              ) : loading ? (
                <div className="flex flex-col items-center justify-center h-full py-16 text-center animate-fade-in">
                  <Loader2 className="h-10 w-10 text-primary animate-spin mb-4" />
                  <p className="text-sm font-semibold text-card-foreground">Generating Memorandum</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Specialist agents are analysing compliance, tax, and controls.
                  </p>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-full py-16 text-center">
                  <div className="flex h-14 w-14 items-center justify-center rounded-full border-2 border-dashed border-border mb-4">
                    <FileText className="h-7 w-7 text-muted-foreground/25" />
                  </div>
                  <p className="text-sm font-medium text-muted-foreground">
                    Submit a procurement request to generate the CFO Audit Memorandum.
                  </p>
                  <p className="text-xs text-muted-foreground/60 mt-1">The memorandum will appear here after all specialist agents complete.</p>
                </div>
              )}
            </CardContent>

            {memo && (
              <CardFooter className="border-t pt-4 pb-4 mt-auto">
                <div className="flex w-full items-center justify-between text-[10px] font-semibold uppercase tracking-widest text-muted-foreground/50">
                  <span>Gemini · Auto-managed tokens</span>
                  <div className="flex items-center gap-1.5">
                    <span className="h-1.5 w-1.5 rounded-full bg-success" />
                    Complete
                  </div>
                </div>
              </CardFooter>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}
