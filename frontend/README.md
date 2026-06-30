# ContractIQ AI - Frontend

Professional AI-powered contract analysis dashboard built with Next.js 15, TypeScript, and Tailwind CSS.

## 🚀 Quick Start

### Prerequisites
- Node.js 18.17 or later
- npm or yarn

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Production Build

```bash
npm run build
npm start
```

## 📁 Project Structure

```
src/
├── app/                      # Next.js App Router
│   ├── layout.tsx           # Root layout with Tailwind CSS
│   └── page.tsx             # Main dashboard page
│
├── components/              # Reusable React components
│   ├── Header.tsx           # Navigation header with branding
│   ├── UploadSection.tsx    # Drag-and-drop file upload
│   ├── ProcessingIndicator.tsx # Progress indicator with status
│   ├── Card.tsx             # Reusable card wrapper
│   ├── SummaryCard.tsx      # Executive summary display
│   ├── RisksCard.tsx        # Risk identification display
│   ├── ClausesCard.tsx      # Contract clauses display
│   ├── RecommendationsCard.tsx # Recommendations display
│   └── index.ts             # Component exports
│
├── types/                   # TypeScript type definitions
│   └── contract.ts          # Contract analysis types
│
├── lib/                     # Utility functions
│   └── mockData.ts          # Mock data generators
│
└── styles/                  # Global styles
    └── globals.css          # Tailwind CSS imports
```

## 🎨 Components

### Header
Main navigation header with ContractIQ branding and quick links.

```tsx
<Header />
```

### UploadSection
Drag-and-drop interface for PDF file uploads.

```tsx
<UploadSection onUpload={(file) => handleUpload(file)} />
```

### ProcessingIndicator
Shows upload/processing status with animated progress bar.

```tsx
<ProcessingIndicator state={processingState} />
```

### Card Components

#### SummaryCard
Displays executive summary with document metadata.

```tsx
<SummaryCard
  title="contract.pdf"
  summary="Contract summary text..."
  metadata={{
    file_size: 2500000,
    word_count: 8543,
    page_count: 24,
    format: "pdf"
  }}
/>
```

#### RisksCard
Lists identified risks with severity levels and recommendations.

```tsx
<RisksCard risks={analysis.risks} />
```

#### ClausesCard
Displays extracted contract clauses organized by importance.

```tsx
<ClausesCard clauses={analysis.clauses} />
```

#### RecommendationsCard
Shows actionable recommendations prioritized by urgency.

```tsx
<RecommendationsCard recommendations={analysis.recommendations} />
```

## 📊 Data Types

### ContractAnalysis
Complete contract analysis result:

```typescript
interface ContractAnalysis {
  contract_id: string;
  file_name: string;
  summary: string;
  risks: Risk[];
  clauses: Clause[];
  recommendations: Recommendation[];
  metadata: {
    file_size?: number;
    word_count?: number;
    page_count?: number;
    format?: string;
  };
  created_at: string;
}
```

### Risk
```typescript
interface Risk {
  category: string;
  severity: "low" | "medium" | "high" | "critical";
  title: string;
  description: string;
  clause_reference?: string;
  recommendation?: string;
}
```

### Clause
```typescript
interface Clause {
  title: string;
  category: string;
  clause_reference?: string;
  description: string;
  importance: "low" | "medium" | "high";
}
```

### Recommendation
```typescript
interface Recommendation {
  priority: "low" | "medium" | "high";
  category: string;
  recommendation: string;
  rationale: string;
}
```

### ProcessingState
```typescript
interface ProcessingState {
  status: "idle" | "uploading" | "processing" | "completed" | "error";
  progress: number;
  message: string;
  error?: string;
}
```

## 🎯 Mock Data

The frontend currently uses realistic mock data for development:

```typescript
import { generateMockContractAnalysis } from "@/lib/mockData";

const analysis = generateMockContractAnalysis();
```

Mock data includes:
- Realistic contract analysis with 5 identified risks
- 7 key clauses across different categories
- 5 actionable recommendations
- Sample metadata (word count, page count, file size)

## 🔧 Configuration

### Tailwind CSS
All styling uses Tailwind CSS utility classes. No CSS files needed for component styling.

### TypeScript
Strict TypeScript configuration with full type safety throughout.

### ESLint
Code linting configured with Next.js best practices.

## 📦 Dependencies

### Core
- `next@15.5.19` - React framework
- `react@19.0.0-rc` - UI library
- `typescript@5.x` - Type safety

### Styling
- `tailwindcss@3.4.14` - Utility-first CSS
- `postcss@8.x` - CSS processing

### Development
- `@types/node` - Node.js types
- `eslint` - Code linting
- `eslint-config-next` - Next.js ESLint config

## 🌟 Features

✅ **Responsive Design** - Works on mobile, tablet, and desktop
✅ **Type-Safe** - Full TypeScript support throughout
✅ **Production-Ready** - Clean code with comprehensive documentation
✅ **No Third-Party UI** - Built with Tailwind CSS only
✅ **Mock Data** - Realistic sample data for development
✅ **Accessibility** - Semantic HTML and ARIA labels
✅ **Performance** - Optimized with Next.js

## 🚀 Backend Integration (Future)

To connect to the backend API:

1. Create environment variables in `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

2. Replace mock data calls with actual API calls:
```typescript
const response = await fetch(
  `${process.env.NEXT_PUBLIC_API_URL}/contracts/{id}`,
  { headers: { "Content-Type": "application/json" } }
);
const analysis = await response.json();
```

3. Update components to use real API responses instead of mock data.

## 📝 Implementation Notes

- **Reusable Components**: All components are modular and can be composed
- **Tailwind CSS**: No external UI libraries - pure utility-first CSS
- **Type Safety**: Full TypeScript with strict mode enabled
- **Mock Data**: Comprehensive mock data for development without backend
- **Responsive Grid**: Auto-adjusts from mobile to desktop layouts
- **Color System**: Uses Tailwind color palette for consistency
