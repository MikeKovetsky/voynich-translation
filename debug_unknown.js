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

const unknownPages = [];
Object.keys(t).forEach(p => {
    if (getSection(p) === "Unknown") {
        unknownPages.push(p);
    }
});

console.log("First 10 Unknown Pages:", unknownPages.slice(0, 10));
console.log("Content of first Unknown:", t[unknownPages[0]]?.slice(0, 100));
