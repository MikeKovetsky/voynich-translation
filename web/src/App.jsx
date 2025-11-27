import { useState } from 'react'
import { ChevronLeft, ChevronRight, BookOpen } from 'lucide-react'
import pages from './data/pages.json'
import translations from './data/translations.json'

function App() {
  const [currentPageIndex, setCurrentPageIndex] = useState(0)
  const [showTranslation, setShowTranslation] = useState(true)
  
  const currentPage = pages[currentPageIndex]
  const currentTranslation = translations[currentPage] || []

  const handlePrev = () => {
    setCurrentPageIndex(prev => Math.max(0, prev - 1))
  }

  const handleNext = () => {
    setCurrentPageIndex(prev => Math.min(pages.length - 1, prev + 1))
  }

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <header className="bg-slate-800 p-4 flex items-center justify-between shadow-lg z-10 border-b border-slate-700">
        <div className="flex items-center gap-2">
          <BookOpen className="w-6 h-6 text-amber-500" />
          <h1 className="text-xl font-bold text-amber-500">Voynich Viewer</h1>
        </div>
        
        <div className="flex items-center gap-4">
          <button 
            onClick={handlePrev}
            disabled={currentPageIndex === 0}
            className="p-2 rounded hover:bg-slate-700 disabled:opacity-50 transition-colors"
          >
            <ChevronLeft />
          </button>
          
          <select 
            value={currentPageIndex}
            onChange={(e) => setCurrentPageIndex(Number(e.target.value))}
            className="bg-slate-700 text-slate-100 border border-slate-600 rounded px-2 py-1"
          >
            {pages.map((page, idx) => (
              <option key={page} value={idx}>
                {page}
              </option>
            ))}
          </select>
          
          <button 
            onClick={handleNext}
            disabled={currentPageIndex === pages.length - 1}
            className="p-2 rounded hover:bg-slate-700 disabled:opacity-50 transition-colors"
          >
            <ChevronRight />
          </button>
        </div>

        <div className="flex items-center gap-2">
          <input 
            type="checkbox" 
            id="showTranslation"
            checked={showTranslation}
            onChange={(e) => setShowTranslation(e.target.checked)}
            className="w-4 h-4 accent-amber-500 cursor-pointer"
          />
          <label htmlFor="showTranslation" className="cursor-pointer select-none">
            Show Translation
          </label>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 overflow-auto bg-slate-950 flex justify-center relative p-8">
        <div className="relative shadow-2xl inline-block">
          <img 
            src={`/manuscript/${currentPage}`} 
            alt={currentPage}
            className="max-w-full h-auto shadow-2xl"
            style={{ maxHeight: 'calc(100vh - 120px)' }}
          />
          
          {showTranslation && currentTranslation.map((item, idx) => (
            <div 
              key={idx}
              className="absolute bg-slate-900/80 text-amber-100 p-3 rounded text-sm hover:bg-slate-900/95 transition-all cursor-help border border-amber-500/30 backdrop-blur-sm shadow-lg"
              style={{ 
                top: item.top, 
                left: item.left,
                maxWidth: '250px'
              }}
            >
              <div className="font-serif">{item.text}</div>
            </div>
          ))}
        </div>
      </main>
    </div>
  )
}

export default App
