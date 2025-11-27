import React, { useState, useMemo } from 'react';
import { BarChart, Activity, Book, Star, User } from 'lucide-react';
import translations from './data/translations.json';
import dictionaryData from './data/dictionary.json';
import manuscriptData from './data/manuscript_data.json';

const Stats = () => {
  const [selectedSection, setSelectedSection] = useState('All');

  // --- Calculation Logic (Ported from Python) ---
  const statsData = useMemo(() => {
    const getSection = (page) => {
      // Handle both 'f10r' and '10r' formats
      const match = page.match(/^f?(\d+)([rv]?)/i);
      if (!match) return "Unknown";
      
      const num = parseInt(match[1], 10);
      if (isNaN(num)) return "Unknown";

      if (num >= 1 && num <= 66) return "Botanical";
      if (num >= 67 && num <= 73) return "Astronomical";
      if (num >= 75 && num <= 84) return "Biological";
      if (num >= 85 && num <= 86) return "Cosmological";
      if (num >= 87 && num <= 102) return "Pharmaceutical";
      if (num >= 103 && num <= 116) return "Recipes";
      return "Unknown";
    };

    const calculateConfidence = (text) => {
      if (!text || !text.trim()) return 0;
      
      // Clean markdown
      const cleanText = text.replace(/\*\*.*?\*\*/g, '').replace(/#.*/g, '');
      const words = cleanText.split(/\s+/).filter(w => w.length > 0);
      
      if (words.length === 0) return 0;
      if (text.length < 50) return 0; // Too short

      const questionMarks = (text.match(/\?/g) || []).length;
      const unknownTags = (text.match(/UNKNOWN|verb \(unknown\)/g) || []).length;
      
      let confidence = 100.0;
      const penalty = (questionMarks + unknownTags) * 2;
      confidence -= (penalty / Math.max(words.length, 1)) * 100;
      
      return Math.max(0, Math.min(100, parseFloat(confidence.toFixed(1))));
    };

    // Initialize sections
    const sections = {
      "Botanical": { total_pages: 0, translated_pages: 0, confidence_sum: 0, dictionary: null },
      "Astronomical": { total_pages: 0, translated_pages: 0, confidence_sum: 0, dictionary: null },
      "Biological": { total_pages: 0, translated_pages: 0, confidence_sum: 0, dictionary: null },
      "Cosmological": { total_pages: 0, translated_pages: 0, confidence_sum: 0, dictionary: null },
      "Pharmaceutical": { total_pages: 0, translated_pages: 0, confidence_sum: 0, dictionary: null },
      "Recipes": { total_pages: 0, translated_pages: 0, confidence_sum: 0, dictionary: null },
      "Unknown": { total_pages: 0, translated_pages: 0, confidence_sum: 0, dictionary: null }
    };

    let totalPages = 0;
    let translatedPages = 0;
    let totalConfidenceSum = 0;

    // Process Pages
    Object.entries(translations).forEach(([page, text]) => {
      const sec = getSection(page);
      if (!sections[sec]) return;

      sections[sec].total_pages++;
      totalPages++;

      if (text.length > 50 && !text.slice(0, 10).includes('?')) {
        const conf = calculateConfidence(text);
        sections[sec].translated_pages++;
        sections[sec].confidence_sum += conf;
        translatedPages++;
        totalConfidenceSum += conf;
      }
    });

    // Finalize Section Page Stats
    Object.keys(sections).forEach(key => {
      const s = sections[key];
      s.avg_confidence = s.translated_pages > 0 ? parseFloat((s.confidence_sum / s.translated_pages).toFixed(1)) : 0;
      s.coverage_percent = s.total_pages > 0 ? parseFloat(((s.translated_pages / s.total_pages) * 100).toFixed(1)) : 0;
    });

    // --- DICTIONARY STATS CALCULATION ---

    // 1. Calculate Section Words first
    const sectionWords = {};
    Object.keys(sections).forEach(k => sectionWords[k] = new Set());
    // Also track all unique words in manuscript for Global stats
    const allManuscriptWords = new Set();

    // Map words to sections using manuscriptData
    Object.entries(manuscriptData).forEach(([pageId, data]) => {
       const sec = getSection(pageId);
       
       if (data.text) {
           const cleanText = data.text
               .replace(/`/g, '') 
               .replace(/<.*?>/g, '') 
               .replace(/\$/g, '') 
               .replace(/[.,]/g, ' '); 
           
           const words = cleanText.split(/\s+/).filter(w => w && w.length > 0);
           words.forEach(w => {
             if (sectionWords[sec]) sectionWords[sec].add(w);
             allManuscriptWords.add(w);
           });
       }
    });

    // 2. Global Dictionary Stats (Based on Manuscript Words)
    // This ensures consistency with Section stats (Metric B: Text Readability)
    const globalDictStats = {
      total_entries: allManuscriptWords.size,
      domains: {},
      confidence_levels: {},
      translation_status: { 0: 0, 1: 0, 2: 0 }
    };

    allManuscriptWords.forEach(word => {
        const entry = dictionaryData.entries[word];
        if (entry) {
            const status = entry.translation_status !== undefined ? entry.translation_status : 0;
            globalDictStats.translation_status[status]++;
            
            const conf = entry.confidence_level || 'UNKNOWN';
            globalDictStats.confidence_levels[conf] = (globalDictStats.confidence_levels[conf] || 0) + 1;

            const domain = entry.domain || 'unknown';
            globalDictStats.domains[domain] = (globalDictStats.domains[domain] || 0) + 1;
        } else {
            // Word in text but not in dictionary -> Untranslated
            globalDictStats.translation_status[0]++;
        }
    });

    const globalWeightedSum = (globalDictStats.translation_status[2] * 1.0) + (globalDictStats.translation_status[1] * 0.5);
    globalDictStats.completeness_score = globalDictStats.total_entries > 0 
      ? parseFloat(((globalWeightedSum / globalDictStats.total_entries) * 100).toFixed(1))
      : 0;


    // 3. Section Dictionary Stats (Based on Word Occurrence)
    // Calculate stats for each section
    Object.keys(sections).forEach(secKey => {
        const words = sectionWords[secKey];
        const stats = {
            total_entries: words.size,
            translation_status: { 0: 0, 1: 0, 2: 0 },
            confidence_levels: {},
            domains: {}
        };

        words.forEach(word => {
            const entry = dictionaryData.entries[word];
            if (entry) {
                const status = entry.translation_status !== undefined ? entry.translation_status : 0;
                stats.translation_status[status]++;
                
                const conf = entry.confidence_level || 'UNKNOWN';
                stats.confidence_levels[conf] = (stats.confidence_levels[conf] || 0) + 1;

                const domain = entry.domain || 'unknown';
                stats.domains[domain] = (stats.domains[domain] || 0) + 1;
            } else {
                // Word appearing in text but not in dictionary -> Untranslated
                stats.translation_status[0]++;
            }
        });

        const wSum = (stats.translation_status[2] * 1.0) + (stats.translation_status[1] * 0.5);
        stats.completeness_score = stats.total_entries > 0 
            ? parseFloat(((wSum / stats.total_entries) * 100).toFixed(1))
            : 0;
            
        sections[secKey].dictionary = stats;
    });

    // Global Stats Object
    const globalStats = {
      total_pages: totalPages,
      translated_pages: translatedPages,
      avg_confidence: translatedPages > 0 ? parseFloat((totalConfidenceSum / translatedPages).toFixed(1)) : 0,
      coverage_percent: totalPages > 0 ? parseFloat(((translatedPages / totalPages) * 100).toFixed(1)) : 0,
      dictionary: globalDictStats
    };

    return {
      global: globalStats,
      sections: sections
    };
  }, []);

  // Available sections
  const sectionKeys = ['All', ...Object.keys(statsData.sections).filter(k => k !== 'Unknown')];

  const currentStats = useMemo(() => {
    if (selectedSection === 'All') {
      return statsData.global;
    }
    return statsData.sections[selectedSection];
  }, [selectedSection, statsData]);

  const getConfidenceColor = (score) => {
    if (score >= 80) return 'text-green-500';
    if (score >= 60) return 'text-amber-500';
    return 'text-red-500';
  };

  return (
    <div className="flex-1 flex overflow-hidden bg-slate-950 text-slate-100 p-8">
      <div className="max-w-5xl mx-auto w-full overflow-y-auto">
        <div className="flex items-center gap-4 mb-8">
          <Activity className="w-8 h-8 text-amber-500" />
          <h1 className="text-3xl font-bold text-amber-500">Translation Statistics</h1>
        </div>

        {/* Filters */}
        <div className="mb-8 flex flex-wrap gap-2">
          {sectionKeys.map(sec => (
            <button
              key={sec}
              onClick={() => setSelectedSection(sec)}
              className={`px-4 py-2 rounded-full border transition-all ${
                selectedSection === sec
                  ? 'bg-amber-500 text-slate-900 border-amber-500 font-bold'
                  : 'bg-slate-900 text-slate-300 border-slate-700 hover:border-amber-500/50'
              }`}
            >
              {sec}
            </button>
          ))}
        </div>

        {/* Main Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* North Star Card */}
          <div className="bg-slate-900 p-6 rounded-xl border border-amber-500/30 shadow-xl relative overflow-hidden">
            <div className="absolute top-0 right-0 p-4 opacity-10">
              <Star className="w-24 h-24 text-amber-500" />
            </div>
            <div className="flex items-center justify-between mb-4 relative z-10">
              <h3 className="text-lg font-semibold text-amber-500">North Star Metric</h3>
              <Star className="w-5 h-5 text-amber-500" />
            </div>
            <div className="text-4xl font-bold text-white relative z-10">
              {currentStats.dictionary?.completeness_score || 0}%
            </div>
            <div className="text-sm text-slate-400 mt-2 relative z-10">
              Dictionary Translation Completeness
            </div>
            {/* Progress Bar */}
            <div className="w-full bg-slate-800 h-2 rounded-full mt-4 overflow-hidden relative z-10">
              <div 
                className="bg-gradient-to-r from-amber-600 to-yellow-400 h-full transition-all duration-500" 
                style={{ width: `${currentStats.dictionary?.completeness_score || 0}%` }}
              />
            </div>
          </div>

          {/* Coverage Card */}
          <div className="bg-slate-900 p-6 rounded-xl border border-slate-800 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-slate-400">Coverage</h3>
              <Book className="w-5 h-5 text-blue-400" />
            </div>
            <div className="text-4xl font-bold text-blue-400">
              {currentStats.coverage_percent}%
            </div>
            <div className="text-sm text-slate-500 mt-2">
              {currentStats.translated_pages} / {currentStats.total_pages} Pages
            </div>
            {/* Progress Bar */}
            <div className="w-full bg-slate-800 h-2 rounded-full mt-4 overflow-hidden">
              <div 
                className="bg-blue-500 h-full transition-all duration-500" 
                style={{ width: `${currentStats.coverage_percent}%` }}
              />
            </div>
          </div>

          {/* Confidence Card */}
          <div className="bg-slate-900 p-6 rounded-xl border border-slate-800 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-slate-400">Avg. Confidence</h3>
              <Star className="w-5 h-5 text-amber-400" />
            </div>
            <div className={`text-4xl font-bold ${getConfidenceColor(currentStats.avg_confidence)}`}>
              {currentStats.avg_confidence}%
            </div>
            <div className="text-sm text-slate-500 mt-2">
              Based on lexical completeness
            </div>
             {/* Progress Bar */}
             <div className="w-full bg-slate-800 h-2 rounded-full mt-4 overflow-hidden">
              <div 
                className={`h-full transition-all duration-500 ${
                    currentStats.avg_confidence >= 80 ? 'bg-green-500' : 
                    currentStats.avg_confidence >= 60 ? 'bg-amber-500' : 'bg-red-500'
                }`} 
                style={{ width: `${currentStats.avg_confidence}%` }}
              />
            </div>
          </div>

           {/* Section Info Card */}
           <div className="bg-slate-900 p-6 rounded-xl border border-slate-800 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-slate-400">Domain</h3>
              <User className="w-5 h-5 text-purple-400" />
            </div>
            <div className="text-2xl font-bold text-purple-400">
              {selectedSection === 'All' ? 'Full Manuscript' : selectedSection}
            </div>
            <div className="text-sm text-slate-500 mt-2">
              {selectedSection === 'All' ? 'Aggregated stats across all sections' : 'Specific section statistics'}
            </div>
          </div>
        </div>

        {/* Detailed Breakdown for ALL view */}
        <div className="space-y-8">
          {selectedSection === 'All' && (
            <div className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden">
               <div className="p-4 border-b border-slate-800 bg-slate-800/50">
                  <h3 className="font-bold text-slate-200">Page Translation Breakdown</h3>
               </div>
               <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm">
                      <thead>
                          <tr className="bg-slate-800/30 text-slate-400">
                              <th className="p-4 font-medium">Section</th>
                              <th className="p-4 font-medium">Pages</th>
                              <th className="p-4 font-medium">Coverage</th>
                              <th className="p-4 font-medium">Confidence</th>
                          </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800">
                          {Object.entries(statsData.sections).filter(([k]) => k !== 'Unknown').map(([name, data]) => (
                              <tr key={name} className="hover:bg-slate-800/50 transition-colors">
                                  <td className="p-4 font-medium text-slate-200">{name}</td>
                                  <td className="p-4 text-slate-400">{data.total_pages}</td>
                                  <td className="p-4">
                                      <div className="flex items-center gap-2">
                                          <span className="text-blue-400 font-mono">{data.coverage_percent}%</span>
                                          <div className="w-16 bg-slate-800 h-1.5 rounded-full overflow-hidden">
                                              <div className="bg-blue-500 h-full" style={{ width: `${data.coverage_percent}%` }} />
                                          </div>
                                      </div>
                                  </td>
                                  <td className="p-4">
                                      <div className="flex items-center gap-2">
                                          <span className={`font-mono ${getConfidenceColor(data.avg_confidence)}`}>
                                              {data.avg_confidence}%
                                          </span>
                                          <div className="w-16 bg-slate-800 h-1.5 rounded-full overflow-hidden">
                                              <div className={`h-full ${
                                                  data.avg_confidence >= 80 ? 'bg-green-500' : 
                                                  data.avg_confidence >= 60 ? 'bg-amber-500' : 'bg-red-500'
                                              }`} style={{ width: `${data.avg_confidence}%` }} />
                                          </div>
                                      </div>
                                  </td>
                              </tr>
                          ))}
                      </tbody>
                  </table>
               </div>
            </div>
          )}

          {/* Dictionary Stats - Visible for all sections */}
          {currentStats.dictionary && (
            <div className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden p-6">
               <h3 className="text-xl font-bold text-amber-500 mb-6 flex items-center gap-2">
                  <Book className="w-6 h-6" />
                  Dictionary Statistics ({selectedSection})
               </h3>
               
               <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {/* Left: Overview */}
                  <div>
                      <div className="mb-6">
                          <div className="text-sm text-slate-400 mb-1">Total Dictionary Entries</div>
                          <div className="text-4xl font-bold text-slate-100">{currentStats.dictionary.total_entries}</div>
                      </div>

                      <h4 className="font-semibold text-slate-300 mb-4">Confidence Levels</h4>
                      <div className="space-y-3 mb-8">
                          {Object.entries(currentStats.dictionary.confidence_levels)
                            .sort(([,a], [,b]) => b - a)
                            .map(([level, count]) => (
                              <div key={level}>
                                  <div className="flex justify-between text-sm mb-1">
                                      <span className="text-slate-400">{level}</span>
                                      <span className="text-slate-200">{count}</span>
                                  </div>
                                  <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                                      <div 
                                          className={`h-full ${
                                              level === 'VERIFIED' ? 'bg-green-400' :
                                              level.includes('HIGH') ? 'bg-green-500' :
                                              level === 'MEDIUM' ? 'bg-amber-500' :
                                              'bg-slate-600'
                                          }`}
                                          style={{ width: `${(count / currentStats.dictionary.total_entries) * 100}%` }}
                                      />
                                  </div>
                              </div>
                          ))}
                      </div>

                      <h4 className="font-semibold text-slate-300 mb-4">Translation Status</h4>
                      <div className="space-y-3">
                          {[2, 1, 0].map((status) => {
                              const count = currentStats.dictionary.translation_status[status] || 0;
                              const labels = { 2: 'Translated', 1: 'Partial', 0: 'Untranslated' };
                              const colors = { 2: 'bg-green-500', 1: 'bg-amber-500', 0: 'bg-slate-600' };
                              return (
                                  <div key={status}>
                                      <div className="flex justify-between text-sm mb-1">
                                          <span className="text-slate-400">{labels[status]}</span>
                                          <span className="text-slate-200">{count}</span>
                                      </div>
                                      <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                                          <div 
                                              className={`h-full ${colors[status]}`}
                                              style={{ width: `${(count / currentStats.dictionary.total_entries) * 100}%` }}
                                          />
                                      </div>
                                  </div>
                              );
                          })}
                      </div>
                  </div>

                  {/* Right: Domains */}
                  <div>
                      <h4 className="font-semibold text-slate-300 mb-4">Word Domains</h4>
                      <div className="grid grid-cols-2 gap-4">
                          {Object.entries(currentStats.dictionary.domains)
                            .sort(([,a], [,b]) => b - a)
                            .slice(0, 10)
                            .map(([domain, count]) => (
                              <div key={domain} className="bg-slate-800/50 p-3 rounded border border-slate-700">
                                  <div className="text-xs text-amber-500 uppercase font-bold mb-1 truncate">{domain}</div>
                                  <div className="text-2xl font-bold text-slate-200">{count}</div>
                              </div>
                          ))}
                      </div>
                  </div>
               </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Stats;
