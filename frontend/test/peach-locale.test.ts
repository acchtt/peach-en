import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';

const localeAdapter = readFileSync(
  fileURLToPath(new URL('../../web/peach-locale.js', import.meta.url)), 'utf8',
);

function runAdapter() {
  // The adapter is intentionally a dependency-free classic script, also served on login.
  new Function(localeAdapter)();
  if (document.readyState === 'loading') document.dispatchEvent(new Event('DOMContentLoaded'));
}

describe('English-first locale adapter', () => {
  it('keeps original Chinese UI when requested', () => {
    localStorage.setItem('peach-ui-locale', 'zh-CN');
    document.body.innerHTML = '<header><select id="peachLocale"><option value="en-US">English</option><option value="zh-CN">中文</option></select><button>设置</button></header>';
    runAdapter();
    expect(document.documentElement.lang).toBe('zh-CN');
    expect(document.querySelector('button')?.textContent).toBe('设置');
    expect((document.getElementById('peachLocale') as HTMLSelectElement).value).toBe('zh-CN');
  });

  it('defaults to English, translates dynamic buttons, preserves user media metadata', async () => {
    localStorage.removeItem('peach-ui-locale');
    document.body.innerHTML = [
      '<header><select id="peachLocale"><option value="en-US">English</option><option value="zh-CN">中文</option></select>',
      '<button title="打开设置" aria-label="打开设置">设置</button></header>',
      '<main><div id="grid"><article class="media-card"><h2>首页</h2></article></div>',
      '<input placeholder="搜索馆藏"><section data-settings-host><p>外观与导航</p></section></main>',
    ].join('');
    runAdapter();
    expect(document.documentElement.lang).toBe('en-US');
    expect(document.querySelector('header button')?.textContent).toBe('Settings');
    expect(document.querySelector('header button')?.getAttribute('aria-label')).toBe('Open settings');
    expect(document.querySelector('input')?.placeholder).toBe('Search library');
    expect(document.querySelector('[data-settings-host]')?.textContent).toBe('Appearance & navigation');
    expect(document.querySelector('.media-card h2')?.textContent).toBe('首页');

    const later = document.createElement('button');
    later.textContent = '保存配置';
    document.body.append(later);
    await new Promise<void>((resolve) => setTimeout(resolve, 50));
    expect(later.textContent).toBe('Save configuration');
    expect((document.getElementById('peachLocale') as HTMLSelectElement).value).toBe('en-US');
  });
});
