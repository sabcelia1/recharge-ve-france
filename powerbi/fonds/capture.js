// Convertit html/*.html en png/*.png (2560x1440, soit 1280x720 en résolution x2)
const path = require('path');
const fs = require('fs');
let playwright;
try { playwright = require('playwright'); }
catch { playwright = require('/opt/npm-tools/node_modules/playwright'); }

(async () => {
  const dir = __dirname;
  fs.mkdirSync(path.join(dir, 'png'), { recursive: true });
  const browser = await playwright.chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 2 });
  for (const f of fs.readdirSync(path.join(dir, 'html')).filter(f => f.endsWith('.html'))) {
    await page.goto('file://' + path.join(dir, 'html', f));
    await page.waitForTimeout(200);
    await page.screenshot({ path: path.join(dir, 'png', f.replace('.html', '.png')) });
    console.log('png :', f);
  }
  await browser.close();
})();
