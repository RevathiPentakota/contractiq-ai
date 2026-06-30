# ContractIQ AI - Frontend Component Index

**Complete reference for all UI components**

---

## 🎨 Component Gallery

### 1. Header Component
**File**: `src/components/Header.tsx`

Features:
- Logo with brand name and tagline
- Navigation menu (Dashboard, Contracts, Help)
- User profile placeholder
- Fully responsive

```tsx
import Header from "@/components/Header";

export default function MyPage() {
  return <Header />;
}
```

**Design**: 
- Blue gradient logo icon
- Border-bottom separator
- Horizontal navigation layout

---

### 2. Upload Section
**File**: `src/components/UploadSection.tsx`

Features:
- Drag-and-drop interface
- File input fallback
- PDF-only validation
- Visual feedback on drag over
- File size limit notice (10MB)

```tsx
import UploadSection from "@/components/UploadSection";

export default function MyPage() {
  return (
    <UploadSection 
      onUpload={(file) => console.log("Uploading:", file.name)}
    />
  );
}
```

**Design**:
- Dashed border container
- Blue icon and accent color
- Changes on drag over (blue background)

---

### 3. Processing Indicator
**File**: `src/components/ProcessingIndicator.tsx`

Features:
- Status-specific icons (spinner, checkmark, error)
- Animated progress bar
- Progress percentage display
- Error message support
- Color-coded backgrounds (blue/green/red)

```tsx
import ProcessingIndicator from "@/components/ProcessingIndicator";
import { ProcessingState } from "@/types/contract";

export default function MyPage() {
  const state: ProcessingState = {
    status: "processing",
    progress: 65,
    message: "Analyzing contract..."
  };
  
  return <ProcessingIndicator state={state} />;
}
```

**Statuses**:
- `idle` - Not shown
- `uploading` - Blue with progress bar
- `processing` - Blue with spinner
- `completed` - Green with checkmark
- `error` - Red with error icon

---

### 4. Card Component
**File**: `src/components/Card.tsx`

Generic card wrapper used by all analysis cards.

```tsx
import Card from "@/components/Card";

export default function MyCard() {
  return (
    <Card
      title="Card Title"
      description="Optional description"
      icon={<YourIcon />}
    >
      <p>Card content goes here</p>
    </Card>
  );
}
```

**Features**:
- Header with optional icon
- Bordered container
- Shadow effect
- Responsive padding

---

### 5. Summary Card
**File**: `src/components/SummaryCard.tsx`

Displays executive summary and metadata.

```tsx
import SummaryCard from "@/components/SummaryCard";

export default function MyPage() {
  return (
    <SummaryCard
      title="Service Agreement 2024.pdf"
      summary="This is a comprehensive SaaS agreement..."
      metadata={{
        format: "pdf",
        word_count: 8543,
        page_count: 24,
        file_size: 2500000
      }}
    />
  );
}
```

**Displays**:
- Document icon
- Contract title
- Executive summary (paragraph)
- 4-column metadata grid (Format, Pages, Words, Size)

---

### 6. Risks Card
**File**: `src/components/RisksCard.tsx`

Shows identified risks with severity levels.

```tsx
import RisksCard from "@/components/RisksCard";
import { Risk } from "@/types/contract";

export default function MyPage() {
  const risks: Risk[] = [
    {
      category: "Liability",
      severity: "high",
      title: "Unlimited Indemnification",
      description: "Your company must indemnify...",
      clause_reference: "Section 8.1",
      recommendation: "Negotiate cap on obligations..."
    }
  ];
  
  return <RisksCard risks={risks} />;
}
```

**Features**:
- Risk icon
- Severity count summary
- Risk list with:
  - Colored severity badges
  - Category labels
  - Description
  - Clause references
  - Recommendation indicator

**Severity Colors**:
- Critical: Red
- High: Orange
- Medium: Yellow
- Low: Green

---

### 7. Clauses Card
**File**: `src/components/ClausesCard.tsx`

Displays extracted contract clauses by importance.

```tsx
import ClausesCard from "@/components/ClausesCard";
import { Clause } from "@/types/contract";

export default function MyPage() {
  const clauses: Clause[] = [
    {
      title: "Service Term and Renewal",
      category: "Term",
      importance: "high",
      description: "Initial term of 36 months with automatic annual renewal...",
      clause_reference: "Section 2"
    }
  ];
  
  return <ClausesCard clauses={clauses} />;
}
```

**Features**:
- Clause icon
- Critical clause count
- Clause list with:
  - Importance-based left border color
  - Title and category
  - Description
  - Location reference
  - Importance level badge

**Importance Colors**:
- High: Red left border
- Medium: Yellow left border
- Low: Green left border

---

### 8. Recommendations Card
**File**: `src/components/RecommendationsCard.tsx`

Shows actionable recommendations prioritized by urgency.

```tsx
import RecommendationsCard from "@/components/RecommendationsCard";
import { Recommendation } from "@/types/contract";

export default function MyPage() {
  const recommendations: Recommendation[] = [
    {
      priority: "high",
      category: "Legal",
      recommendation: "Negotiate cap on indemnification...",
      rationale: "Current terms expose your company to unlimited liability..."
    }
  ];
  
  return <RecommendationsCard recommendations={recommendations} />;
}
```

