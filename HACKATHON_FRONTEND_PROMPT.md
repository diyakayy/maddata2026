# TAM Hackathon — FRONTEND PROMPT

Copy everything below the line into Claude Code. This builds the **frontend only**. A teammate is building the backend separately — the API contract below is the source of truth for integration.

---

Build the complete frontend for **TAM** (Transaction Analysis Machine) — an AI-powered Financial Due Diligence platform for M&A transactions. This is a hackathon project. The frontend should look polished, professional, and impressive for a demo. It connects to a FastAPI backend running at `http://localhost:8000`.

## Tech Stack

- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript (strict)
- **Styling:** Tailwind CSS
- **Components:** shadcn/ui (install all needed components)
- **Icons:** Lucide React
- **Charts:** Recharts (for DCF projections and ratio visualizations)
- **State:** React hooks + polling (no TanStack Query needed — keep it simple)
- **PDF viewer:** `<iframe>` or `<object>` tag pointing at backend PDF URL

## How to Run

```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

## Project Structure

```
frontend/
├── package.json
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
├── src/
│   ├── app/
│   │   ├── layout.tsx              # Root layout: sidebar + main content area
│   │   ├── page.tsx                # Dashboard
│   │   ├── globals.css             # Tailwind base + custom styles
│   │   ├── deals/
│   │   │   ├── page.tsx            # Deals list
│   │   │   └── [id]/
│   │   │       └── page.tsx        # Deal detail (tabbed)
│   │   └── upload/
│   │       └── page.tsx            # New deal + file upload
│   ├── components/
│   │   ├── layout/
│   │   │   └── sidebar.tsx         # Dark sidebar navigation
│   │   ├── dashboard/
│   │   │   ├── stats-cards.tsx     # Top-level metric cards
│   │   │   └── recent-deals.tsx    # Recent deals table
│   │   ├── upload/
│   │   │   └── file-dropzone.tsx   # Drag-and-drop file upload
│   │   ├── analysis/
│   │   │   ├── overview-tab.tsx    # Overview: summary + key metrics
│   │   │   ├── qoe-tab.tsx         # Quality of Earnings
│   │   │   ├── financials-tab.tsx  # Working Capital + Ratios
│   │   │   ├── dcf-tab.tsx         # DCF Valuation
│   │   │   ├── red-flags-tab.tsx   # Red Flags + Anomalies
│   │   │   └── insights-tab.tsx    # AI Insights
│   │   ├── chat/
│   │   │   └── chat-panel.tsx      # RAG chatbot panel
│   │   ├── reports/
│   │   │   └── report-panel.tsx    # Report generation + download
│   │   └── ui/                     # shadcn components (auto-generated)
│   ├── lib/
│   │   ├── api.ts                  # API client — all backend calls
│   │   ├── types.ts                # TypeScript interfaces
│   │   └── utils.ts                # Formatters, helpers
│   └── hooks/
│       └── use-polling.ts          # Reusable polling hook
```

## API Client (`lib/api.ts`)

The backend runs at `http://localhost:8000`. Create a typed API client:

```typescript
const API_BASE = "http://localhost:8000/api";

// --- Helper ---
async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) throw new Error(`API error: ${res.status} ${res.statusText}`);
  return res.json();
}

// --- Deals ---
export async function createDeal(data: {
  name: string; target_company: string; industry?: string; deal_size?: number;
}): Promise<Deal> {
  return fetchJSON("/deals", { method: "POST", body: JSON.stringify(data) });
}

export async function getDeals(): Promise<{ deals: Deal[] }> {
  return fetchJSON("/deals");
}

export async function getDeal(id: number): Promise<DealDetail> {
  return fetchJSON(`/deals/${id}`);
}

export async function deleteDeal(id: number): Promise<void> {
  return fetchJSON(`/deals/${id}`, { method: "DELETE" });
}

// --- Documents ---
export async function uploadDocuments(dealId: number, files: File[]): Promise<{ documents: Document[] }> {
  const formData = new FormData();
  files.forEach((f) => formData.append("files", f));
  const res = await fetch(`${API_BASE}/deals/${dealId}/documents`, {
    method: "POST",
    body: formData,  // No Content-Type header — browser sets multipart boundary
  });
  if (!res.ok) throw new Error("Upload failed");
  return res.json();
}

export async function getDocuments(dealId: number): Promise<{ documents: Document[] }> {
  return fetchJSON(`/deals/${dealId}/documents`);
}

// --- Analysis ---
export async function triggerAnalysis(dealId: number): Promise<{ status: string }> {
  return fetchJSON(`/deals/${dealId}/analyze`, { method: "POST" });
}

export async function getAnalyses(dealId: number): Promise<{ analyses: Analysis[] }> {
  return fetchJSON(`/deals/${dealId}/analysis`);
}

export async function getAnalysis(dealId: number, type: string): Promise<Analysis> {
  return fetchJSON(`/deals/${dealId}/analysis/${type}`);
}

// --- Chat ---
export async function sendChatMessage(dealId: number, message: string): Promise<ChatMessage> {
  return fetchJSON(`/deals/${dealId}/chat`, { method: "POST", body: JSON.stringify({ message }) });
}

export async function getChatHistory(dealId: number): Promise<{ messages: ChatMessage[] }> {
  return fetchJSON(`/deals/${dealId}/chat`);
}

export async function clearChat(dealId: number): Promise<void> {
  return fetchJSON(`/deals/${dealId}/chat`, { method: "DELETE" });
}

// --- Reports ---
export async function generateReport(dealId: number, type: "iar" | "dcf" | "red_flag"): Promise<{ report_id: number }> {
  return fetchJSON(`/deals/${dealId}/reports/${type}`, { method: "POST" });
}

export async function getReports(dealId: number): Promise<{ reports: Report[] }> {
  return fetchJSON(`/deals/${dealId}/reports`);
}

export function getReportDownloadUrl(reportId: number): string {
  return `${API_BASE}/reports/${reportId}/download`;
}

export async function getReportStatus(dealId: number, type: string): Promise<{ status: string }> {
  return fetchJSON(`/deals/${dealId}/reports/${type}/status`);
}
```

