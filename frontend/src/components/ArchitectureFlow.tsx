import {
  Database,
  FileText,
  Cpu,
  Search,
  Sparkles,
  Shield,
  ArrowRight,
  CheckCircle2,
  Server,
  Globe,
  Layers,
} from 'lucide-react';

interface FlowStep {
  icon: React.ElementType;
  title: string;
  description: string;
  tech: string;
  color: 'blue' | 'green' | 'purple' | 'amber' | 'red' | 'cyan';
}

const flowSteps: FlowStep[] = [
  {
    icon: FileText,
    title: 'PDF Ingestion',
    description: 'Parse BIS standard PDFs page-by-page with 10% overlap for context preservation',
    tech: 'pdfplumber',
    color: 'blue',
  },
  {
    icon: Layers,
    title: 'Chunking & Embedding',
    description: 'Generate dense vector embeddings using SentenceTransformers for each text chunk',
    tech: 'all-MiniLM-L6-v2',
    color: 'purple',
  },
  {
    icon: Database,
    title: 'Vector Store',
    description: 'Store embeddings in ChromaDB for fast similarity search with metadata filtering',
    tech: 'ChromaDB',
    color: 'green',
  },
  {
    icon: Search,
    title: 'Similarity Retrieval',
    description: 'Retrieve top-5 most relevant chunks using cosine similarity from the vector store',
    tech: 'ChromaDB Query',
    color: 'cyan',
  },
  {
    icon: Cpu,
    title: 'LLM Reasoning',
    description: 'Pass retrieved context to Groq LLM with strict no-hallucination prompt instructions',
    tech: 'llama3-70b-8192',
    color: 'amber',
  },
  {
    icon: Shield,
    title: 'Structured Output',
    description: 'Enforce Pydantic schema validation on LLM output with fallback error handling',
    tech: 'Pydantic + Langchain',
    color: 'red',
  },
];

const techStack = [
  { name: 'Python 3.11+', category: 'Language', color: 'bg-blue-100 text-blue-700' },
  { name: 'FastAPI', category: 'Web Framework', color: 'bg-teal-100 text-teal-700' },
  { name: 'Streamlit', category: 'UI Framework', color: 'bg-red-100 text-red-700' },
  { name: 'ChromaDB', category: 'Vector Database', color: 'bg-green-100 text-green-700' },
  { name: 'SentenceTransformers', category: 'Embeddings', color: 'bg-purple-100 text-purple-700' },
  { name: 'Groq API', category: 'LLM Inference', color: 'bg-amber-100 text-amber-700' },
  { name: 'Langchain', category: 'Orchestration', color: 'bg-indigo-100 text-indigo-700' },
  { name: 'Pydantic', category: 'Validation', color: 'bg-pink-100 text-pink-700' },
];

const fileStructure = [
  { path: 'inference.py', desc: 'Mandatory entry point for automated evaluation', important: true },
  { path: 'src/config.py', desc: 'Environment variables and constants', important: false },
  { path: 'src/ingest.py', desc: 'PDF parsing and ChromaDB population', important: false },
  { path: 'src/rag_engine.py', desc: 'Retrieval + Groq LLM pipeline with Pydantic schemas', important: true },
  { path: 'src/api.py', desc: 'FastAPI application endpoints', important: false },
  { path: 'src/app.py', desc: 'Streamlit frontend UI', important: false },
  { path: 'eval_script.py', desc: 'Evaluation harness placeholder', important: false },
  { path: 'requirements.txt', desc: 'Python dependencies', important: false },
];

const colorMap: Record<string, { bg: string; iconBg: string; iconText: string; border: string; line: string }> = {
  blue: { bg: 'bg-blue-50', iconBg: 'bg-blue-100', iconText: 'text-blue-600', border: 'border-blue-200', line: 'bg-blue-400' },
  green: { bg: 'bg-green-50', iconBg: 'bg-green-100', iconText: 'text-green-600', border: 'border-green-200', line: 'bg-green-400' },
  purple: { bg: 'bg-purple-50', iconBg: 'bg-purple-100', iconText: 'text-purple-600', border: 'border-purple-200', line: 'bg-purple-400' },
  amber: { bg: 'bg-amber-50', iconBg: 'bg-amber-100', iconText: 'text-amber-600', border: 'border-amber-200', line: 'bg-amber-400' },
  red: { bg: 'bg-red-50', iconBg: 'bg-red-100', iconText: 'text-red-600', border: 'border-red-200', line: 'bg-red-400' },
  cyan: { bg: 'bg-cyan-50', iconBg: 'bg-cyan-100', iconText: 'text-cyan-600', border: 'border-cyan-200', line: 'bg-cyan-400' },
};

