import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Sparkles,
  Building2,
  Target,
  Rocket,
  ChevronRight,
  Loader2,
  CheckCircle2,
  ArrowRight
} from 'lucide-react'
import { StrategyCard } from './StrategyCard'

interface Strategy {
  id: string
  title: string
  category: string
  description: string
  confidence_score: number
  action_steps: {
    step_number: number
    title: string
    description: string
    timeline?: string
  }[]
  rationale: string
  potential_impact: string
  risk_factors: string[]
}

interface FormData {
  industry: string
  company_stage: string
  challenge: string
  focus_area: string
}

const INDUSTRIES = [
  { value: 'fintech', label: 'FinTech' },
  { value: 'healthtech', label: 'HealthTech' },
  { value: 'saas', label: 'SaaS' },
  { value: 'ecommerce', label: 'E-Commerce' },
  { value: 'retail', label: 'Retail' },
  { value: 'manufacturing', label: 'Manufacturing' },
  { value: 'logistics', label: 'Logistics' },
  { value: 'cleantech', label: 'CleanTech' },
]

const COMPANY_STAGES = [
  { value: 'startup', label: 'Startup' },
  { value: 'growth', label: 'Growth' },
  { value: 'scaleup', label: 'Scale-up' },
  { value: 'enterprise', label: 'Enterprise' },
]

const FOCUS_AREAS = [
  { value: 'market_expansion', label: 'Market Expansion' },
  { value: 'product_innovation', label: 'Product Innovation' },
  { value: 'operational_efficiency', label: 'Operations' },
  { value: 'partnerships', label: 'Partnerships' },
  { value: 'revenue_growth', label: 'Revenue Growth' },
]