## TypeScript Types (`lib/types.ts`)

```typescript
export interface Deal {
  id: number;
  name: string;
  target_company: string;
  industry: string | null;
  deal_size: number | null;
  status: "pending" | "analyzing" | "completed" | "failed";
  created_at: string;
  document_count: number;
  analysis_count: number;
}

export interface DealDetail extends Deal {
  documents: Document[];
  analyses: AnalysisSummary[];
}

export interface Document {
  id: number;
  filename: string;
  file_type: string;
  file_size: number;
  doc_type: string | null;
  doc_type_confidence: number | null;
  uploaded_at: string;
}

export interface AnalysisSummary {
  analysis_type: string;
  status: string;
  completed_at: string | null;
}

export interface Analysis {
  id: number;
  analysis_type: string;
  status: string;
  results: any;            // Structure depends on analysis_type (see below)
  error_message: string | null;
  created_at: string;
  completed_at: string | null;
}

export interface ChatMessage {
  id: number;
  role: "user" | "assistant";
  content: string;
  sources: { chunk_text: string; filename: string; relevance_score: number }[] | null;
  created_at: string;
}

export interface Report {
  id: number;
  report_type: "iar" | "dcf" | "red_flag";
  generated_at: string;
  download_url: string;
}

// --- Analysis Result Shapes ---

export interface QoEResults {
  reported_ebitda: number;
  adjusted_ebitda: number;
  total_adjustments: number;
  adjustments: { description: string; amount: number; category: string; impact: string }[];
  quality_score: number;
  earnings_sustainability: "high" | "medium" | "low";
  ebitda_margin: number;
  adjusted_ebitda_margin: number;
}

export interface WorkingCapitalResults {
  current_assets: number;
  current_liabilities: number;
  net_working_capital: number;
  current_ratio: number;
  dso: number;
  dio: number;
  dpo: number;
  cash_conversion_cycle: number;
  nwc_as_pct_revenue: number;
  assessment: string;
}

export interface RatioResults {
  liquidity: { current_ratio: number; quick_ratio: number; cash_ratio: number };
  profitability: { gross_margin: number; ebitda_margin: number; operating_margin: number; net_margin: number; roe: number; roa: number };
  leverage: { debt_to_equity: number; debt_to_assets: number; interest_coverage: number; debt_to_ebitda: number };
  efficiency: { asset_turnover: number; inventory_turnover: number; receivables_turnover: number };
  cash_flow: { ocf_to_net_income: number; fcf_margin: number };
  overall_health_score: number;
  health_rating: "Excellent" | "Good" | "Fair" | "Concerning" | "Critical";
}

export interface DCFResults {
  assumptions: Record<string, number>;
  projected_years: { year: number; revenue: number; ebitda: number; fcf: number; discount_factor: number; pv_fcf: number; growth_rate: number }[];
  terminal_value: number;
  pv_terminal_value: number;
  sum_pv_fcf: number;
  enterprise_value: number;
  equity_value: number;
  ev_to_revenue: number;
  ev_to_ebitda: number;
  current_ebitda_margin: number;
}

export interface RedFlag {
  flag: string;
  severity: "high" | "medium" | "low";
  description: string;
  metric: string;
  value: number;
  threshold: number;
}

export interface Anomaly {
  anomaly: string;
  severity: "critical" | "high" | "medium" | "low";
  category: "statistical" | "rule_based";
  description: string;
  metric: string;
  value: number;
  expected_range: string;
}

export interface AIInsights {
  executive_summary: string;
  key_findings: { finding: string; impact: string; recommendation: string }[];
  risk_assessment: {
    overall_risk: "low" | "medium" | "high";
    financial_risk: string;
    operational_risk: string;
    deal_recommendation: "proceed" | "proceed_with_caution" | "significant_concerns";
  };
  valuation_opinion: string;
  questions_for_management: string[];
}
```

