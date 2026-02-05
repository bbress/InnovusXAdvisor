import { useState } from 'react'
import { StrategyLab } from './components/StrategyLab'
import { UnderTheHood } from './components/UnderTheHood'

function App() {
  const [showUnderTheHood, setShowUnderTheHood] = useState(false)

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <header className="text-center mb-8">
          <div className="inline-flex items-center gap-2 mb-2">
            <div className="w-8 h-8 rounded-lg gradient-primary flex items-center justify-center">
              <span className="text-white font-bold text-sm">IX</span>
            </div>
            <h1 className="text-2xl font-bold text-gray-900">
              AI Strategy Lab
            </h1>
          </div>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Experience enterprise AI in action. Get personalized business strategies
            powered by our AI platform, then explore the technology behind it.
          </p>
        </header>

        {/* Main Content */}
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Strategy Lab */}
          <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
            <StrategyLab />
          </div>

          {/* Under the Hood */}
          <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
            <UnderTheHood />
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-8 text-center text-sm text-gray-500">
          <p>
            Powered by InnovusX AI Platform •
            <a href="https://innovus-x.com" className="text-blue-600 hover:underline ml-1">
              Learn more
            </a>
          </p>
        </footer>
      </div>
    </div>
  )
}

export default App
