# OrkestrAI - Frontend Architecture

## Frontend Folder Structure

```
frontend/
├── public/
│   ├── favicon.ico
│   ├── logo.svg
│   └── agents/                      # Agent avatar images
│       ├── strategy-agent.svg
│       ├── architecture-agent.svg
│       ├── code-builder-agent.svg
│       ├── github-agent.svg
│       └── pitch-agent.svg
│
├── src/
│   ├── app/
│   │   ├── layout.tsx               # Root layout with providers
│   │   ├── page.tsx                 # Landing page
│   │   ├── globals.css              # Global styles + Tailwind
│   │   │
│   │   ├── dashboard/
│   │   │   ├── page.tsx             # Projects dashboard
│   │   │   └── layout.tsx
│   │   │
│   │   ├── create/
│   │   │   └── page.tsx             # Create new project form
│   │   │
│   │   ├── project/
│   │   │   └── [id]/
│   │   │       ├── page.tsx         # Project orchestration view
│   │   │       └── results/
│   │   │           └── page.tsx     # Results & artifacts view
│   │   │
│   │   └── api/                     # API routes (if needed)
│   │       └── auth/
│   │           └── [...nextauth]/
│   │               └── route.ts
│   │
│   ├── components/
│   │   ├── ui/                      # Reusable UI components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── input.tsx
│   │   │   ├── badge.tsx
│   │   │   ├── progress.tsx
│   │   │   ├── tabs.tsx
│   │   │   ├── dialog.tsx
│   │   │   └── skeleton.tsx
│   │   │
│   │   ├── layout/
│   │   │   ├── header.tsx
│   │   │   ├── footer.tsx
│   │   │   └── sidebar.tsx
│   │   │
│   │   ├── orchestration/           # Orchestration-specific components
│   │   │   ├── agent-panel.tsx      # Agent avatars & status
│   │   │   ├── agent-card.tsx       # Individual agent card
│   │   │   ├── activity-timeline.tsx # Vertical timeline
│   │   │   ├── code-stream.tsx      # Live code generation
│   │   │   ├── progress-tracker.tsx # Overall progress
│   │   │   ├── output-preview.tsx   # Real-time output
│   │   │   └── workflow-diagram.tsx # Visual workflow
│   │   │
│   │   ├── project/
│   │   │   ├── project-card.tsx     # Project list item
│   │   │   ├── project-form.tsx     # Create project form
│   │   │   ├── project-header.tsx   # Project details header
│   │   │   └── artifact-viewer.tsx  # View generated artifacts
│   │   │
│   │   ├── results/
│   │   │   ├── strategy-view.tsx    # Strategy output display
│   │   │   ├── architecture-view.tsx # Architecture diagrams
│   │   │   ├── code-viewer.tsx      # Code with syntax highlighting
│   │   │   ├── github-view.tsx      # GitHub integration results
│   │   │   └── pitch-view.tsx       # Pitch materials
│   │   │
│   │   └── animations/
│   │       ├── particle-effect.tsx  # Particle connections
│   │       ├── typing-effect.tsx    # Typing animation
│   │       └── pulse-effect.tsx     # Pulsing indicators
│   │
│   ├── lib/
│   │   ├── api/
│   │   │   ├── client.ts            # API client setup
│   │   │   ├── projects.ts          # Project API calls
│   │   │   ├── orchestration.ts     # Orchestration API calls
│   │   │   └── github.ts            # GitHub API calls
│   │   │
│   │   ├── websocket/
│   │   │   ├── client.ts            # WebSocket client
│   │   │   └── hooks.ts             # WebSocket React hooks
│   │   │
│   │   ├── store/
│   │   │   ├── index.ts             # Zustand store setup
│   │   │   ├── project-store.ts     # Project state
│   │   │   ├── orchestration-store.ts # Orchestration state
│   │   │   └── ui-store.ts          # UI state (modals, etc.)
│   │   │
│   │   └── utils/
│   │       ├── cn.ts                # Class name utility
│   │       ├── format.ts            # Formatting helpers
│   │       └── validators.ts        # Form validation
│   │
│   ├── hooks/
│   │   ├── use-orchestration.ts     # Orchestration logic hook
│   │   ├── use-websocket.ts         # WebSocket connection hook
│   │   ├── use-project.ts           # Project data hook
│   │   └── use-debounce.ts          # Debounce hook
│   │
│   ├── types/
│   │   ├── project.ts               # Project types
│   │   ├── agent.ts                 # Agent types
│   │   ├── orchestration.ts         # Orchestration types
│   │   └── api.ts                   # API response types
│   │
│   └── constants/
│       ├── agents.ts                # Agent configurations
│       ├── routes.ts                # Route constants
│       └── config.ts                # App configuration
│
├── .env.local.example
├── .eslintrc.json
├── .gitignore
├── next.config.js
├── package.json
├── postcss.config.js
├── tailwind.config.ts
├── tsconfig.json
└── README.md
```

