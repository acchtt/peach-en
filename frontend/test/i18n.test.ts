import { describe, expect, it } from 'vitest';
import catalog from '../../web/peach-ui-en.json';
import { uiText } from '../src/i18n';

describe('English-first source-level interface copy', () => {
  it('translates primary navigation and setup text', () => {
    expect(uiText('首页', 'en-US')).toBe('Home');
    expect(uiText('访问密码', 'en-US')).toBe('Access password');
    expect(uiText('添加媒体库', 'en-US')).toBe('Add media library');
    expect(uiText('设置完成', 'en-US')).toBe('Setup complete');
  });

  it('preserves Chinese when selected', () => {
    expect(uiText('首页', 'zh-CN')).toBe('首页');
    expect(uiText('保存配置', 'zh-CN')).toBe('保存配置');
  });

  it('leaves unknown media titles, paths and user data unchanged', () => {
    for (const value of ['ABP-123', 'R:\\My Videos\\Movie.mkv', '未翻译的个人片名']) {
      expect(uiText(value, 'en-US')).toBe(value);
    }
  });

  it('keeps reviewed UI translations unique and non-empty', () => {
    expect(Object.keys(catalog).length).toBeGreaterThanOrEqual(390);
    for (const [chinese, english] of Object.entries(catalog)) {
      expect(chinese.trim()).not.toBe('');
      expect(english.trim()).not.toBe('');
      expect(uiText(chinese, 'en-US')).toBe(english);
    }
  });
});
