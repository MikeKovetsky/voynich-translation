import React, { useState, useMemo } from 'react';
import { BarChart, Activity, Book, Star, User } from 'lucide-react';
import statsData from './data/stats.json';

const Stats = () => {
  const [selectedSection, setSelectedSection] = useState('All');

  // Available sections
  const sections = ['All', ...Object.keys(statsData.sections).filter(k => k !== 'Unknown')];

  const currentStats = useMemo(() => {
    if (selectedSection === 'All') {
      return statsData.global;
    }
    return statsData.sections[selectedSection];
  }, [selectedSection]);

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
          {sections.map(sec => (
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
        {selectedSection === 'All' && (
          <div className="space-y-8">
            {/* Page Stats Table */}
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

            {/* Dictionary Stats */}
            {statsData.dictionary && (
              <div className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden p-6">
                 <h3 className="text-xl font-bold text-amber-500 mb-6 flex items-center gap-2">
                    <Book className="w-6 h-6" />
                    Dictionary Statistics
                 </h3>
                 
                 <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Left: Overview */}
                    <div>
                        <div className="mb-6">
                            <div className="text-sm text-slate-400 mb-1">Total Dictionary Entries</div>
                            <div className="text-4xl font-bold text-slate-100">{statsData.dictionary.total_entries}</div>
                        </div>

                        <h4 className="font-semibold text-slate-300 mb-4">Confidence Levels</h4>
                        <div className="space-y-3">
                            {Object.entries(statsData.dictionary.confidence_levels)
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
                                            style={{ width: `${(count / statsData.dictionary.total_entries) * 100}%` }}
                                        />
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Right: Domains */}
                    <div>
                        <h4 className="font-semibold text-slate-300 mb-4">Word Domains</h4>
                        <div className="grid grid-cols-2 gap-4">
                            {Object.entries(statsData.dictionary.domains)
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
        )}
      </div>
    </div>
  );
};

export default Stats;
