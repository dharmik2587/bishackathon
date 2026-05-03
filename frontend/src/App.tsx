import { useState } from 'react';
import {
  Search,
  BarChart3,
  Server,
  BookOpen,
  Shield,
  Cpu,
  Zap,
  Code2,
  ExternalLink,
} from 'lucide-react';
import QueryEngine from './components/QueryEngine';
import Dashboard from './components/Dashboard';
import ArchitectureFlow from './components/ArchitectureFlow';
import { TabId } from './types';

const tabs: { id: TabId; label: string; icon: React.ElementType; description: string }[] = [
  { id: 'query', label: 'Query Engine', icon: Search, description: 'Interactive RAG query interface' },
  { id: 'dashboard', label: 'Evaluation Dashboard', icon: BarChart3, description: 'Metrics & batch evaluation' },
  { id: 'architecture', label: 'Architecture', icon: Server, description: 'System design & tech stack' },
];

export default function App() {
  const [activeTab, setActiveTab] = useState<TabId>('query');

  return (
    <div className="min-h-screen bg-gradient-to-br from-surface-50 via-white to-primary-50/30">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-lg border-b border-surface-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="flex items-center justify-between h-16">
            {/* Logo & Title */}
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="w-10 h-10 bg-gradient-to-br from-primary-600 to-primary-700 rounded-xl flex items-center justify-center shadow-lg shadow-primary-200">
                  <BookOpen className="w-5 h-5 text-white" />
                </div>
                <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-accent-400 rounded-full border-2 border-white" />
              </div>
              <div>
                <h1 className="text-lg font-black text-surface-900 leading-tight">
                  BIS Standards
                  <span className="gradient-text ml-1">RAG Engine</span>
                </h1>
                <p className="text-xs text-surface-400 font-medium">
                  Recommendation Engine Prototype
                </p>
              </div>
            </div>

            {/* Status Indicators */}
            <div className="hidden sm:flex items-center gap-4">
              <div className="flex items-center gap-1.5 text-xs font-medium text-accent-600 bg-accent-50 px-3 py-1.5 rounded-full border border-accent-200">
                <Shield className="w-3.5 h-3.5" />
                No Hallucination
              </div>
              <div className="flex items-center gap-1.5 text-xs font-medium text-primary-600 bg-primary-50 px-3 py-1.5 rounded-full border border-primary-200">
                <Cpu className="w-3.5 h-3.5" />
                Groq Powered
              </div>
              <div className="flex items-center gap-1.5 text-xs font-medium text-amber-600 bg-amber-50 px-3 py-1.5 rounded-full border border-amber-200">
                <Zap className="w-3.5 h-3.5" />
                &lt;5s Latency
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-white/60 backdrop-blur-sm border-b border-surface-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="flex gap-1 py-2">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold transition-all
                    ${
                      isActive
                        ? 'bg-primary-600 text-white shadow-lg shadow-primary-200'
                        : 'text-surface-600 hover:bg-surface-100 hover:text-surface-800'
                    }
                  `}
                >
                  <Icon className="w-4 h-4" />
                  <span className="hidden sm:inline">{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
        {/* Tab description */}
        <div className="mb-6">
          {tabs.map(
            (tab) =>
              activeTab === tab.id && (
                <p key={tab.id} className="text-sm text-surface-500 animate-fade-in">
                  {tab.description}
                </p>
              )
          )}
        </div>

        {/* Tab Content */}
        <div className="animate-fade-in">
          {activeTab === 'query' && <QueryEngine />}
          {activeTab === 'dashboard' && <Dashboard />}
          {activeTab === 'architecture' && <ArchitectureFlow />}
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-surface-200 bg-white/50 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2 text-sm text-surface-500">
              <BookOpen className="w-4 h-4 text-primary-500" />
              <span className="font-semibold">BIS Standards Recommendation Engine</span>
              <span className="text-surface-300">|</span>
              <span>RAG Prototype for Hackathon</span>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-3 text-xs text-surface-400">
                <span className="flex items-center gap-1">
                  <Shield className="w-3 h-3" /> Hit Rate @3: &gt;80%
                </span>
                <span className="text-surface-300">•</span>
                <span className="flex items-center gap-1">
                  <Zap className="w-3 h-3" /> MRR @5: &gt;0.7
                </span>
                <span className="text-surface-300">•</span>
                <span className="flex items-center gap-1">
                  <Cpu className="w-3 h-3" /> Latency: &lt;5s
                </span>
              </div>
              <div className="flex items-center gap-2">
                <button className="p-1.5 text-surface-400 hover:text-surface-600 transition-colors rounded-lg hover:bg-surface-100">
                  <Code2 className="w-4 h-4" />
                </button>
                <button className="p-1.5 text-surface-400 hover:text-surface-600 transition-colors rounded-lg hover:bg-surface-100">
                  <ExternalLink className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
