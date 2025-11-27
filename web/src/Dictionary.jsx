import React, { useState, useMemo } from 'react';
import { Search, Book, Filter, ExternalLink } from 'lucide-react';
import dictionaryData from './data/dictionary.json';

const Dictionary = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDomain, setSelectedDomain] = useState('All');
  const [minConfidence, setMinConfidence] = useState('All');

  // Extract unique domains
  const domains = useMemo(() => {
    const allDomains = new Set();
    Object.values(dictionaryData.entries).forEach(entry => {
      if (entry.domain) allDomains.add(entry.domain);
    });
    return ['All', ...Array.from(allDomains).sort()];
  }, []);

  const confidenceLevels = ['All', 'VERIFIED', 'ULTRA_HIGH', 'VERY_HIGH', 'HIGH', 'MEDIUM', 'LOW'];

  const filteredEntries = useMemo(() => {
    return Object.values(dictionaryData.entries).filter(entry => {
      // Search filter
      const searchLower = searchTerm.toLowerCase();
      const matchesSearch = 
        entry.voynich.toLowerCase().includes(searchLower) ||
        entry.meaning.toLowerCase().includes(searchLower) ||
        (entry.notes && entry.notes.toLowerCase().includes(searchLower));

      // Domain filter
      const matchesDomain = selectedDomain === 'All' || entry.domain === selectedDomain;

      // Confidence filter
      const matchesConfidence = minConfidence === 'All' || entry.confidence_level === minConfidence;

      return matchesSearch && matchesDomain && matchesConfidence;
    });
  }, [searchTerm, selectedDomain, minConfidence]);

  const getConfidenceColor = (level) => {
    switch (level) {
      case 'VERIFIED': return 'bg-green-500/20 text-green-400 border-green-500/50';
      case 'ULTRA_HIGH': return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/50';
      case 'VERY_HIGH': return 'bg-teal-500/20 text-teal-400 border-teal-500/50';
      case 'HIGH': return 'bg-blue-500/20 text-blue-400 border-blue-500/50';
      case 'MEDIUM': return 'bg-amber-500/20 text-amber-400 border-amber-500/50';
      case 'LOW': return 'bg-red-500/20 text-red-400 border-red-500/50';
      default: return 'bg-slate-700 text-slate-400 border-slate-600';
    }
  };

  return (
    <div className="flex-1 flex flex-col overflow-hidden bg-slate-950 text-slate-100">
      {/* Header / Search Area */}
      <div className="bg-slate-900 border-b border-slate-800 p-6 shadow-lg z-10">
        <div className="max-w-5xl mx-auto w-full">
          <div className="flex items-center gap-4 mb-6">
            <Book className="w-8 h-8 text-amber-500" />
            <div>
              <h1 className="text-2xl font-bold text-amber-500">Voynich Dictionary</h1>
              <div className="text-slate-400 text-sm">
                {filteredEntries.length} entries found (Total: {dictionaryData.total_entries})
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Search Input */}
            <div className="md:col-span-2 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search Voynich word or meaning..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg py-3 pl-10 pr-4 text-slate-100 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500 transition-all"
              />
            </div>

            {/* Domain Filter */}
            <div className="relative">
              <select
                value={selectedDomain}
                onChange={(e) => setSelectedDomain(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg py-3 px-4 text-slate-100 focus:outline-none focus:border-amber-500 appearance-none cursor-pointer"
              >
                {domains.map(domain => (
                  <option key={domain} value={domain}>
                    Domain: {domain}
                  </option>
                ))}
              </select>
              <Filter className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4 pointer-events-none" />
            </div>

            {/* Confidence Filter */}
            <div className="relative">
              <select
                value={minConfidence}
                onChange={(e) => setMinConfidence(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg py-3 px-4 text-slate-100 focus:outline-none focus:border-amber-500 appearance-none cursor-pointer"
              >
                {confidenceLevels.map(level => (
                  <option key={level} value={level}>
                    Confidence: {level}
                  </option>
                ))}
              </select>
              <Filter className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4 pointer-events-none" />
            </div>
          </div>
        </div>
      </div>

      {/* Results List */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-5xl mx-auto w-full space-y-4">
          {filteredEntries.length > 0 ? (
            filteredEntries.map((entry) => (
              <div 
                key={entry.voynich} 
                className="bg-slate-900 border border-slate-800 rounded-xl p-6 hover:border-slate-700 transition-all shadow-sm hover:shadow-md group"
              >
                <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                  <div>
                    <div className="flex items-baseline gap-3 mb-2">
                      <h3 className="text-2xl font-bold text-amber-500 font-mono">{entry.voynich}</h3>
                      <span className={`px-2 py-0.5 rounded text-xs font-bold border ${getConfidenceColor(entry.confidence_level)}`}>
                        {entry.confidence_level}
                      </span>
                    </div>
                    
                    <div className="text-lg text-slate-200 font-medium mb-3">
                      {entry.meaning}
                    </div>

                    <div className="flex flex-wrap gap-x-6 gap-y-2 text-sm text-slate-400">
                      <div className="flex items-center gap-2">
                        <span className="uppercase text-xs font-bold tracking-wider text-slate-500">Domain</span>
                        <span className="text-slate-300 capitalize">{entry.domain}</span>
                      </div>
                      {entry.language && (
                        <div className="flex items-center gap-2">
                          <span className="uppercase text-xs font-bold tracking-wider text-slate-500">Language</span>
                          <span className="text-slate-300 capitalize">{entry.language}</span>
                        </div>
                      )}
                      <div className="flex items-center gap-2">
                         <span className="uppercase text-xs font-bold tracking-wider text-slate-500">Source</span>
                         <span className="text-slate-300">{entry.source}</span>
                      </div>
                    </div>
                  </div>

                  {/* Evidence / Notes Side */}
                  <div className="md:w-1/3 md:border-l md:border-slate-800 md:pl-6 text-sm">
                    {entry.evidence && (
                       <div className="mb-3">
                         <span className="uppercase text-xs font-bold tracking-wider text-slate-500 block mb-1">Evidence</span>
                         <p className="text-slate-300 leading-relaxed">{entry.evidence}</p>
                       </div>
                    )}
                    {entry.notes && (
                       <div>
                         <span className="uppercase text-xs font-bold tracking-wider text-slate-500 block mb-1">Notes</span>
                         <p className="text-slate-400 italic">{entry.notes}</p>
                       </div>
                    )}
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-20 text-slate-500">
              <Search className="w-12 h-12 mx-auto mb-4 opacity-20" />
              <p className="text-lg">No dictionary entries found matching your filters.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dictionary;