export function StrategyLab() {
  const [step, setStep] = useState<'form' | 'loading' | 'results'>('form')
  const [formData, setFormData] = useState<FormData>({
    industry: '',
    company_stage: '',
    challenge: '',
    focus_area: '',
  })
  const [strategies, setStrategies] = useState<Strategy[]>([])
  const [selectedStrategy, setSelectedStrategy] = useState<Strategy | null>(null)
  const [metadata, setMetadata] = useState<any>(null)

  const handleSubmit = async () => {
    setStep('loading')

    try {
      // Call the demo endpoint
      const response = await fetch(
        `/api/v1/strategy/demo?industry=${formData.industry}&challenge=${encodeURIComponent(formData.challenge)}`
      )

      if (!response.ok) {
        throw new Error('Failed to generate strategies')
      }

      const data = await response.json()
      setStrategies(data.strategies)
      setMetadata(data.metadata)
      setStep('results')
    } catch (error) {
      // Use mock data for demo
      setTimeout(() => {
        setStrategies(getMockStrategies())
        setMetadata({
          correlation_id: 'demo-' + Date.now(),
          model_version: 'v2.3',
          latency_ms: 1250,
          tokens_used: 856,
          retrieval_count: 12
        })
        setStep('results')
      }, 2000)
    }
  }

  const handleReset = () => {
    setStep('form')
    setFormData({
      industry: '',
      company_stage: '',
      challenge: '',
      focus_area: '',
    })
    setStrategies([])
    setSelectedStrategy(null)
  }

  return (
    <div className="h-[600px] flex flex-col">
      {/* Header */}
      <div className="p-4 border-b bg-gradient-to-r from-blue-600 to-indigo-600">
        <div className="flex items-center gap-2 text-white">
          <Sparkles className="w-5 h-5" />
          <h2 className="font-semibold">Strategy Generator</h2>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden">
        <AnimatePresence mode="wait">
          {step === 'form' && (
            <motion.div
              key="form"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="h-full p-4 overflow-y-auto custom-scrollbar"
            >
              <div className="space-y-4">
                {/* Industry */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    <Building2 className="w-4 h-4 inline mr-1" />
                    Industry
                  </label>
                  <select
                    value={formData.industry}
                    onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Select industry...</option>
                    {INDUSTRIES.map((ind) => (
                      <option key={ind.value} value={ind.value}>
                        {ind.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Company Stage */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    <Rocket className="w-4 h-4 inline mr-1" />
                    Company Stage
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    {COMPANY_STAGES.map((stage) => (
                      <button
                        key={stage.value}
                        onClick={() => setFormData({ ...formData, company_stage: stage.value })}
                        className={`px-3 py-2 text-sm rounded-lg border transition-all ${
                          formData.company_stage === stage.value
                            ? 'border-blue-500 bg-blue-50 text-blue-700'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        {stage.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Challenge */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    <Target className="w-4 h-4 inline mr-1" />
                    Business Challenge
                  </label>
                  <textarea
                    value={formData.challenge}
                    onChange={(e) => setFormData({ ...formData, challenge: e.target.value })}
                    placeholder="Describe your primary business challenge or growth goal..."
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                {/* Focus Area */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Focus Area (Optional)
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {FOCUS_AREAS.map((area) => (
                      <button
                        key={area.value}
                        onClick={() => setFormData({
                          ...formData,
                          focus_area: formData.focus_area === area.value ? '' : area.value
                        })}
                        className={`px-3 py-1.5 text-xs rounded-full border transition-all ${
                          formData.focus_area === area.value
                            ? 'border-blue-500 bg-blue-50 text-blue-700'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        {area.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Submit Button */}
                <button
                  onClick={handleSubmit}
                  disabled={!formData.industry || !formData.company_stage || !formData.challenge}
                  className="w-full py-3 px-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-medium rounded-lg hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
                >
                  Generate Strategies
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </motion.div>
          )}

          {step === 'loading' && (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="h-full flex flex-col items-center justify-center p-8"
            >
              <PipelineAnimation />
            </motion.div>
          )}

          {step === 'results' && (
            <motion.div
              key="results"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="h-full flex flex-col"
            >
              {selectedStrategy ? (
                <StrategyDetail
                  strategy={selectedStrategy}
                  onBack={() => setSelectedStrategy(null)}
                />
              ) : (
                <div className="flex-1 p-4 overflow-y-auto custom-scrollbar">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-medium text-gray-900">
                      Your Strategies
                    </h3>
                    <button
                      onClick={handleReset}
                      className="text-sm text-blue-600 hover:underline"
                    >
                      Start over
                    </button>
                  </div>
                  <div className="space-y-3">
                    {strategies.map((strategy, index) => (
                      <StrategyCard
                        key={strategy.id}
                        strategy={strategy}
                        index={index}
                        onClick={() => setSelectedStrategy(strategy)}
                      />
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}

function PipelineAnimation() {
  const stages = [
    { label: 'Processing context', icon: '📝' },
    { label: 'Searching knowledge base', icon: '🔍' },
    { label: 'Analyzing strategies', icon: '🧠' },
    { label: 'Generating recommendations', icon: '✨' },
  ]

  const [currentStage, setCurrentStage] = useState(0)

  useState(() => {
    const interval = setInterval(() => {
      setCurrentStage((prev) => (prev < stages.length - 1 ? prev + 1 : prev))
    }, 500)
    return () => clearInterval(interval)
  })

  return (
    <div className="text-center">
      <Loader2 className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
      <div className="space-y-2">
        {stages.map((stage, index) => (
          <motion.div
            key={stage.label}
            initial={{ opacity: 0.3 }}
            animate={{
              opacity: index <= currentStage ? 1 : 0.3,
            }}
            className={`flex items-center gap-2 justify-center text-sm ${
              index <= currentStage ? 'text-gray-900' : 'text-gray-400'
            }`}
          >
            {index < currentStage ? (
              <CheckCircle2 className="w-4 h-4 text-green-500" />
            ) : index === currentStage ? (
              <Loader2 className="w-4 h-4 animate-spin text-blue-500" />
            ) : (
              <div className="w-4 h-4 rounded-full border border-gray-300" />
            )}
            <span>{stage.icon}</span>
            <span>{stage.label}</span>
          </motion.div>
        ))}
      </div>
    </div>
  )
}

function StrategyDetail({
  strategy,
  onBack
}: {
  strategy: Strategy
  onBack: () => void
}) {
  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b">
        <button
          onClick={onBack}
          className="text-sm text-blue-600 hover:underline mb-2 flex items-center gap-1"
        >
          <ChevronRight className="w-4 h-4 rotate-180" />
          Back to all strategies
        </button>
        <h3 className="font-semibold text-gray-900">{strategy.title}</h3>
        <div className="flex items-center gap-2 mt-1">
          <span className="px-2 py-0.5 text-xs rounded-full bg-blue-100 text-blue-700">
            {strategy.category.replace('_', ' ')}
          </span>
          <span className="text-sm text-gray-500">
            {(strategy.confidence_score * 100).toFixed(0)}% confidence
          </span>
        </div>
      </div>
      <div className="flex-1 p-4 overflow-y-auto custom-scrollbar">
        <p className="text-sm text-gray-600 mb-4">{strategy.description}</p>

        <h4 className="font-medium text-gray-900 mb-2">Action Steps</h4>
        <div className="space-y-3 mb-4">
          {strategy.action_steps.map((step) => (
            <div key={step.step_number} className="flex gap-3">
              <div className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-xs font-medium">
                {step.step_number}
              </div>
              <div>
                <div className="font-medium text-sm text-gray-900">{step.title}</div>
                <div className="text-xs text-gray-500">{step.description}</div>
                {step.timeline && (
                  <div className="text-xs text-blue-600 mt-1">{step.timeline}</div>
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="bg-green-50 rounded-lg p-3 mb-3">
          <h4 className="font-medium text-green-800 text-sm mb-1">Potential Impact</h4>
          <p className="text-sm text-green-700">{strategy.potential_impact}</p>
        </div>

        {strategy.risk_factors.length > 0 && (
          <div className="bg-amber-50 rounded-lg p-3">
            <h4 className="font-medium text-amber-800 text-sm mb-1">Risk Factors</h4>
            <ul className="text-sm text-amber-700 list-disc list-inside">
              {strategy.risk_factors.map((risk, i) => (
                <li key={i}>{risk}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}

function getMockStrategies(): Strategy[] {
  return [
    {
      id: 'str-001',
      title: 'Phased Market Entry Strategy',
      category: 'market_expansion',
      description: 'Implement a systematic phased approach to market expansion, starting with markets that offer the best combination of opportunity and manageable complexity.',
      confidence_score: 0.92,
      action_steps: [
        { step_number: 1, title: 'Market Analysis', description: 'Conduct comprehensive market analysis', timeline: 'Weeks 1-4' },
        { step_number: 2, title: 'Pilot Selection', description: 'Select initial pilot market', timeline: 'Weeks 4-6' },
        { step_number: 3, title: 'Local Setup', description: 'Establish local infrastructure', timeline: 'Weeks 6-12' },
        { step_number: 4, title: 'Soft Launch', description: 'Execute limited pilot launch', timeline: 'Weeks 12-20' },
      ],
      rationale: 'Phased expansion minimizes risk while allowing for market learning.',
      potential_impact: '30-40% revenue increase within 18 months',
      risk_factors: ['Regulatory delays', 'Local competition', 'Currency fluctuation']
    },
    {
      id: 'str-002',
      title: 'Strategic Partnership Accelerator',
      category: 'partnerships',
      description: 'Leverage strategic partnerships with established players to accelerate growth and market presence.',
      confidence_score: 0.88,
      action_steps: [
        { step_number: 1, title: 'Partner Mapping', description: 'Identify potential partners', timeline: 'Weeks 1-3' },
        { step_number: 2, title: 'Value Proposition', description: 'Develop partnership proposals', timeline: 'Weeks 3-5' },
        { step_number: 3, title: 'Negotiation', description: 'Engage and negotiate terms', timeline: 'Weeks 5-12' },
      ],
      rationale: 'Partnerships can compress years of market building into months.',
      potential_impact: '5-10x customer reach within first year',
      risk_factors: ['Partner dependency', 'Integration complexity']
    },
    {
      id: 'str-003',
      title: 'Technology-Led Differentiation',
      category: 'technology',
      description: 'Invest in technology capabilities that create sustainable competitive advantages.',
      confidence_score: 0.85,
      action_steps: [
        { step_number: 1, title: 'Tech Assessment', description: 'Evaluate current capabilities', timeline: 'Weeks 1-4' },
        { step_number: 2, title: 'Innovation Roadmap', description: 'Develop investment priorities', timeline: 'Weeks 4-6' },
        { step_number: 3, title: 'Build & Deploy', description: 'Execute technology development', timeline: 'Weeks 6-24' },
      ],
      rationale: 'Technology leadership creates defensible competitive moats.',
      potential_impact: '20-30% improvement in unit economics',
      risk_factors: ['Technology execution risk', 'Investment requirements']
    }
  ]
}