## Component Architecture

### 1. Landing Page (`app/page.tsx`)

**Purpose**: Hero section with value proposition and CTA

**Key Features**:
- Animated hero section with gradient background
- Feature highlights with icons
- "Start Building" CTA button
- Demo video/GIF showcase
- Social proof (if available)

```tsx
export default function LandingPage() {
  return (
    <div className="min-h-screen">
      <Hero />
      <Features />
      <HowItWorks />
      <CTA />
    </div>
  );
}
```

### 2. Create Project Page (`app/create/page.tsx`)

**Purpose**: Form to input project idea and preferences

**Key Features**:
- Large textarea for project description
- Optional preferences (tech stack, deployment)
- Real-time character count
- Example prompts/templates
- "Start Orchestration" button

```tsx
export default function CreateProjectPage() {
  return (
    <div className="container max-w-4xl py-12">
      <ProjectForm onSubmit={handleCreateProject} />
    </div>
  );
}
```

### 3. Orchestration View (`app/project/[id]/page.tsx`)

**Purpose**: Real-time visualization of agent orchestration

**Layout Structure**:
```
┌─────────────────────────────────────────────────────┐
│                    Header                           │
│  Project Name | Progress: 60% | Status: Architecting│
└─────────────────────────────────────────────────────┘
┌──────────────┬──────────────────────────────────────┐
│              │                                      │
│   Agent      │        Main Content Area            │
│   Panel      │                                      │
│              │  ┌────────────────────────────────┐ │
│  [Strategy]  │  │   Activity Timeline            │ │
│  [Architect] │  │   - Agent started              │ │
│  [Builder]   │  │   - Analyzing requirements     │ │
│  [GitHub]    │  │   - Generating architecture    │ │
│  [Pitch]     │  └────────────────────────────────┘ │
│              │                                      │
│              │  ┌────────────────────────────────┐ │
│              │  │   Code Stream                  │ │
│              │  │   (Live code generation)       │ │
│              │  └────────────────────────────────┘ │
│              │                                      │
└──────────────┴──────────────────────────────────────┘
```

**Key Components**:
- [`AgentPanel`](src/components/orchestration/agent-panel.tsx): Left sidebar with agent avatars
- [`ActivityTimeline`](src/components/orchestration/activity-timeline.tsx): Center timeline of events
- [`CodeStream`](src/components/orchestration/code-stream.tsx): Live code generation display
- [`ProgressTracker`](src/components/orchestration/progress-tracker.tsx): Top progress bar
- [`OutputPreview`](src/components/orchestration/output-preview.tsx): Real-time output cards

### 4. Results Page (`app/project/[id]/results/page.tsx`)

**Purpose**: Display all generated artifacts

**Layout Structure**:
```
┌─────────────────────────────────────────────────────┐
│                  Project Header                     │
│  Name | Status: Completed | Download All            │
└─────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────┐
│                    Tabs                             │
│  Strategy | Architecture | Code | GitHub | Pitch    │
└─────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────┐
│                                                     │
│              Tab Content Area                       │
│                                                     │
│  (Displays selected artifact with formatting)      │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## State Management with Zustand

### Project Store

```typescript
// lib/store/project-store.ts
import { create } from 'zustand';
import { Project } from '@/types/project';

