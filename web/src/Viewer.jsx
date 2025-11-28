import { useState, useEffect, useMemo } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import pages from './data/pages.json'
import coordinates from './data/coordinates.json'
import translations from './data/translations.json'

function Viewer() {
  const { pageId } = useParams()
  const navigate = useNavigate()
  const [showTranslation, setShowTranslation] = useState(true)
  const [markdownContent, setMarkdownContent] = useState('')
  const [loading, setLoading] = useState(false)

  // Determine current page index and name
  const pageIndex = useMemo(() => {
    if (!pageId) return 0
    const idx = pages.findIndex(p => p.replace('.jpg', '') === pageId)
    return idx >= 0 ? idx : 0
  }, [pageId])

  const currentPage = pages[pageIndex]
  const pageName = currentPage ? currentPage.replace('.jpg', '') : ''

  useEffect(() => {
    if (!pageName) return;

    const fetchTranslation = async () => {
      setLoading(true)
      try {
        const text = translations[pageName]
        
        if (text) {
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

  const hasLineTranslations = Object.keys(lineTranslations).length > 0

  const currentCoordinates = coordinates[currentPage] || {}
  const hasCoordinates = Object.keys(currentCoordinates).length > 0

  const handlePrev = () => {
    const newIndex = Math.max(0, pageIndex - 1)
    const newPage = pages[newIndex].replace('.jpg', '')
    navigate(`/viewer/${newPage}`)
  }

  const handleNext = () => {
    const newIndex = Math.min(pages.length - 1, pageIndex + 1)
    const newPage = pages[newIndex].replace('.jpg', '')
    navigate(`/viewer/${newPage}`)
  }
  
  const handlePageSelect = (e) => {
    const idx = Number(e.target.value)
    const newPage = pages[idx].replace('.jpg', '')
    navigate(`/viewer/${newPage}`)
  }

  if (!currentPage) return <div className="flex-1 flex items-center justify-center bg-slate-950 text-amber-500">Loading pages...</div>

  return (
    <div className="flex-1 flex flex-col overflow-hidden relative bg-slate-950">
      {/* Viewer Controls Toolbar */}
      <div className="bg-slate-800/50 p-2 flex items-center justify-center gap-4 border-b border-slate-700 backdrop-blur-sm">
          <div className="flex items-center gap-4">
            <button 
              onClick={handlePrev}
              disabled={pageIndex === 0}
              className="p-2 rounded hover:bg-slate-700 disabled:opacity-50 transition-colors text-slate-200"
            >
              <ChevronLeft />
            </button>
            
            <select 
              value={pageIndex}
              onChange={handlePageSelect}
              className="bg-slate-700 text-slate-100 border border-slate-600 rounded px-2 py-1 max-w-[150px]"
            >
              {pages.map((page, idx) => (
                <option key={page} value={idx}>
                  {page.replace('.jpg', '')}
                </option>
              ))}
            </select>
            
            <button 
              onClick={handleNext}
              disabled={pageIndex === pages.length - 1}
              className="p-2 rounded hover:bg-slate-700 disabled:opacity-50 transition-colors text-slate-200"
            >
              <ChevronRight />
            </button>
          </div>

          <div className="w-px h-6 bg-slate-600 mx-2"></div>

          <div className="flex items-center gap-2">
            <input 
              type="checkbox" 
              id="showTranslation"
              checked={showTranslation}
              onChange={(e) => setShowTranslation(e.target.checked)}
              className="w-4 h-4 accent-amber-500 cursor-pointer"
            />
            <label htmlFor="showTranslation" className="cursor-pointer select-none text-slate-200 text-sm">
              Show Translation
            </label>
          </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden relative justify-center bg-slate-950">
          <div className="relative shadow-2xl inline-block h-full flex justify-center items-start overflow-auto p-8">
            <div className="relative">
              <img 
                src={currentPage.startsWith('extra') ? `/manuscript/extra/${currentPage}` : `/manuscript/${currentPage}`} 
                alt={currentPage}
                className="max-w-full h-auto shadow-2xl"
                style={{ maxHeight: 'calc(100vh - 180px)' }}
              />
              
              {/* Overlay Mode: Coordinates exist */}
              {showTranslation && hasCoordinates && hasLineTranslations && (
                <div className="absolute inset-0 pointer-events-none">
                  {Object.entries(currentCoordinates).map(([id, coords]) => {
                    const text = lineTranslations[id]
                    if (!text) return null
                    return (
                      <div 
                        key={id}
                        className="absolute text-amber-100 p-2 rounded text-sm hover:bg-slate-900/95 transition-all border border-amber-500/30 backdrop-blur-sm shadow-lg pointer-events-auto cursor-help"
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

              {/* Overlay Mode: No Coordinates (Fallback Layer) */}
              {showTranslation && (!hasCoordinates || !hasLineTranslations) && (
                <div className="absolute inset-0 bg-slate-900/70 p-8 overflow-auto backdrop-blur-[2px] transition-all">
                   <div className="max-w-2xl mx-auto bg-slate-900/90 p-6 rounded-lg shadow-2xl border border-amber-500/30 text-slate-100">
                     <h2 className="text-xl font-bold text-amber-500 mb-4 border-b border-slate-700 pb-2 sticky top-0 bg-slate-900/95 pt-2">
                       Translated Page: {pageName}
                     </h2>
                     {loading ? (
                       <div className="flex justify-center p-4 text-slate-400">Loading translation...</div>
                     ) : (
                       <div className="prose prose-invert prose-amber max-w-none">
                         <ReactMarkdown remarkPlugins={[remarkGfm]}>
                           {markdownContent}
                         </ReactMarkdown>
                       </div>
                     )}
                   </div>
                </div>
              )}
            </div>
          </div>
      </div>
    </div>
  )
}

export default Viewer