## Utility Helpers (`lib/utils.ts`)

```typescript
export function formatCurrency(value: number): string {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD",
    minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(value);
}

export function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`;
}

export function formatNumber(value: number, decimals = 1): string {
  return new Intl.NumberFormat("en-US", {
    minimumFractionDigits: decimals, maximumFractionDigits: decimals
  }).format(value);
}

export function formatCompactCurrency(value: number): string {
  if (Math.abs(value) >= 1_000_000_000) return `$${(value / 1_000_000_000).toFixed(1)}B`;
  if (Math.abs(value) >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}M`;
  if (Math.abs(value) >= 1_000) return `$${(value / 1_000).toFixed(0)}K`;
  return `$${value.toFixed(0)}`;
}

export function cn(...classes: (string | undefined | false)[]): string {
  return classes.filter(Boolean).join(" ");
}

export function severityColor(severity: string): string {
  switch (severity) {
    case "critical": return "bg-red-700 text-white";
    case "high": return "bg-red-500 text-white";
    case "medium": return "bg-amber-500 text-white";
    case "low": return "bg-blue-500 text-white";
    default: return "bg-gray-400 text-white";
  }
}

export function healthColor(score: number): string {
  if (score >= 80) return "text-emerald-500";
  if (score >= 65) return "text-green-500";
  if (score >= 45) return "text-amber-500";
  if (score >= 25) return "text-orange-500";
  return "text-red-500";
}

export function riskBadgeColor(risk: string): string {
  switch (risk) {
    case "low": return "bg-emerald-100 text-emerald-800 border-emerald-300";
    case "medium": return "bg-amber-100 text-amber-800 border-amber-300";
    case "high": return "bg-red-100 text-red-800 border-red-300";
    default: return "bg-gray-100 text-gray-800";
  }
}

export function recommendationLabel(rec: string): string {
  switch (rec) {
    case "proceed": return "Proceed";
    case "proceed_with_caution": return "Proceed with Caution";
    case "significant_concerns": return "Significant Concerns";
    default: return rec;
  }
}

export function fileTypeIcon(type: string): string {
  switch (type) {
    case "pdf": return "FileText";
    case "xlsx": case "xls": case "csv": return "Sheet";
    case "docx": case "doc": case "txt": return "FileType";
    case "png": case "jpg": case "jpeg": return "Image";
    default: return "File";
  }
}

export function timeSince(dateStr: string): string {
  const seconds = Math.floor((Date.now() - new Date(dateStr).getTime()) / 1000);
  if (seconds < 60) return "just now";
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
}
```

## Polling Hook (`hooks/use-polling.ts`)

```typescript
import { useEffect, useRef, useState } from "react";

export function usePolling<T>(
  fetcher: () => Promise<T>,
  intervalMs: number,
  shouldPoll: boolean
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!shouldPoll) return;
    let active = true;

    const poll = async () => {
      try {
        const result = await fetcher();
        if (active) { setData(result); setLoading(false); }
      } catch (e) {
        if (active) setLoading(false);
      }
    };

    poll(); // initial fetch
    const id = setInterval(poll, intervalMs);
    return () => { active = false; clearInterval(id); };
  }, [shouldPoll, intervalMs]);

  return { data, loading };
}
```

---

## DESIGN SYSTEM

### Color Palette
```
Primary:     slate-900 (sidebar bg), slate-800 (sidebar hover)
Background:  slate-50 (main area), white (cards)
Accent:      blue-600 (primary buttons, links, active nav)
Success:     emerald-500 (good metrics, low risk)
Warning:     amber-500 (medium risk, caution)
Danger:      red-500 (high risk, critical, bad metrics)
Critical:    red-700 (critical severity)
Text:        slate-900 (headers), slate-600 (body), slate-400 (muted)
Borders:     slate-200
```

### Layout
- **Sidebar:** Fixed left, 256px wide (w-64), full height, dark (slate-900)
- **Main content:** ml-64, p-8, bg-slate-50, min-h-screen
- **Cards:** bg-white, rounded-xl, shadow-sm, border border-slate-200, p-6
- **Max content width:** max-w-7xl mx-auto

### Typography
- **Page titles:** text-2xl font-bold text-slate-900
- **Section headers:** text-lg font-semibold text-slate-800
- **Body:** text-sm text-slate-600
- **Metric values:** text-3xl font-bold (use healthColor for coloring)
- **Metric labels:** text-xs uppercase tracking-wide text-slate-400

---

## PAGE DESIGNS

### Root Layout (`layout.tsx`)

Sidebar on left + main content area on right. Sidebar is always visible.

```
┌──────────┬────────────────────────────────────────────┐
│          │                                            │
│  SIDEBAR │         {children} — page content          │
│          │                                            │
│  ◆ TAM   │                                            │
│          │                                            │
│  🏠 Home  │                                            │
│  📤 Upload│                                            │
│  📄 Deals │                                            │
│          │                                            │
│          │                                            │
│          │                                            │
│  ─────── │                                            │
│  v1.0    │                                            │
└──────────┴────────────────────────────────────────────┘
```

Sidebar details:
- Background: slate-900
- TAM logo at top: bold white text "TAM" with subtitle "Transaction Analysis Machine" in slate-400, text-xs
- Nav items: Home (/), Upload (/upload), Deals (/deals)
- Each nav item: flex items-center gap-3, py-2.5 px-4, rounded-lg, text-slate-300
- Active item: bg-slate-800, text-white
- Lucide icons: LayoutDashboard, Upload, FolderOpen
- Bottom: version "v1.0.0" in slate-500, text-xs

### 1. Dashboard (`/page.tsx`)

```
┌──────────────────────────────────────────────────────┐
│  Financial Due Diligence Dashboard                   │
│                                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐ │
│  │Total Deals│ │ Documents │ │ Analyses │ │Avg Score│ │
│  │    3      │ │    12     │ │    21    │ │   72    │ │
│  └──────────┘ └──────────┘ └──────────┘ └─────────┘ │
│                                                      │
│  Recent Deals                        [+ New Deal]    │
│  ┌──────────────────────────────────────────────┐    │
│  │ Name         │ Target    │ Status │ Risk │Date│    │
│  │ Apex Cloud.. │ Apex Co.. │ ✅ Done│ Med  │ 2d │    │
│  │ Widget Inc.. │ Widget .. │ ⏳ Run │  —   │ 1h │    │
│  └──────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────┘
```

Stats cards:
- 4 cards in a grid (grid-cols-4 gap-6)
- Each card: white bg, rounded-xl, p-6, shadow-sm
- Icon in colored circle (top-left), value (text-3xl font-bold), label below (text-sm text-slate-500)
- Icons: Briefcase (deals), FileText (docs), BarChart3 (analyses), Heart (health)

Recent deals table:
- shadcn Table component
- Status column: green badge "Completed", amber "Analyzing" with pulse animation, gray "Pending"
- Risk column: colored badge (green/amber/red) based on ai_insights.risk_assessment.overall_risk
- Clicking a row navigates to `/deals/{id}`
- "+ New Deal" button in top right → navigates to /upload

Fetch data: `GET /api/deals` on mount. Compute stats from the deals array.
For "Avg Score": fetch each completed deal's analysis and average the health scores. If too complex, just show the count of completed analyses.

### 2. Upload Page (`/upload/page.tsx`)

```
┌──────────────────────────────────────────────────────┐
│  New Due Diligence Deal                              │
│                                                      │
│  Deal Name:     [ Apex Cloud Acquisition       ]     │
│  Target Company:[ Apex Cloud Solutions          ]     │
│  Industry:      [ SaaS                     ▼   ]     │
│  Deal Size ($): [ 45,000,000                   ]     │
│                                                      │
│  ┌──────────────────────────────────────────────┐    │
│  │                                              │    │
│  │     📁 Drag & drop files here               │    │
│  │     or click to browse                       │    │
│  │                                              │    │
│  │     Supports: PDF, Excel, CSV, Word,         │    │
│  │     Images, Text files                       │    │
│  │                                              │    │
│  └──────────────────────────────────────────────┘    │
│                                                      │
│  Uploaded Files:                                     │
│  ┌─────────────────────────────────────┐             │
│  │ 📄 income_statement_2025.pdf  2.1MB  ✕ │          │
│  │ 📊 balance_sheet.xlsx         840KB  ✕ │          │
│  │ 📄 cash_flow_report.pdf      1.5MB  ✕ │          │
│  └─────────────────────────────────────┘             │
│                                                      │
│              [ 🚀 Run Analysis ]                     │
│                                                      │
│  ┌──────────────────────────────────────────────┐    │
│  │  ⏳ Analyzing... Extracting financial data    │    │
│  │  ████████████░░░░░░░░  45%                   │    │
│  └──────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────┘
```

Flow:
1. User fills in deal details
2. User drags files onto the dropzone (or clicks to browse)
3. Files show in a list below with size + remove button
4. User clicks "Run Analysis"
5. Frontend:
   a. Calls `POST /api/deals` to create the deal
   b. Calls `POST /api/deals/{id}/documents` to upload all files
   c. Calls `POST /api/deals/{id}/analyze` to trigger analysis
   d. Shows a progress/status card that polls `GET /api/deals/{id}` every 3s
   e. When status = "completed", redirect to `/deals/{id}`
   f. When status = "failed", show error message with retry button

Dropzone:
- Dashed border (border-dashed border-2 border-slate-300), rounded-xl
- Hover: border-blue-400 bg-blue-50
- Drag over: border-blue-500 bg-blue-50 scale-[1.01]
- Accept: .pdf, .xlsx, .xls, .csv, .docx, .doc, .txt, .png, .jpg, .jpeg
- Use native HTML drag/drop events (onDragOver, onDrop, onChange for input)

Industry dropdown options: SaaS, Manufacturing, Healthcare, Financial Services, Retail, Technology, Energy, Real Estate, Other

Analyzing state:
- Replace "Run Analysis" with a card showing status
- Animated pulse or spinner
- Text updates: "Creating deal...", "Uploading documents...", "Analyzing financial data...", "Generating insights..."

### 3. Deals List (`/deals/page.tsx`)

```
┌──────────────────────────────────────────────────────┐
│  All Deals                              [+ New Deal] │
│                                                      │
│  ┌──────────────────────────────────────────────┐    │
│  │ Name          │ Target      │ Size   │Status │    │
│  │───────────────┼─────────────┼────────┼───────│    │
│  │ Apex Cloud    │ Apex Cloud  │ $45M   │ ✅    │    │
│  │ Widget Inc    │ Widget Inc  │ $12M   │ ⏳    │    │
│  │ DataFlow AI   │ DataFlow    │ $80M   │ ⬜    │    │
│  └──────────────────────────────────────────────┘    │
│                                                      │
│  Showing 3 deals                                     │
└──────────────────────────────────────────────────────┘
```

- Fetch `GET /api/deals` on mount
- Full-width table with hover states
- Status: green checkmark (completed), amber spinner (analyzing), gray circle (pending), red X (failed)
- Click row → `/deals/{id}`
- Empty state: "No deals yet. Upload your first financial documents to get started." + button to /upload

### 4. Deal Detail (`/deals/[id]/page.tsx`) — THE BIG PAGE

This is the most complex page. It has a **header section** and **7 tabs**.

```
┌──────────────────────────────────────────────────────┐
│  ← Back to Deals                                     │
│                                                      │
│  Apex Cloud Solutions Acquisition         MEDIUM ⚠️  │
│  Target: Apex Cloud Solutions · SaaS · $45M          │
│  Created 2 days ago                                  │
│                                                      │
│  ┌────┬─────┬──────┬─────┬──────┬─────────┬────────┐ │
│  │Over│ QoE │Finan.│ DCF │Flags │Insights │  Chat  │ │
│  └────┴─────┴──────┴─────┴──────┴─────────┴────────┘ │
│                                                      │
│           [ Tab content here ]                       │
│                                                      │
│  ─── Report Generation ───────────────────────────── │
│  [📄 IAR Report] [📊 DCF Report] [🚩 Red Flag Report]│
└──────────────────────────────────────────────────────┘
```

Header:
- Back link: text-sm text-blue-600 with ArrowLeft icon
- Deal name: text-2xl font-bold
- Risk badge: large, colored, pulled from ai_insights → risk_assessment → overall_risk
- Subtitle: target company, industry, deal size, time since creation

If deal is still "analyzing": show a full-page loading state with spinner + "Analysis in progress..." and poll every 3s.

Tabs: Use shadcn `Tabs` component. Each tab fetches its specific analysis data on activation.

#### Report Generation Section
Fixed at the bottom of the deal detail page (below the tabs). Three buttons:
- "Generate IAR Report" → calls `POST /api/deals/{id}/reports/iar`
- "Generate DCF Report" → calls `POST /api/deals/{id}/reports/dcf`
- "Generate Red Flag Report" → calls `POST /api/deals/{id}/reports/red_flag`

Each button shows: loading spinner while generating, then a "Download PDF" link when done.
Poll `GET /api/deals/{id}/reports/{type}/status` every 2s while generating.
When completed, show download button that opens `getReportDownloadUrl(reportId)` in a new tab.

Also show previously generated reports in a list below the buttons.

---

#### Tab: Overview

```
┌──────────────────────────────────────────────────────┐
│  Executive Summary                                   │
│  ┌──────────────────────────────────────────────┐    │
│  │ Apex Cloud Solutions demonstrates strong      │    │
│  │ revenue growth (28% YoY) with healthy SaaS   │    │
│  │ unit economics...                             │    │
│  └──────────────────────────────────────────────┘    │
│                                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐ │
│  │ Revenue  │ │Adj EBITDA│ │   NWC    │ │ Health  │ │
│  │ $22.4M   │ │ $4.45M   │ │ $4.33M   │ │ 72/100  │ │
│  │          │ │ 19.9%    │ │ 19.3%    │ │  Good   │ │
│  └──────────┘ └──────────┘ └──────────┘ └─────────┘ │
│                                                      │
│  Deal Recommendation                                 │
│  ┌──────────────────────────────────────────────┐    │
│  │ ⚠️ PROCEED WITH CAUTION                      │    │
│  │ Financial Risk: Moderate — strong growth...   │    │
│  │ Operational Risk: Low to moderate...          │    │
│  └──────────────────────────────────────────────┘    │
│                                                      │
│  Documents (3 files)                                 │
│  📄 income_statement.pdf  · Income Statement · 94%   │
│  📊 balance_sheet.xlsx    · Balance Sheet    · 91%   │
│  📄 cash_flow.pdf         · Cash Flow        · 88%   │
└──────────────────────────────────────────────────────┘
```

- Data from: `ai_insights` + `qoe` (adjusted EBITDA) + `working_capital` (NWC) + `ratios` (health score)
- 4 metric cards: Revenue (formatCompactCurrency), Adjusted EBITDA + margin, NWC + % revenue, Health Score + rating
- Executive summary: rendered as markdown-ish text in a light blue/gray box
- Deal recommendation: colored box matching risk level
- Documents list at bottom showing filename + ML-classified type + confidence percentage

#### Tab: Quality of Earnings

```
┌──────────────────────────────────────────────────────┐
│  Quality of Earnings                    Score: 55    │
│                                                      │
│  EBITDA Bridge                                       │
│  ┌──────────────────────────────────────────────┐    │
│  │  Reported EBITDA          $3,360,000         │    │
│  │  + Litigation settlement    +750,000         │    │
│  │  + CEO consulting fees      +320,000         │    │
│  │  − Related party lease      -180,000         │    │
│  │  + PPP loan forgiveness     +200,000         │    │
│  │  ───────────────────────────────────          │    │
│  │  Adjusted EBITDA          $4,450,000         │    │
│  └──────────────────────────────────────────────┘    │
│                                                      │
│  Earnings Sustainability: MEDIUM                     │
│  EBITDA Margin: 15.0% → Adjusted: 19.9%             │
│                                                      │
│  Adjustments Detail                                  │
│  ┌──────────────────────────────────────────────┐    │
│  │Category        │ Description       │ Amount  │    │
│  │Non-Recurring   │ Litigation...     │ +$750K  │    │
│  │Owner Comp      │ CEO fees...       │ +$320K  │    │
│  │Related Party   │ Lease above...    │ -$180K  │    │
│  │Non-Recurring   │ PPP forgive...    │ +$200K  │    │
│  └──────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────┘
```

- Quality score: big number in colored circle (green ≥70, amber ≥40, red <40)
- EBITDA bridge: styled as a waterfall — each row is a line item. Positive amounts in green, negative in red. Final row bold with top border.
- Adjustments table: shadcn Table, category badge + description + formatted amount
- Sustainability badge: colored (high=green, medium=amber, low=red)

#### Tab: Financials (Working Capital + Ratios)

Two sections stacked:

**Working Capital Section:**
```
┌──────────────────────────────────────────────────────┐
│  Working Capital Analysis                            │
│                                                      │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────────┐  │
│  │ DSO  │ │ DIO  │ │ DPO  │ │ CCC  │ │   NWC    │  │
│  │ 78.2 │ │ 15.2 │ │105.9 │ │-12.5 │ │ $4.33M   │  │
│  │ days │ │ days │ │ days │ │ days │ │ 19.3%rev │  │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────────┘  │
│                                                      │
│  Assessment: Healthy working capital cycle...        │
└──────────────────────────────────────────────────────┘
```

**Ratios Section:**
```
┌──────────────────────────────────────────────────────┐
│  Financial Ratios                    Health: 72 GOOD │
│                                                      │
│  Liquidity            Profitability                  │
│  ┌────────────────┐   ┌────────────────┐             │
│  │Current  2.00 🟢│   │Gross M. 70.0%🟢│             │
│  │Quick    1.93 🟢│   │EBITDA M 15.0%🟡│             │
│  │Cash     0.74 🟡│   │Net M.   6.9% 🟡│             │
│  └────────────────┘   │ROE     25.4% 🟢│             │
│                       │ROA     10.8% 🟢│             │
│  Leverage             └────────────────┘             │
│  ┌────────────────┐   Efficiency                     │
│  │D/E     1.35 🟡 │   ┌────────────────┐             │
│  │D/A     0.57 🟡 │   │Asset T. 1.58 🟢│             │
│  │Int Cov 8.00 🟢 │   │Inv T.  24.00🟢│             │
│  │D/EBITDA 1.49🟢 │   │Recv T.  4.67 🟡│             │
│  └────────────────┘   └────────────────┘             │
└──────────────────────────────────────────────────────┘
```

Ratio indicators (colored dots):
- Liquidity: current_ratio ≥ 1.5 = green, ≥ 1.0 = amber, else red
- Quick: ≥ 1.0 = green, ≥ 0.5 = amber, else red
- Gross margin: ≥ 40% = green, ≥ 20% = amber, else red
- Net margin: ≥ 10% = green, ≥ 0% = amber, else red
- D/E: ≤ 1.5 = green, ≤ 3.0 = amber, else red
- Interest coverage: ≥ 5 = green, ≥ 2 = amber, else red

Use 4-column grid layout for the ratio groups.

#### Tab: DCF Valuation

```
┌──────────────────────────────────────────────────────┐
│  DCF Valuation                                       │
│                                                      │
│  Enterprise Value: $38.2M    Equity Value: $37.7M    │
│  EV/Revenue: 1.7x           EV/EBITDA: 11.4x        │
│                                                      │
│  5-Year Projection        [Recharts bar/line chart]  │
│  ┌──────────────────────────────────────────────┐    │
│  │ Year │ Revenue  │ EBITDA  │  FCF    │ PV FCF │    │
│  │  1   │ $24.6M   │ $3.7M  │ $2.5M   │ $2.2M  │    │
│  │  2   │ $26.9M   │ $4.0M  │ $2.8M   │ $2.2M  │    │
│  │  3   │ $29.1M   │ $4.4M  │ $3.0M   │ $2.2M  │    │
│  │  4   │ $31.1M   │ $4.7M  │ $3.2M   │ $2.1M  │    │
│  │  5   │ $33.0M   │ $5.0M  │ $3.4M   │ $1.9M  │    │
│  └──────────────────────────────────────────────┘    │
│                                                      │
│  Valuation Bridge                                    │
│  PV of FCFs:        $10.6M                           │
│  PV Terminal Value: $27.6M                           │
│  Enterprise Value:  $38.2M                           │
│  + Cash:            $3.2M                            │
│  − Debt:            $5.0M                            │
│  Equity Value:      $36.4M                           │
│                                                      │
│  Key Assumptions                                     │
│  WACC: 12% · Terminal Growth: 3% · Tax Rate: 25%    │
└──────────────────────────────────────────────────────┘
```

- Top metrics: 4 large cards (EV, Equity Value, EV/Revenue, EV/EBITDA)
- **Recharts bar chart:** Revenue + FCF bars per year, with a line for PV FCF
- Projection table: formatted with compact currency
- Valuation bridge: styled like the QoE bridge (running calculation)
- Assumptions: simple key-value display

#### Tab: Red Flags + Anomalies

```
┌──────────────────────────────────────────────────────┐
│  Red Flags & Anomaly Detection                       │
│                                                      │
│  Summary:  🔴 2 High   🟡 3 Medium   🔵 1 Low       │
│                                                      │
│  Red Flags                                           │
│  ┌──────────────────────────────────────────────┐    │
│  │ 🔴 HIGH  Slow Collections                    │    │
│  │ DSO of 78 days means it takes over 2 months  │    │
│  │ to collect. Metric: 78.2 / Threshold: 60     │    │
│  ├──────────────────────────────────────────────┤    │
│  │ 🟡 MED   Earnings Quality Concern            │    │
│  │ Revenue positive but OCF analysis needed...   │    │
│  └──────────────────────────────────────────────┘    │
│                                                      │
│  ML Anomaly Detection                                │
│  ┌──────────────────────────────────────────────┐    │
│  │ 🟡 MEDIUM  [Statistical]                     │    │
│  │ Unusual Net Margin — 6.9% is at the lower    │    │
│  │ end of the typical range (5-25%). Z: 1.2     │    │
│  └──────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────┘
```

- Summary bar: count badges with colored backgrounds
- Each red flag: card with severity badge (left), title, description, metric/threshold
- Anomalies section: separate from red flags, labeled "ML Anomaly Detection"
- Anomaly cards: same layout but include "Statistical" or "Rule-based" badge and expected range

Data from: `red_flags` analysis + `anomalies` analysis

#### Tab: AI Insights

```
┌──────────────────────────────────────────────────────┐
│  AI-Powered Insights                                 │
│                                                      │
│  Executive Summary                                   │
│  ┌──────────────────────────────────────────────┐    │
│  │ Apex Cloud Solutions demonstrates strong...   │    │
│  └──────────────────────────────────────────────┘    │
│                                                      │
│  Key Findings                                        │
│  ┌──────────────────────────────────────────────┐    │
│  │ 🔴 HIGH IMPACT                               │    │
│  │ EBITDA adjustments total $1.09M (32%)        │    │
│  │ → Negotiate based on adjusted EBITDA...       │    │
│  ├──────────────────────────────────────────────┤    │
│  │ 🟡 MEDIUM IMPACT                             │    │
│  │ DSO of 78 days indicates slow collections    │    │
│  │ → Request AR aging schedule...                │    │
│  └──────────────────────────────────────────────┘    │
│                                                      │
│  Valuation Opinion                                   │
│  ┌──────────────────────────────────────────────┐    │
│  │ DCF suggests EV of ~$35-40M. At $45M deal   │    │
│  │ price, buyer paying modest premium...         │    │
│  └──────────────────────────────────────────────┘    │
│                                                      │
│  Questions for Management (7)                        │
│  1. Can you provide the AR aging schedule...         │
│  2. What percentage of revenue is annual vs...       │
│  3. Please detail the related party lease...         │
│  ...                                                 │
└──────────────────────────────────────────────────────┘
```

- Executive summary in a highlighted box (blue-50 border-l-4 border-blue-400)
- Key findings: each as a card with impact badge + finding + recommendation (indented with →)
- Valuation opinion: highlighted box
- Questions: numbered list with clean typography

#### Tab: Chat (RAG-powered)

```
┌──────────────────────────────────────────────────────┐
│  Ask AI about this deal                  [Clear ↻]   │
│                                                      │
│  ┌──────────────────────────────────────────────┐    │
│  │                                              │    │
│  │    👤 What are the biggest risks?            │    │
│  │                                              │    │
│  │    🤖 Based on the financial analysis, the   │    │
│  │    key risks are:                            │    │
│  │    1. Slow collections (DSO 78 days)...      │    │
│  │    2. QoE adjustments of 32%...              │    │
│  │                                              │    │
│  │    Sources:                                  │    │
│  │    📄 income_statement.pdf (94% relevant)    │    │
│  │    📄 cash_flow.pdf (87% relevant)           │    │
│  │                                              │    │
│  └──────────────────────────────────────────────┘    │
│                                                      │
│  Suggested:                                          │
│  [ What are the biggest risks? ]                     │
│  [ Is the revenue sustainable? ]                     │
│  [ Summarize the earnings quality ]                  │
│  [ What should I ask management? ]                   │
│                                                      │
│  ┌──────────────────────────────────────────────┐    │
│  │ Ask a question about this deal...    [Send ➤]│    │
│  └──────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────┘
```

- Chat thread: scrollable area (max-h-[500px] overflow-y-auto)
- User messages: right-aligned, blue-600 bg, white text, rounded-xl
- AI messages: left-aligned, white bg, border, rounded-xl, includes "Sources" section showing which documents were used
- Sources: small text below AI message, showing filename + relevance score
- Suggested questions: clickable chips/buttons above the input, disappear after first use
- Input: full-width text input with send button (blue-600)
- Clear button: top right, clears chat history (calls DELETE)
- Loading state: typing indicator (3 bouncing dots) while waiting for AI response

Fetch chat history on tab activation: `GET /api/deals/{id}/chat`
Send message: `POST /api/deals/{id}/chat` → append both user and AI messages to local state

---

## shadcn Components Needed

Install these shadcn components:
```bash
npx shadcn@latest add button card badge table tabs input textarea separator
npx shadcn@latest add dialog dropdown-menu skeleton progress toast tooltip
npx shadcn@latest add scroll-area sheet avatar alert
```

Also install:
```bash
npm install recharts lucide-react
```

## Important Implementation Notes

1. **All API calls go to `http://localhost:8000/api/...`** — configure this in api.ts. Use an env var `NEXT_PUBLIC_API_URL` with default `http://localhost:8000/api`.
2. **Polling pattern:** Deal detail page polls every 3s while status is "analyzing". Report buttons poll every 2s while generating. Stop polling when done.
3. **Error handling:** Show toast notifications (shadcn toast) on API errors. Never crash on null data — always use optional chaining and fallback displays.
4. **Empty/loading states:** Every component should handle: loading (skeleton or spinner), empty (friendly message + CTA), error (red alert with message), and data states.
5. **File upload:** Use native FormData, NOT a library. Accept all listed formats. Show file size in human-readable format (KB/MB).
6. **Number formatting:** ALWAYS use the util formatters. Never show raw numbers. Currency = `$X,XXX,XXX`, percentages = `XX.X%`, days = `XX.X days`.
7. **No SSR for API calls** — use `"use client"` directive on all pages that fetch data. These are all client-side rendered pages.
8. **Desktop-first** — use desktop-appropriate layouts. Don't worry about mobile but don't explicitly break it.
9. **Recharts:** Only used on the DCF tab. Keep it simple — one BarChart for projected revenue/FCF. Style it to match the design system.

## `next.config.js`

```js
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
};
module.exports = nextConfig;
```

Now build the entire frontend. Start with the root layout and sidebar, then the dashboard, then upload page, then deals list, then the deal detail page with all tabs. Make sure all API calls match the contract exactly — the backend team is building to the same spec.