interface ProjectState {
  projects: Project[];
  currentProject: Project | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setProjects: (projects: Project[]) => void;
  setCurrentProject: (project: Project) => void;
  addProject: (project: Project) => void;
  updateProject: (id: string, updates: Partial<Project>) => void;
  deleteProject: (id: string) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useProjectStore = create<ProjectState>((set) => ({
  projects: [],
  currentProject: null,
  isLoading: false,
  error: null,
  
  setProjects: (projects) => set({ projects }),
  setCurrentProject: (project) => set({ currentProject: project }),
  addProject: (project) => set((state) => ({ 
    projects: [...state.projects, project] 
  })),
  updateProject: (id, updates) => set((state) => ({
    projects: state.projects.map(p => p.id === id ? { ...p, ...updates } : p),
    currentProject: state.currentProject?.id === id 
      ? { ...state.currentProject, ...updates } 
      : state.currentProject
  })),
  deleteProject: (id) => set((state) => ({
    projects: state.projects.filter(p => p.id !== id)
  })),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error })
}));
```

### Orchestration Store

```typescript
// lib/store/orchestration-store.ts
import { create } from 'zustand';
import { AgentLog, OrchestrationStatus } from '@/types/orchestration';

interface OrchestrationState {
  status: OrchestrationStatus;
  currentAgent: string | null;
  progress: number;
  logs: AgentLog[];
  outputs: Record<string, any>;
  
  // Actions
  setStatus: (status: OrchestrationStatus) => void;
  setCurrentAgent: (agent: string | null) => void;
  setProgress: (progress: number) => void;
  addLog: (log: AgentLog) => void;
  setOutput: (agentName: string, output: any) => void;
  reset: () => void;
}

export const useOrchestrationStore = create<OrchestrationState>((set) => ({
  status: 'idle',
  currentAgent: null,
  progress: 0,
  logs: [],
  outputs: {},
  
  setStatus: (status) => set({ status }),
  setCurrentAgent: (agent) => set({ currentAgent: agent }),
  setProgress: (progress) => set({ progress }),
  addLog: (log) => set((state) => ({ 
    logs: [...state.logs, log] 
  })),
  setOutput: (agentName, output) => set((state) => ({
    outputs: { ...state.outputs, [agentName]: output }
  })),
  reset: () => set({
    status: 'idle',
    currentAgent: null,
    progress: 0,
    logs: [],
    outputs: {}
  })
}));
```

## WebSocket Integration

### WebSocket Hook

```typescript
// hooks/use-websocket.ts
import { useEffect, useRef } from 'react';
import { useOrchestrationStore } from '@/lib/store/orchestration-store';

