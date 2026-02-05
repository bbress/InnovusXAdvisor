import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Layers,
  GitBranch,
  Shield,
  BarChart3,
  Database,
  Brain,
  Cpu,
  CheckCircle2,
  AlertCircle,
  Activity
} from 'lucide-react'

type TabId = 'architecture' | 'mlops' | 'governance' | 'evaluation'

interface Tab {
  id: TabId
  label: string
  icon: React.ReactNode
}

const TABS: Tab[] = [
  { id: 'architecture', label: 'Architecture', icon: <Layers className="w-4 h-4" /> },
  { id: 'mlops', label: 'MLOps', icon: <GitBranch className="w-4 h-4" /> },
  { id: 'governance', label: 'Governance', icon: <Shield className="w-4 h-4" /> },
  { id: 'evaluation', label: 'Evaluation', icon: <BarChart3 className="w-4 h-4" /> },
]

export function UnderTheHood() {
  const [activeTab, setActiveTab] = useState<TabId>('architecture')

  return (
    <div className="h-[600px] flex flex-col">
      {/* Header */}
      <div className="p-4 border-b bg-gradient-to-r from-slate-700 to-slate-800">
        <div className="flex items-center gap-2 text-white">
          <Cpu className="w-5 h-5" />
          <h2 className="font-semibold">Under the Hood</h2>
        </div>
        <p className="text-slate-300 text-sm mt-1">
          Explore the AI/ML platform powering this demo
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex-1 px-3 py-2.5 text-sm font-medium flex items-center justify-center gap-1.5 transition-colors ${
              activeTab === tab.id
                ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
            }`}
          >
            {tab.icon}
            <span className="hidden sm:inline">{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto custom-scrollbar">
        <AnimatePresence mode="wait">
          {activeTab === 'architecture' && <ArchitecturePanel key="arch" />}
          {activeTab === 'mlops' && <MLOpsPanel key="mlops" />}
          {activeTab === 'governance' && <GovernancePanel key="gov" />}
          {activeTab === 'evaluation' && <EvaluationPanel key="eval" />}
        </AnimatePresence>
      </div>
    </div>
  )
}

function ArchitecturePanel() {
  const components = [
    { name: 'Data Layer', icon: <Database className="w-4 h-4" />, status: 'healthy', metric: '847 docs' },
    { name: 'RAG Engine', icon: <Brain className="w-4 h-4" />, status: 'healthy', metric: '45ms avg' },
    { name: 'Agent Orchestrator', icon: <Cpu className="w-4 h-4" />, status: 'healthy', metric: '3 agents' },
    { name: 'LLM Gateway', icon: <Activity className="w-4 h-4" />, status: 'healthy', metric: 'GPT-4' },
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="p-4"
    >
      <h3 className="font-medium text-gray-900 mb-3">Platform Architecture</h3>

      {/* Pipeline visualization */}
      <div className="bg-slate-50 rounded-lg p-4 mb-4">
        <div className="flex items-center justify-between text-xs">
          {['Input', 'RAG', 'Agents', 'LLM', 'Output'].map((stage, i, arr) => (
            <div key={stage} className="flex items-center">
              <div className="px-2 py-1 bg-blue-100 text-blue-700 rounded font-medium">
                {stage}
              </div>
              {i < arr.length - 1 && (
                <div className="w-4 h-px bg-blue-300 mx-1" />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Components */}
      <div className="space-y-2">
        {components.map((comp, i) => (
          <motion.div
            key={comp.name}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.1 }}
            className="flex items-center justify-between p-3 bg-white border rounded-lg"
          >
            <div className="flex items-center gap-2">
              <div className="p-1.5 bg-slate-100 rounded">
                {comp.icon}
              </div>
              <span className="font-medium text-sm">{comp.name}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-500">{comp.metric}</span>
              <CheckCircle2 className="w-4 h-4 text-green-500" />
            </div>
          </motion.div>
        ))}
      </div>

      <div className="mt-4 p-3 bg-blue-50 rounded-lg">
        <p className="text-xs text-blue-700">
          <strong>Architecture Highlight:</strong> Modular design enables independent scaling
          of each component. RAG provides context, agents handle reasoning, LLM gateway
          manages inference with automatic fallback.
        </p>
      </div>
    </motion.div>
  )
}

function MLOpsPanel() {
  const pipelineStages = [
    { name: 'Data Validation', status: 'success', time: '2h ago' },
    { name: 'Embedding Generation', status: 'success', time: '2h ago' },
    { name: 'Model Evaluation', status: 'success', time: '7d ago' },
    { name: 'Model Deployment', status: 'success', time: '7d ago' },
  ]

  const modelVersions = [
    { version: 'v2.3', status: 'active', score: 0.92 },
    { version: 'v2.2', status: 'archived', score: 0.89 },
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="p-4"
    >
      <h3 className="font-medium text-gray-900 mb-3">MLOps Pipeline</h3>

      {/* Pipeline status */}
      <div className="bg-slate-50 rounded-lg p-3 mb-4">
        <div className="text-xs font-medium text-gray-500 mb-2">Pipeline Status</div>
        <div className="space-y-2">
          {pipelineStages.map((stage) => (
            <div key={stage.name} className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-green-500" />
                <span className="text-sm">{stage.name}</span>
              </div>
              <span className="text-xs text-gray-400">{stage.time}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Model registry */}
      <div className="mb-4">
        <div className="text-xs font-medium text-gray-500 mb-2">Model Registry</div>
        <div className="space-y-2">
          {modelVersions.map((model) => (
            <div
              key={model.version}
              className={`flex items-center justify-between p-2 rounded-lg ${
                model.status === 'active' ? 'bg-green-50 border border-green-200' : 'bg-gray-50'
              }`}
            >
              <div className="flex items-center gap-2">
                <span className="font-mono text-sm">{model.version}</span>
                {model.status === 'active' && (
                  <span className="px-1.5 py-0.5 text-xs bg-green-100 text-green-700 rounded">
                    Production
                  </span>
                )}
              </div>
              <span className="text-sm text-gray-600">
                Score: {(model.score * 100).toFixed(0)}%
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Drift detection */}
      <div className="p-3 bg-emerald-50 rounded-lg">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-medium text-emerald-700">Drift Detection</span>
          <span className="text-xs text-emerald-600">Healthy</span>
        </div>
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div>
            <span className="text-gray-500">Embedding Drift:</span>
            <span className="ml-1 font-medium">0.02</span>
          </div>
          <div>
            <span className="text-gray-500">Prediction Drift:</span>
            <span className="ml-1 font-medium">0.04</span>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

function GovernancePanel() {
  const controls = [
    { name: 'Audit Logging', enabled: true, coverage: '100%' },
    { name: 'PII Detection', enabled: true, coverage: '100%' },
    { name: 'Access Control', enabled: true, coverage: 'RBAC' },
    { name: 'Bias Monitoring', enabled: true, coverage: '0.02 score' },
  ]

  const auditTrail = [
    { time: '09:42:01', action: 'Request received', status: 'success' },
    { time: '09:42:01', action: 'PII scan completed', status: 'success' },
    { time: '09:42:02', action: 'RAG retrieval', status: 'success' },
    { time: '09:42:03', action: 'LLM inference', status: 'success' },
    { time: '09:42:03', action: 'Response delivered', status: 'success' },
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="p-4"
    >
      <h3 className="font-medium text-gray-900 mb-3">Compliance & Governance</h3>

      {/* Controls */}
      <div className="grid grid-cols-2 gap-2 mb-4">
        {controls.map((control) => (
          <div key={control.name} className="p-2 bg-slate-50 rounded-lg">
            <div className="flex items-center gap-1.5 mb-1">
              <CheckCircle2 className="w-3.5 h-3.5 text-green-500" />
              <span className="text-xs font-medium">{control.name}</span>
            </div>
            <span className="text-xs text-gray-500">{control.coverage}</span>
          </div>
        ))}
      </div>

      {/* Audit trail */}
      <div className="mb-4">
        <div className="text-xs font-medium text-gray-500 mb-2">Sample Audit Trail</div>
        <div className="bg-slate-900 rounded-lg p-3 font-mono text-xs text-slate-300 space-y-1">
          {auditTrail.map((entry, i) => (
            <div key={i} className="flex gap-2">
              <span className="text-slate-500">{entry.time}</span>
              <span className="text-green-400">✓</span>
              <span>{entry.action}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="p-3 bg-purple-50 rounded-lg">
        <p className="text-xs text-purple-700">
          <strong>Governance Highlight:</strong> Every request is logged with full audit trail.
          PII is automatically detected and redacted. Bias monitoring runs continuously with
          alerts on threshold violations.
        </p>
      </div>
    </motion.div>
  )
}

function EvaluationPanel() {
  const metrics = [
    { name: 'Relevance', score: 0.89, target: 0.85 },
    { name: 'Groundedness', score: 0.94, target: 0.90 },
    { name: 'Coherence', score: 0.91, target: 0.85 },
    { name: 'Actionability', score: 0.85, target: 0.80 },
  ]

  const approaches = [
    { method: 'RAG + GPT-4', quality: 94, latency: '1.2s', cost: '$0.04', current: true },
    { method: 'Fine-tuned', quality: 89, latency: '0.8s', cost: '$0.01', current: false },
    { method: 'Prompt-only', quality: 76, latency: '0.9s', cost: '$0.03', current: false },
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="p-4"
    >
      <h3 className="font-medium text-gray-900 mb-3">Quality Evaluation</h3>

      {/* Quality metrics */}
      <div className="space-y-3 mb-4">
        {metrics.map((metric) => (
          <div key={metric.name}>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-600">{metric.name}</span>
              <span className="font-medium">{(metric.score * 100).toFixed(0)}%</span>
            </div>
            <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${metric.score * 100}%` }}
                transition={{ duration: 0.5 }}
                className={`h-full rounded-full ${
                  metric.score >= metric.target
                    ? 'bg-gradient-to-r from-green-400 to-emerald-500'
                    : 'bg-gradient-to-r from-amber-400 to-orange-500'
                }`}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Approach comparison */}
      <div className="mb-4">
        <div className="text-xs font-medium text-gray-500 mb-2">Approach Comparison</div>
        <div className="overflow-hidden rounded-lg border">
          <table className="w-full text-xs">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-2 py-1.5 text-left font-medium text-gray-600">Method</th>
                <th className="px-2 py-1.5 text-center font-medium text-gray-600">Quality</th>
                <th className="px-2 py-1.5 text-center font-medium text-gray-600">Latency</th>
                <th className="px-2 py-1.5 text-center font-medium text-gray-600">Cost</th>
              </tr>
            </thead>
            <tbody>
              {approaches.map((approach) => (
                <tr
                  key={approach.method}
                  className={approach.current ? 'bg-blue-50' : ''}
                >
                  <td className="px-2 py-1.5 border-t">
                    {approach.method}
                    {approach.current && (
                      <span className="ml-1 text-blue-600">←</span>
                    )}
                  </td>
                  <td className="px-2 py-1.5 border-t text-center">{approach.quality}%</td>
                  <td className="px-2 py-1.5 border-t text-center">{approach.latency}</td>
                  <td className="px-2 py-1.5 border-t text-center">{approach.cost}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="p-3 bg-amber-50 rounded-lg">
        <p className="text-xs text-amber-700">
          <strong>Evaluation Insight:</strong> RAG approach provides best quality-cost tradeoff.
          Fine-tuning offers lower latency but requires ongoing training investment.
          Continuous evaluation ensures production quality stays above thresholds.
        </p>
      </div>
    </motion.div>
  )
}
