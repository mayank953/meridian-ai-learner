import { useState } from "react";
import { Upload, MessageSquare, ShieldCheck, Monitor } from "lucide-react";
import DocumentUploadTab from "@/components/DocumentUploadTab";
import RagQATab from "@/components/RagQATab";
import AuditTab from "@/components/AuditTab";
import SystemStatusTab from "@/components/SystemStatusTab";

const TABS = [
  
  { id: "qa", label: "RAG Q&A", icon: MessageSquare },
  { id: "audit", label: "Procurement Audit", icon: ShieldCheck },
  { id: "upload", label: "Index Documents", icon: Upload },
  { id: "status", label: "System Status", icon: Monitor },
  
] as const;

type TabId = (typeof TABS)[number]["id"];

const Index = () => {
  const [activeTab, setActiveTab] = useState<TabId>("upload");

  return (
    <div className="min-h-screen bg-background flex">
      {/* Sidebar */}
      <aside className="w-[260px] shrink-0 border-r border-border bg-card/60 backdrop-blur flex flex-col">
        {/* Logo */}
        <div className="px-5 pt-6 pb-5">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center text-base font-extrabold text-primary-foreground shrink-0 font-heading shadow-lg shadow-primary/20">
              M
            </div>
            <div>
              <h1 className="text-sm font-bold font-heading text-foreground tracking-tight leading-tight">
                Meridian AI
              </h1>
              <p className="text-[10px] text-muted-foreground leading-tight">
                Procurement Intelligence
              </p>
            </div>
          </div>
        </div>

        {/* Section label */}
        <div className="px-5 pt-2 pb-2">
          <span className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground/60">Platform</span>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 space-y-0.5">
          {TABS.map((tab) => {
            const isActive = activeTab === tab.id;
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`group w-full flex items-center gap-3.5 px-4 py-3.5 rounded-lg text-sm font-medium transition-all relative
                  ${isActive
                    ? "bg-primary/10 text-primary font-semibold"
                    : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
                  }`}
              >
                {isActive && (
                  <span className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-6 rounded-r-full bg-primary" />
                )}
                <span className={`flex items-center justify-center w-9 h-9 rounded-lg transition-colors
                  ${isActive ? "bg-primary/15" : "bg-muted/50 group-hover:bg-muted"}`}>
                  <Icon className="w-[18px] h-[18px] shrink-0" />
                </span>
                {tab.label}
              </button>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-border/50 mx-3 mb-2">
          <p className="text-[10px] text-muted-foreground/50 text-center tracking-wide">Aldermoor Industries · Hamburg (fictional demo company)</p>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <div className="max-w-6xl mx-auto px-8 py-8">
          {activeTab === "upload" && <DocumentUploadTab />}
          {activeTab === "qa" && <RagQATab />}
          {activeTab === "audit" && <AuditTab />}
          {activeTab === "status" && <SystemStatusTab />}
        </div>
      </main>
    </div>
  );
};

export default Index;
