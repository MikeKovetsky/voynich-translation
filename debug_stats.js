const fs = require("fs");
const t = JSON.parse(fs.readFileSync("web/src/data/translations.json", "utf8"));

const getSection = (page) => {
  const match = page.match(/f(\d+)([rv]?)/);
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
  const cleanText = text.replace(/\*\*.*?\*\*/g, '').replace(/#.*/g, '');
  const words = cleanText.split(/\s+/).filter(w => w.length > 0);
  if (words.length === 0) return 0;
  if (text.length < 50) return 0;
  const questionMarks = (text.match(/\?/g) || []).length;
  const unknownTags = (text.match(/UNKNOWN|verb \(unknown\)/g) || []).length;
  let confidence = 100.0;
  const penalty = (questionMarks + unknownTags) * 2;
  confidence -= (penalty / Math.max(words.length, 1)) * 100;
  return Math.max(0, Math.min(100, parseFloat(confidence.toFixed(1))));
};

const sections = {};
let totalConf = 0;
let totalCount = 0;

Object.entries(t).forEach(([page, text]) => {
  const s = getSection(page);
  if (!sections[s]) sections[s] = { sum: 0, count: 0 };
  
  if (text.length > 50 && !text.slice(0, 10).includes('?')) {
      const conf = calculateConfidence(text);
      sections[s].sum += conf;
      sections[s].count++;
      totalConf += conf;
      totalCount++;
  }
});

console.log("Global Avg:", totalCount ? (totalConf / totalCount).toFixed(1) : 0);
Object.keys(sections).forEach(k => {
    const sec = sections[k];
    console.log(`${k}: ${sec.count ? (sec.sum / sec.count).toFixed(1) : 0} (n=${sec.count})`);
});
