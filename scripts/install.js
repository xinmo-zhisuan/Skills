const fs = require("fs");
const path = require("path");
const os = require("os");

const SKILL_NAME = "fetch-bibtex";
const skillDir = path.join(os.homedir(), ".claude", "skills", SKILL_NAME);

fs.mkdirSync(skillDir, { recursive: true });

const filesToCopy = [
  { src: "SKILL.md", dest: "SKILL.md" },
  { src: "scripts/bibtex_fetcher.py", dest: "scripts/bibtex_fetcher.py" },
];

for (const { src, dest } of filesToCopy) {
  const srcPath = path.resolve(__dirname, "..", src);
  const destPath = path.join(skillDir, dest);
  fs.mkdirSync(path.dirname(destPath), { recursive: true });
  fs.copyFileSync(srcPath, destPath);
}

console.log(`fetch-bibtex skill installed to ${skillDir}`);