**Features**:
- Recommendation icon
- Priority count summary
- Recommendations sorted by priority
- Each recommendation shows:
  - Priority emoji indicator (🔴 High, 🟡 Medium, 🟢 Low)
  - Priority badge
  - Recommendation text
  - Category
  - Rationale

---

## 🔄 Data Flow

```
User Action
    ↓
handleUpload()
    ↓
Simulate Processing Stages:
  - Stage 1: Uploading (30%)
  - Stage 2: Extracting (45%)
  - Stage 3: Analyzing (65%)
  - Stage 4: Completed (100%)
    ↓
Load Mock Data: generateMockContractAnalysis()
    ↓
Display Results:
  - SummaryCard
  - RisksCard + ClausesCard (side-by-side)
  - RecommendationsCard
    ↓
User can: Reset → Upload New Contract
```

---

## 📐 Responsive Breakpoints

All components use Tailwind CSS responsive classes:

- **Mobile**: Default (< 640px)
- **sm**: 640px - Small tablets
- **md**: 768px - Tablets
- **lg**: 1024px - Large screens
- **xl**: 1280px - Extra large screens

### Responsive Behavior Examples

**Card Grid**:
```tsx
<div className="grid gap-6 lg:grid-cols-2">
  <RisksCard />
  <ClausesCard />
</div>
```
- Mobile: Single column (full width)
- Large+: Two columns side-by-side

**Text Sizing**:
```tsx
<h2 className="text-2xl font-bold text-gray-900 sm:text-3xl">
  Heading
</h2>
```
- Mobile: text-2xl
- Small+: text-3xl

---

## 🎯 Type Definitions Quick Reference

### Risk Severity
```typescript
type RiskSeverity = "low" | "medium" | "high" | "critical"
```

### Clause Importance
```typescript
type ClauseImportance = "low" | "medium" | "high"
```

### Recommendation Priority
```typescript
type RecommendationPriority = "low" | "medium" | "high"
```

### Processing Status
```typescript
type ProcessingStatus = "idle" | "uploading" | "processing" | "completed" | "error"
```

---

## 🛠️ Common Usage Patterns

### Import All Components
```tsx
import {
  Header,
  UploadSection,
  ProcessingIndicator,
  Card,
  SummaryCard,
  RisksCard,
  ClausesCard,
  RecommendationsCard
} from "@/components";
```

### Import Mock Data
```tsx
import {
  generateMockContractAnalysis,
  generateMockProcessingState,
  generateProcessingStates
} from "@/lib/mockData";
```

### Import Types
```tsx
import {
  ContractAnalysis,
  Risk,
  Clause,
  Recommendation,
  ProcessingState
} from "@/types/contract";
```

---

## 📊 Component Sizes

### Bundle Impact (Approximate)

| Component | Size |
|-----------|------|
| Header | ~2 KB |
| UploadSection | ~3 KB |
| ProcessingIndicator | ~2.5 KB |
| Card | ~1 KB |
| SummaryCard | ~2.5 KB |
| RisksCard | ~3 KB |
| ClausesCard | ~3 KB |
| RecommendationsCard | ~3 KB |
| **Total Components** | **~20 KB** |
| Page with All Components | **119 KB** |

---

## 🔍 Debugging Tips

### Check Mock Data
```tsx
import { generateMockContractAnalysis } from "@/lib/mockData";

const data = generateMockContractAnalysis();
console.log("Mock data:", data);
```

### Verify Processing States
```tsx
import { generateProcessingStates } from "@/lib/mockData";

const states = generateProcessingStates();
console.log("Uploading:", states.uploading);
console.log("Completed:", states.completed);
```

### Type Checking
```tsx
// TypeScript will catch type mismatches
const analysis: ContractAnalysis = {
  // All required fields must be present
  contract_id: "...",
  file_name: "...",
  // etc.
};
```

---

## ✨ Customization Guide

### Change Colors
All colors use Tailwind CSS. Edit component className:

```tsx
// Change from blue to green
<div className="bg-blue-100">  →  <div className="bg-green-100">
```

### Adjust Spacing
Use Tailwind spacing scale:

```tsx
// Larger padding
<div className="px-6 py-4">  →  <div className="px-8 py-6">

// Larger gap
<div className="gap-4">  →  <div className="gap-6">
```

### Add New Fields
Extend TypeScript interfaces:

```tsx
interface Risk {
  category: string;
  severity: "low" | "medium" | "high" | "critical";
  // Add new field:
  customField?: string;
}
```

---

## 📚 Learning Resources

- [Next.js Docs](https://nextjs.org/docs)
- [React Docs](https://react.dev)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [TypeScript Docs](https://www.typescriptlang.org/docs/)

---

**Component Gallery Last Updated**: June 29, 2026  
**Next.js Version**: 15.5.19  
**React Version**: 19.0.0-rc  
**Tailwind CSS Version**: 3.4.14