export default function ArchitectureFlow() {
  return (
    <div className="space-y-8">
      {/* System Overview */}
      <div className="bg-white rounded-2xl shadow-lg border border-surface-200 overflow-hidden">
        <div className="bg-gradient-to-r from-primary-800 via-primary-700 to-primary-600 px-6 py-5">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-white/15 rounded-lg">
              <Server className="w-5 h-5 text-white" />
            </div>
            <h2 className="text-xl font-bold text-white">System Architecture</h2>
          </div>
          <p className="text-primary-200 text-sm">
            End-to-end RAG pipeline for BIS Standards Recommendation Engine
          </p>
        </div>

        {/* Pipeline Flow */}
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {flowSteps.map((step, index) => {
              const c = colorMap[step.color];
              const Icon = step.icon;
              return (
                <div key={index} className="relative">
                  <div
                    className={`${c.bg} border ${c.border} rounded-xl p-4 h-full animate-fade-in relative overflow-hidden`}
                    style={{ animationDelay: `${index * 100}ms` }}
                  >
                    {/* Step number */}
                    <div className="absolute top-2 right-2 w-6 h-6 rounded-full bg-white/60 flex items-center justify-center text-xs font-bold text-surface-500">
                      {index + 1}
                    </div>

                    <div className={`${c.iconBg} w-fit p-2 rounded-lg mb-3`}>
                      <Icon className={`w-5 h-5 ${c.iconText}`} />
                    </div>
                    <h3 className="font-bold text-surface-800 mb-1">{step.title}</h3>
                    <p className="text-xs text-surface-600 leading-relaxed mb-2">{step.description}</p>
                    <div className="flex items-center gap-1.5">
                      <span className="text-xs font-mono font-medium bg-white/60 text-surface-600 px-2 py-0.5 rounded">
                        {step.tech}
                      </span>
                    </div>
                  </div>

                  {/* Arrow connector (visible on larger screens between items) */}
                  {index < flowSteps.length - 1 && (index + 1) % 3 !== 0 && (
                    <div className="hidden lg:flex absolute -right-3 top-1/2 -translate-y-1/2 z-10">
                      <ArrowRight className="w-5 h-5 text-surface-300" />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Tech Stack */}
      <div className="bg-white rounded-2xl shadow-md border border-surface-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-surface-100">
          <h3 className="font-bold text-surface-800 flex items-center gap-2">
            <Globe className="w-5 h-5 text-primary-600" />
            Technology Stack
          </h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {techStack.map((tech, index) => (
              <div
                key={index}
                className="text-center p-3 rounded-xl bg-surface-50 border border-surface-100 animate-fade-in"
                style={{ animationDelay: `${index * 60}ms` }}
              >
                <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold mb-2 ${tech.color}`}>
                  {tech.category}
                </span>
                <p className="text-sm font-bold text-surface-800">{tech.name}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* File Structure */}
      <div className="bg-white rounded-2xl shadow-md border border-surface-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-surface-100">
          <h3 className="font-bold text-surface-800 flex items-center gap-2">
            <FileText className="w-5 h-5 text-primary-600" />
            Project File Structure
          </h3>
        </div>
        <div className="p-6">
          <div className="space-y-2">
            {fileStructure.map((file, index) => (
              <div
                key={index}
                className={`flex items-center gap-3 px-4 py-2.5 rounded-lg transition-colors animate-fade-in ${
                  file.important
                    ? 'bg-primary-50 border border-primary-100'
                    : 'bg-surface-50 border border-surface-100'
                }`}
                style={{ animationDelay: `${index * 50}ms` }}
              >
                <div className="flex items-center gap-2 min-w-[180px]">
                  {file.important && <CheckCircle2 className="w-4 h-4 text-primary-500 shrink-0" />}
                  <code className="text-sm font-mono font-bold text-surface-800">{file.path}</code>
                </div>
                <span className="text-xs text-surface-500">{file.desc}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Inference Schema */}
      <div className="bg-white rounded-2xl shadow-md border border-surface-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-surface-100">
          <h3 className="font-bold text-surface-800 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-primary-600" />
            Mandatory JSON Schemas
          </h3>
        </div>
        <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Input Schema */}
          <div>
            <h4 className="text-xs font-semibold text-surface-500 uppercase tracking-wider mb-2">
              Input Schema (--input)
            </h4>
            <div className="bg-surface-900 rounded-xl p-4 text-xs font-mono text-green-400 overflow-x-auto">
              <pre>{`[
  {
    "id": "q1",
    "query": "Product description..."
  },
  {
    "id": "q2",
    "query": "Another product..."
  }
]`}</pre>
            </div>
          </div>

          {/* Output Schema */}
          <div>
            <h4 className="text-xs font-semibold text-surface-500 uppercase tracking-wider mb-2">
              Output Schema (--output)
            </h4>
            <div className="bg-surface-900 rounded-xl p-4 text-xs font-mono text-green-400 overflow-x-auto">
              <pre>{`[
  {
    "id": "q1",
    "retrieved_standards": [
      "IS 694:2010",
      "IS 1554:1988"
    ],
    "latency_seconds": 1.847
  }
]`}</pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
