import { motion } from 'framer-motion'
import { ChevronRight, TrendingUp } from 'lucide-react'

interface Strategy {
  id: string
  title: string
  category: string
  description: string
  confidence_score: number
}

interface StrategyCardProps {
  strategy: Strategy
  index: number
  onClick: () => void
}

const CATEGORY_COLORS: Record<string, string> = {
  market_expansion: 'bg-blue-100 text-blue-700',
  partnerships: 'bg-purple-100 text-purple-700',
  technology: 'bg-green-100 text-green-700',
  operational_efficiency: 'bg-amber-100 text-amber-700',
  product_innovation: 'bg-pink-100 text-pink-700',
  revenue_growth: 'bg-emerald-100 text-emerald-700',
}

export function StrategyCard({ strategy, index, onClick }: StrategyCardProps) {
  const categoryColor = CATEGORY_COLORS[strategy.category] || 'bg-gray-100 text-gray-700'

  return (
    <motion.button
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      onClick={onClick}
      className="w-full text-left p-4 bg-white border border-gray-200 rounded-xl hover:border-blue-300 hover:shadow-md transition-all group"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className={`px-2 py-0.5 text-xs rounded-full ${categoryColor}`}>
              {strategy.category.replace('_', ' ')}
            </span>
            <span className="flex items-center gap-1 text-xs text-gray-500">
              <TrendingUp className="w-3 h-3" />
              {(strategy.confidence_score * 100).toFixed(0)}%
            </span>
          </div>
          <h4 className="font-medium text-gray-900 mb-1 group-hover:text-blue-600 transition-colors">
            {strategy.title}
          </h4>
          <p className="text-sm text-gray-500 line-clamp-2">
            {strategy.description}
          </p>
        </div>
        <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-blue-500 transition-colors flex-shrink-0 mt-1" />
      </div>

      {/* Confidence bar */}
      <div className="mt-3">
        <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${strategy.confidence_score * 100}%` }}
            transition={{ delay: index * 0.1 + 0.3, duration: 0.5 }}
            className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full"
          />
        </div>
      </div>
    </motion.button>
  )
}
