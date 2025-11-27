import { Routes, Route, Navigate, Link, useLocation } from 'react-router-dom'
import { BookOpen, Activity, Library } from 'lucide-react'
import Stats from './Stats'
import Dictionary from './Dictionary'
import Viewer from './Viewer'

function App() {
  const location = useLocation()
  
  const isViewer = location.pathname.startsWith('/viewer') || location.pathname === '/'
  const isStats = location.pathname === '/stats'
  const isDictionary = location.pathname === '/dictionary'

  return (
    <div className="h-screen flex flex-col overflow-hidden bg-slate-950">
      {/* Header */}
      <header className="bg-slate-800 p-4 flex items-center justify-between shadow-lg z-10 border-b border-slate-700 flex-shrink-0">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <BookOpen className="w-6 h-6 text-amber-500" />
            <h1 className="text-xl font-bold text-amber-500">Voynich Viewer</h1>
          </div>

          <div className="flex bg-slate-700 rounded-lg p-1 border border-slate-600">
            <Link
              to="/viewer/f1r"
              className={`px-3 py-1 rounded-md text-sm transition-colors flex items-center gap-2 ${
                isViewer ? 'bg-slate-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <BookOpen size={16} />
              Viewer
            </Link>
            <Link
              to="/stats"
              className={`px-3 py-1 rounded-md text-sm transition-colors flex items-center gap-2 ${
                isStats ? 'bg-slate-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Activity size={16} />
              Stats
            </Link>
            <Link
              to="/dictionary"
              className={`px-3 py-1 rounded-md text-sm transition-colors flex items-center gap-2 ${
                isDictionary ? 'bg-slate-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Library size={16} />
              Dictionary
            </Link>
          </div>
        </div>
      </header>

      {/* Main Layout Area */}
      <Routes>
        <Route path="/" element={<Navigate to="/viewer/f1r" replace />} />
        <Route path="/viewer" element={<Navigate to="/viewer/f1r" replace />} />
        <Route path="/viewer/:pageId" element={<Viewer />} />
        <Route path="/stats" element={<Stats />} />
        <Route path="/dictionary" element={<Dictionary />} />
      </Routes>
    </div>
  )
}

export default App
