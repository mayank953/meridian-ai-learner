import React, { useState } from "react";
import { Search, Send, Sparkles, MessageSquare, Clock, Trash2 } from "lucide-react";
import { askQuestion } from "@/lib/api";

const EXAMPLE_QUERIES = [
  "What is Aldermoor Industries total revenue in FY2024?",
  "What are the standard payment terms for servo motor suppliers?",
  "What EU customs duty applies to PLC controllers imported from Japan?",
  "What is the IFRS depreciation schedule for filling line equipment?",
];

interface HistoryEntry {
  query: string;
  answer: string | null;
  error: string | null;
  ts: number;
}

export default function RagQATab() {
  const [query, setQuery] = useState("");
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [retrieverType, setRetrieverType] = useState<"similarity" | "contextual" | "multiquery">("similarity");

  const handleAsk = async (q?: string) => {
    const text = (q || query).trim();
    if (!text || loading) return;
    setQuery("");
    setLoading(true);
    const entry: HistoryEntry = { query: text, answer: null, error: null, ts: Date.now() };
    setHistory((prev) => [entry, ...prev]);

    try {
      const res = await askQuestion(text, retrieverType);
      setHistory((prev) => prev.map((h) => (h.ts === entry.ts ? { ...h, answer: res.answer } : h)));
    } catch (err: any) {
      setHistory((prev) => prev.map((h) => (h.ts === entry.ts ? { ...h, error: err.message } : h)));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-6 animate-fade-in">
      {/* Top Row: Query Input & Example Queries */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Knowledge Query - 75% width */}
        <div className="lg:col-span-3 rounded-lg border border-border bg-card p-6 shadow-sm">
          <div className="flex items-center gap-2.5 mb-1">
            <Search className="w-[18px] h-[18px] text-primary" />
            <h2 className="text-base font-semibold font-heading text-card-foreground">Knowledge Query</h2>
          </div>
          <p className="text-sm text-muted-foreground mb-5">
            Ask questions against ingested Aldermoor procurement documents — supplier contracts, EU tariff schedules, IFRS annual reports, and compliance policies.
          </p>

          <div className="mb-5 space-y-2">
            <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Retrieval Strategy</label>
            <div className="flex bg-muted/30 p-1 rounded-lg border border-border">
              {[
                { id: "similarity", label: "Normal" },
                { id: "contextual", label: "Contextual Compression" },
                { id: "multiquery", label: "Multi-Query" }
              ].map(type => (
                <button
                  key={type.id}
                  onClick={() => setRetrieverType(type.id as any)}
                  className={`flex-1 text-xs font-medium py-2 rounded-md transition-all ${retrieverType === type.id ? 'bg-background shadow-sm text-foreground font-semibold border border-border/50' : 'text-muted-foreground hover:text-foreground'}`}
                >
                  {type.label}
                </button>
              ))}
            </div>
          </div>

          <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Your Question</label>
          <textarea
            className="w-full mt-2 p-3 rounded-md border border-border bg-background text-card-foreground text-sm font-body resize-vertical focus:outline-none focus:ring-2 focus:ring-ring/30 focus:border-primary transition-colors min-h-[110px] placeholder:text-muted-foreground"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleAsk(); } }}
            placeholder="e.g. What is the EU import duty rate for servo motors from Japan?"
          />
          <div className="flex items-center justify-between mt-3">
            <span className="text-xs text-muted-foreground">Enter to send · Shift+Enter for newline</span>
            <button
              className="flex items-center gap-2 px-4 py-2 rounded-md bg-primary text-primary-foreground text-sm font-semibold transition-colors hover:bg-primary/90 disabled:opacity-50"
              disabled={!query.trim() || loading}
              onClick={() => handleAsk()}
            >
              {loading ? (
                <><span className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" /> Thinking…</>
              ) : (
                <><Send className="w-4 h-4" /> Ask</>
              )}
            </button>
          </div>
        </div>

        {/* Example queries - Remaining space, vertical order */}
        <div className="lg:col-span-1 rounded-lg border border-border bg-card p-6 shadow-sm">
          <div className="flex items-center gap-2.5 mb-4">
            <Sparkles className="w-[18px] h-[18px] text-accent" />
            <h2 className="text-base font-semibold font-heading text-card-foreground">Query Assistant</h2>
          </div>
          <div className="flex flex-col gap-2">
            {EXAMPLE_QUERIES.map((eq) => (
              <button
                key={eq}
                className="flex items-center gap-2 text-left p-2.5 rounded-md border border-border text-[13px] text-muted-foreground hover:bg-muted hover:text-card-foreground transition-all group"
                onClick={() => { setQuery(eq); handleAsk(eq); }}
              >
                <MessageSquare className="w-3.5 h-3.5 shrink-0 opacity-40 group-hover:opacity-100 transition-opacity" />
                <span className="line-clamp-3">{eq}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Row: Answer History */}
      <div className="w-full">
        <div className="rounded-lg border border-border bg-card p-6 flex flex-col shadow-sm" style={{ minHeight: 300 }}>
          <div className="flex items-center justify-between mb-4 pb-4 border-b">
            <div className="flex items-center gap-2.5">
              <Clock className="w-[18px] h-[18px] text-muted-foreground" />
              <h2 className="text-base font-semibold font-heading text-card-foreground">Answers</h2>
              <span className="text-xs text-muted-foreground bg-muted px-2 py-0.5 rounded-full">{history.length} queries in this session</span>
            </div>
            {history.length > 0 && (
              <button
                className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-destructive transition-colors"
                onClick={() => setHistory([])}
              >
                <Trash2 className="w-3.5 h-3.5" /> Clear History
              </button>
            )}
          </div>

          <div className="flex-1 overflow-y-auto max-h-[600px] pr-2 custom-scrollbar">
            {history.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full py-20 text-muted-foreground">
                <Search className="w-12 h-12 mb-4 opacity-10" />
                <p className="text-sm font-medium">No queries yet</p>
                <p className="text-xs opacity-60">Your question history will appear here</p>
              </div>
            ) : (
              <div className="space-y-6">
                {history.map((h) => (
                  <div key={h.ts} className="animate-fade-in border-b border-border/50 pb-6 last:border-0 last:pb-0">
                    <div className="flex items-start gap-3 mb-4">
                      <div className="w-8 h-8 rounded-lg bg-primary/10 text-primary flex items-center justify-center shrink-0 mt-0.5">
                        <MessageSquare className="w-4 h-4" />
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-semibold text-card-foreground leading-relaxed">{h.query}</p>
                        <p className="text-[10px] text-muted-foreground mt-1 uppercase tracking-tighter">Query Time: {new Date(h.ts).toLocaleTimeString()}</p>
                      </div>
                    </div>
                    {h.answer ? (
                      <div className="ml-11 p-5 rounded-xl bg-muted/40 border border-border/50 shadow-sm relative group overflow-hidden">
                        <div className="absolute top-0 left-0 w-1 h-full bg-primary/20 group-hover:bg-primary/50 transition-colors" />
                        <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-primary/70 mb-3 ml-1">Verified Answer</p>
                        <p className="text-sm text-card-foreground leading-relaxed whitespace-pre-wrap">{h.answer}</p>
                      </div>
                    ) : h.error ? (
                      <div className="ml-11 p-4 rounded-lg bg-destructive/5 border border-destructive/20">
                        <p className="text-[10px] font-semibold uppercase tracking-wider text-destructive mb-2">Error Encountered</p>
                        <p className="text-sm text-destructive">{h.error}</p>
                      </div>
                    ) : (
                      <div className="ml-11 flex items-center gap-3 text-sm text-muted-foreground p-4 bg-muted/20 rounded-lg animate-pulse">
                        <span className="w-4 h-4 border-2 border-primary/30 border-t-primary rounded-full animate-spin" />
                        Intelligence agents are synthesising context and generating an answer…
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
