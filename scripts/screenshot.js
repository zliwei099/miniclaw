const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({
    viewport: { width: 1280, height: 800 }
  });
  
  // 打开 demo.html
  await page.goto('file:///Users/levy/.openclaw/workspace/miniclaw/frontend/demo.html');
  
  // 等待页面加载
  await page.waitForTimeout(2000);
  
  // 截图
  await page.screenshot({ 
    path: '/Users/levy/.openclaw/workspace/miniclaw/screenshots/demo.png',
    fullPage: false
  });
  
  console.log('截图已保存: screenshots/demo.png');
  
  await browser.close();
})();
