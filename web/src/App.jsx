import { useState, useEffect, useMemo } from 'react'
import { ChevronLeft, ChevronRight, BookOpen } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import pages from './data/pages.json'
import coordinates from './data/coordinates.json'

function App() {
  const [currentPageIndex, setCurrentPageIndex] = useState(0)
  const [showTranslation, setShowTranslation] = useState(true)
  const [markdownContent, setMarkdownContent] = useState('')
  const [loading, setLoading] = useState(false)
  
  const currentPage = pages[currentPageIndex]
  const pageName = currentPage.replace('.jpg', '')

  useEffect(() => {
    const fetchTranslation = async () => {
      setLoading(true)
      try {
        const response = await fetch(`/translated/${pageName}.md`)
        const contentType = response.headers.get('content-type')
        
        if (response.ok && contentType && !contentType.includes('text/html')) {
          const text = await response.text()
          setMarkdownContent(text)
        } else {
          setMarkdownContent('*No translation available for this page.*')
        }
      } catch (error) {
        console.error('Error loading translation:', error)
        setMarkdownContent('*Error loading translation.*')
      } finally {
        setLoading(false)
      }
    }

    fetchTranslation()
  }, [pageName])

  // Parse markdown to extract line translations
  const lineTranslations = useMemo(() => {
    const lines = {}
    const regex = /\*\*([a-z0-9]+\.\d+)\*\*:(.*?)(?=\*\*|$)/gs
    let match
    while ((match = regex.exec(markdownContent)) !== null) {
      const id = match[1]
      const text = match[2].trim().split('\n')[0] // Take first line of translation
      lines[id] = text
    }
    return lines
  }, [markdownContent])

  const currentCoordinates = coordinates[currentPage] || {}

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
          
          {/* Overlay Layer */}
          {showTranslation && Object.keys(currentCoordinates).length > 0 && (
            <div className="absolute inset-0 pointer-events-none">
              {Object.entries(currentCoordinates).map(([id, coords]) => {
                const text = lineTranslations[id]
                if (!text) return null
                return (
                  <div 
                    key={id}
                    className="absolute bg-slate-900/80 text-amber-100 p-2 rounded text-sm hover:bg-slate-900/95 transition-all border border-amber-500/30 backdrop-blur-sm shadow-lg pointer-events-auto cursor-help"
                    style={{ 
                      top: coords.top, 
                      left: coords.left,
                      maxWidth: coords.width || '200px'
                    }}
                  >
                    <span className="font-bold text-amber-500 mr-2">{id}:</span>
                    <span className="font-serif">{text}</span>
                  </div>
                )
              })}
            </div>
          )}

          {/* Fallback Side Panel (only if no coordinates for this page) */}
          {showTranslation && Object.keys(currentCoordinates).length === 0 && (
            <div className="absolute top-0 right-0 w-1/3 h-full bg-slate-900/90 text-slate-100 p-6 overflow-auto border-l border-amber-500/30 backdrop-blur-sm shadow-2xl transition-all">
               {loading ? (
                 <div className="flex justify-center p-4">Loading...</div>
               ) : (
                 <div className="prose prose-invert prose-amber max-w-none">
                   <ReactMarkdown remarkPlugins={[remarkGfm]}>
                     {markdownContent}
                   </ReactMarkdown>
                 </div>
               )}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

export default App