export function useWebSocket(projectId: string) {
  const wsRef = useRef<WebSocket | null>(null);
  const { addLog, setStatus, setCurrentAgent, setProgress, setOutput } = useOrchestrationStore();
  
  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/orchestration/${projectId}`);
    wsRef.current = ws;
    
    ws.onopen = () => {
      console.log('WebSocket connected');
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      switch (data.type) {
        case 'agent_start':
          setCurrentAgent(data.agent);
          addLog({
            id: crypto.randomUUID(),
            agent: data.agent,
            action: 'Started',
            status: 'started',
            timestamp: data.timestamp
          });
          break;
          
        case 'agent_thinking':
          addLog({
            id: crypto.randomUUID(),
            agent: data.agent,
            action: data.message,
            status: 'thinking',
            timestamp: data.timestamp
          });
          break;
          
        case 'agent_output':
          setOutput(data.agent, data.data);
          break;
          
        case 'agent_complete':
          addLog({
            id: crypto.randomUUID(),
            agent: data.agent,
            action: 'Completed',
            status: 'completed',
            timestamp: data.timestamp,
            duration: data.duration_ms
          });
          break;
          
        case 'orchestration_complete':
          setStatus('completed');
          setCurrentAgent(null);
          setProgress(100);
          break;
          
        case 'error':
          setStatus('failed');
          addLog({
            id: crypto.randomUUID(),
            agent: data.agent,
            action: data.error,
            status: 'failed',
            timestamp: data.timestamp
          });
          break;
      }
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setStatus('failed');
    };
    
    ws.onclose = () => {
      console.log('WebSocket disconnected');
    };
    
    return () => {
      ws.close();
    };
  }, [projectId]);
  
  return wsRef;
}
```

## Key UI Components

### 1. Agent Panel Component

```tsx
// components/orchestration/agent-panel.tsx
import { AgentCard } from './agent-card';
import { AGENTS } from '@/constants/agents';

export function AgentPanel({ currentAgent }: { currentAgent: string | null }) {
  return (
    <div className="w-64 bg-gray-50 border-r p-4 space-y-4">
      <h2 className="text-lg font-semibold">AI Agents</h2>
      {AGENTS.map((agent) => (
        <AgentCard
          key={agent.name}
          agent={agent}
          isActive={currentAgent === agent.name}
          status={getAgentStatus(agent.name, currentAgent)}
        />
      ))}
    </div>
  );
}
```

### 2. Activity Timeline Component

```tsx
// components/orchestration/activity-timeline.tsx
import { AgentLog } from '@/types/orchestration';
import { formatDistanceToNow } from 'date-fns';

export function ActivityTimeline({ logs }: { logs: AgentLog[] }) {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Activity Timeline</h3>
      <div className="relative">
        {/* Vertical line */}
        <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200" />
        
        {logs.map((log, index) => (
          <div key={log.id} className="relative pl-12 pb-8">
            {/* Dot */}
            <div className={`absolute left-2.5 w-3 h-3 rounded-full ${
              log.status === 'completed' ? 'bg-green-500' :
              log.status === 'failed' ? 'bg-red-500' :
              log.status === 'thinking' ? 'bg-blue-500 animate-pulse' :
              'bg-gray-400'
            }`} />
            
            {/* Content */}
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium">{log.agent}</span>
                <span className="text-xs text-gray-500">
                  {formatDistanceToNow(new Date(log.timestamp), { addSuffix: true })}
                </span>
              </div>
              <p className="text-sm text-gray-600">{log.action}</p>
              {log.duration && (
                <p className="text-xs text-gray-400 mt-1">
                  Completed in {log.duration}ms
                </p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

### 3. Code Stream Component

```tsx
// components/orchestration/code-stream.tsx
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

export function CodeStream({ code, language }: { code: string; language: string }) {
  return (
    <div className="bg-gray-900 rounded-lg overflow-hidden">
      <div className="flex items-center justify-between px-4 py-2 bg-gray-800">
        <span className="text-sm text-gray-300">Live Code Generation</span>
        <span className="text-xs text-gray-500">{language}</span>
      </div>
      <div className="p-4 overflow-auto max-h-96">
        <SyntaxHighlighter
          language={language}
          style={vscDarkPlus}
          showLineNumbers
          wrapLines
        >
          {code}
        </SyntaxHighlighter>
      </div>
    </div>
  );
}
```

## Styling with Tailwind CSS

### Custom Theme Configuration

```typescript
// tailwind.config.ts
import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
        },
        agent: {
          strategy: '#8b5cf6',
          architecture: '#3b82f6',
          builder: '#10b981',
          github: '#f59e0b',
          pitch: '#ec4899',
        }
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'slide-in': 'slideIn 0.3s ease-out',
        'fade-in': 'fadeIn 0.5s ease-out',
      },
      keyframes: {
        slideIn: {
          '0%': { transform: 'translateX(-100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
};

export default config;
```

## Performance Optimizations

### 1. Code Splitting
- Use dynamic imports for heavy components
- Lazy load syntax highlighter
- Split agent visualization components

### 2. Memoization
- Memoize expensive calculations
- Use React.memo for pure components
- Optimize re-renders with useMemo/useCallback

### 3. Virtual Scrolling
- Implement virtual scrolling for long activity timelines
- Use react-window for large lists

### 4. Image Optimization
- Use Next.js Image component
- Optimize agent avatars
- Lazy load images

## Responsive Design

### Breakpoints
- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: > 1024px

### Mobile Adaptations
- Stack agent panel below main content
- Collapsible timeline
- Simplified visualizations
- Touch-friendly interactions

## Accessibility

### WCAG 2.1 AA Compliance
- Semantic HTML
- ARIA labels
- Keyboard navigation
- Focus indicators
- Color contrast ratios
- Screen reader support

## Dependencies

```json
{
  "dependencies": {
    "next": "14.1.0",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "zustand": "4.5.0",
    "tailwindcss": "3.4.1",
    "framer-motion": "11.0.3",
    "react-syntax-highlighter": "15.5.0",
    "date-fns": "3.3.1",
    "lucide-react": "0.323.0",
    "class-variance-authority": "0.7.0",
    "clsx": "2.1.0",
    "tailwind-merge": "2.2.1"
  },
  "devDependencies": {
    "@types/node": "20.11.5",
    "@types/react": "18.2.48",
    "@types/react-dom": "18.2.18",
    "typescript": "5.3.3",
    "eslint": "8.56.0",
    "eslint-config-next": "14.1.0",
    "autoprefixer": "10.4.17",
    "postcss": "8.4.33"
  }
}