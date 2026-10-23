/* English-first UI translation adapter. Source strings remain Chinese for upstream compatibility.
 * This only translates exact, reviewed interface strings; unknown labels remain unchanged.
 * It does NOT translate video titles, performer names, user content, or metadata payloads.
 * Switching languages reloads the UI to avoid stale React / module-level localized constants.
 */
(function () {
  'use strict';
  const KEY = 'peach-ui-locale';
  const translations = {
  "首页": "Home",
  "艺人": "Performers",
  "厂牌": "Studios",
  "标签": "Tags",
  "JAV": "JAV",
  "已标记": "Bookmarked",
  "播放列表": "Playlists",
  "关注": "Following",
  "沉浸模式": "Immersive mode",
  "管理": "Manage",
  "统计": "Statistics",
  "口味": "Preferences",
  "人工复核": "Manual review",
  "数据管理": "Data management",
  "回收站": "Trash",
  "关注管理": "Manage follows",
  "高清版": "HD versions",
  "任务中心": "Task center",
  "Peach 配置": "Peach configuration",
  "来源": "Sources",
  "时长": "Duration",
  "产地": "Region",
  "画幅": "Orientation",
  "创作者": "Creators",
  "内容标签": "Content tags",
  "影片属性": "Video attributes",
  "关注标签": "Followed tags",
  "全部": "All",
  "本地": "Local",
  "在线": "Online",
  "未看": "Unwatched",
  "想看": "Watch later",
  "搜索": "Search",
  "搜索馆藏": "Search library",
  "搜索作品、女优、厂牌或标签": "Search titles, performers, studios or tags",
  "导航与筛选": "Navigation & filters",
  "展开导航与筛选": "Open navigation & filters",
  "退出搜索": "Exit search",
  "沉浸模式 · 随机连播": "Immersive mode · Shuffle",
  "进入沉浸模式": "Enter immersive mode",
  "播放墙": "Video wall",
  "进入播放墙": "Open video wall",
  "多选（Ctrl 单项，Shift 连续）": "Multi-select (Ctrl: individual, Shift: range)",
  "多选模式": "Multi-select mode",
  "密度：大图 / 密集": "Density: large / compact",
  "切换卡片密度": "Change card density",
  "设置": "Settings",
  "打开设置": "Open settings",
  "关闭设置": "Close settings",
  "跳到正文": "Skip to content",
  "未入库的新作": "New releases not in library",
  "Peach 安装教程": "Peach setup guide",
  "外观与导航": "Appearance & navigation",
  "浏览与播放": "Browsing & playback",
  "JAV 与新作": "JAV & new releases",
  "搜索与推荐": "Search & recommendations",
  "内容显示": "Content display",
  "媒体库与入库": "Library & importing",
  "来源与订阅": "Sources & subscriptions",
  "下载渠道": "Download services",
  "网络与访问": "Network & access",
  "应用与维护": "App & maintenance",
  "系统诊断": "System diagnostics",
  "设置分区": "Settings sections",
  "主题": "Theme",
  "增加对比度": "Increase contrast",
  "界面音效": "Interface sounds",
  "侧栏光晕": "Sidebar glow",
  "导航入口与顺序": "Navigation items & order",
  "相关推荐数量": "Number of related recommendations",
  "口味与记录": "Preferences & history",
  "打开口味与记录": "Open preferences & history",
  "SFW 模式": "Safe-for-work mode",
  "隐藏敏感画面，停止悬停预览。": "Hide sensitive imagery and disable hover previews.",
  "每批加载作品": "Items per batch",
  "每批作品": "Items per batch",
  "默认排序": "Default sort",
  "默认排序方向": "Default sort direction",
  "视频卡片大小": "Video card size",
  "作品显示": "Item display",
  "默认图片": "Default image",
  "合并分卷与版本": "Group parts & versions",
  "新作显示": "New release display",
  "新作自动滚动": "Auto-scroll new releases",
  "悬停预览延迟": "Hover preview delay",
  "打开详情自动播放": "Autoplay on opening details",
  "离开详情后小窗播放": "Mini-player after leaving details",
  "快进 / 快退步长": "Seek step",
  "快进 / 快退": "Seek forward / backward",
  "搜索记录数量": "Search history limit",
  "搜索记录": "Search history",
  "随机": "Random",
  "评分": "Rating",
  "高潮计数": "Climax count",
  "观看次数": "Play count",
  "体积": "File size",
  "入库时间": "Date added",
  "观看时间": "Last played",
  "降序": "Descending",
  "升序": "Ascending",
  "官方封面": "Official cover",
  "预览图": "Preview image",
  "大合集": "Compilation",
  "隐藏大合集": "Hide compilations",
  "单人合集": "Solo compilation",
  "隐藏单人合集": "Hide solo compilations",
  "切片": "Excerpts",
  "隐藏切片": "Hide excerpts",
  "保存": "Save",
  "保存配置": "Save configuration",
  "取消": "Cancel",
  "确定": "Confirm",
  "完成": "Done",
  "关闭": "Close",
  "打开": "Open",
  "清除": "Clear",
  "清空": "Empty",
  "删除": "Delete",
  "移除": "Remove",
  "编辑": "Edit",
  "重命名": "Rename",
  "添加": "Add",
  "创建": "Create",
  "新建": "New",
  "提交": "Submit",
  "重试": "Retry",
  "刷新": "Refresh",
  "重新加载": "Reload",
  "返回": "Back",
  "返回首页": "Return home",
  "上一步": "Previous",
  "下一步": "Next",
  "跳过": "Skip",
  "继续": "Continue",
  "更多": "More",
  "展开": "Expand",
  "收起": "Collapse",
  "展开全部": "Expand all",
  "收起全部": "Collapse all",
  "显示更多": "Show more",
  "加载更多": "Load more",
  "加载中": "Loading",
  "处理中": "Processing",
  "查看详情": "View details",
  "查看全部": "View all",
  "查看": "View",
  "详情": "Details",
  "复制": "Copy",
  "复制链接": "Copy link",
  "已复制": "Copied",
  "下载": "Download",
  "上传": "Upload",
  "导入": "Import",
  "导出": "Export",
  "整理": "Organize",
  "选择": "Select",
  "全选": "Select all",
  "取消全选": "Deselect all",
  "已选择": "Selected",
  "筛选": "Filter",
  "排序": "Sort",
  "重置": "Reset",
  "恢复默认": "Restore defaults",
  "确认删除": "Confirm deletion",
  "确认": "Confirm",
  "开": "On",
  "关": "Off",
  "启用": "Enable",
  "禁用": "Disable",
  "已启用": "Enabled",
  "已禁用": "Disabled",
  "自动": "Automatic",
  "手动": "Manual",
  "未知": "Unknown",
  "无": "None",
  "暂无数据": "No data yet",
  "没有结果": "No results",
  "暂无结果": "No results yet",
  "无匹配结果": "No matching results",
  "操作失败": "Operation failed",
  "保存成功": "Saved successfully",
  "保存失败": "Save failed",
  "成功": "Success",
  "失败": "Failed",
  "错误": "Error",
  "警告": "Warning",
  "名称": "Name",
  "标题": "Title",
  "描述": "Description",
  "日期": "Date",
  "时间": "Time",
  "状态": "Status",
  "进度": "Progress",
  "大小": "Size",
  "路径": "Path",
  "文件": "File",
  "文件夹": "Folder",
  "位置": "Location",
  "类型": "Type",
  "版本": "Version",
  "语言": "Language",
  "字幕": "Subtitles",
  "播放": "Play",
  "暂停": "Pause",
  "停止": "Stop",
  "上一集": "Previous episode",
  "下一集": "Next episode",
  "音量": "Volume",
  "全屏": "Fullscreen",
  "退出全屏": "Exit fullscreen",
  "倍速": "Playback speed",
  "画质": "Video quality",
  "切换": "Switch",
  "预览": "Preview",
  "封面": "Cover",
  "海报": "Poster",
  "作品": "Works",
  "影片": "Videos",
  "视频": "Video",
  "资源": "Resources",
  "演员": "Performers",
  "女优": "Actresses",
  "事务所": "Agencies",
  "卖家": "Sellers",
  "合集": "Collections",
  "系列": "Series",
  "分类": "Categories",
  "数据上传": "Data sharing",
  "开机自启": "Start with system",
  "开机后启动 Peach": "Launch Peach at startup",
  "只启动托盘，不打开网页": "Start in tray without opening browser",
  "在桌面创建快捷方式": "Create desktop shortcut",
  "可用": "Available",
  "不可用": "Unavailable",
  "连接": "Connect",
  "断开连接": "Disconnect",
  "本地媒体库": "Local media library",
  "扫描": "Scan",
  "开始扫描": "Start scan",
  "重新扫描": "Rescan",
  "媒体库": "Media library",
  "已完成": "Completed",
  "排队中": "Queued",
  "正在运行": "Running",
  "正在扫描": "Scanning",
  "手动添加": "Add manually",
  "更新": "Update",
  "检查更新": "Check for updates",
  "检查": "Check",
  "设置密码": "Set password",
  "密码": "Password",
  "登录": "Sign in",
  "退出登录": "Sign out",
  "访问密码": "Access password",
  "账号": "Account",
  "网络": "Network",
  "维护": "Maintenance",
  "高级设置": "Advanced settings",
  "详细设置": "Detailed settings",
  "诊断": "Diagnostics",
  "大图 · 竖幅头像": "Large · Portrait",
  "紧凑 · 圆形头像": "Compact · Circular",
  "大图 · 完整标识": "Large · Full logo",
  "紧凑 · 圆形标识": "Compact · Circular logo",
  "大图": "Large",
  "紧凑": "Compact",
  "艺人列表": "Performer list",
  "艺人资料": "Performer profile",
  "索引": "Index",
  "网盘": "Cloud drives",
  "绑定": "Link",
  "取消关注": "Unfollow",
  "立即关注": "Follow",
  "加入想看": "Add to watchlist",
  "从想看移除": "Remove from watchlist",
  "收藏": "Favorites",
  "取消收藏": "Remove favorite",
  "我的收藏": "My collection",
  "新作": "New releases",
  "推荐": "Recommendations",
  "最近播放": "Recently played",
  "播放历史": "Watch history",
  "全部作品": "All works",
  "本地作品": "Local works",
  "在线作品": "Online works",
  "暂无内容": "Nothing here yet",
  "只填域名，留空用默认地址": "Enter a domain only; leave blank to use the default address",
  "JavDB 或 MISSAV 打不开时，填一个能打开的镜像域名。": "If JavDB or MISSAV is unavailable, enter an accessible mirror domain.",
  "访问密码不正确": "Incorrect access password",
  "保持登录": "Stay signed in",
  "欢迎使用 Peach": "Welcome to Peach",
  "添加媒体库，开始整理馆藏。": "Add a media library and start organizing your collection.",
  "请在运行 Peach 的这台电脑上打开设置。": "Open setup on the computer running Peach.",
  "返回首次设置": "Back to first-time setup",
  "使用已有数据目录": "Use existing data directory",
  "完成设置后扫描并补全资料": "Scan and enrich metadata after setup",
  "请选择媒体读取策略": "Choose a media access policy",
  "开启后，访问 Peach 需要先登录。": "When enabled, you must sign in to access Peach.",
  "未设置密码时，能连接到 Peach 的设备可直接进入。": "Without a password, devices that can reach Peach can access it directly.",
  "请输入 8–256 个字符。": "Enter 8–256 characters.",
  "完成设置后": "After setup",
  "读取已有 NFO 和封面，采集缺失资料。符合自动规则的资料会在处理完成后保存到数据库，其余资料留待确认。": "Read existing NFO files and artwork, then retrieve missing metadata. Eligible automatic updates are saved when processing finishes; others require confirmation.",
  "浏览器历史记录": "Browser history",
  "可选": "Optional",
  "接下来导入浏览器历史记录": "Import browser history next",
  "用于生成口味分析。完成设置后选择读取这台电脑，或导入其他设备的记录；也可稍后从「口味」进入。": "Used for preference analysis. After setup, read this computer's browser history or import another device's records. You can also do this later under Preferences.",
  "版本统计与错误诊断": "Version statistics & error diagnostics",
  "馆藏与口味明细上传默认关闭，可在「应用与维护」查看并选择。": "Sharing detailed library and preference data is off by default. Review and enable it under App & maintenance.",
  "完成设置": "Finish setup",
  "设置完成": "Setup complete",
  "正在启动馆藏。": "Starting your library.",
  "已连接已有数据目录。": "Connected to the existing data directory.",
  "首次扫描已排队，在后台整理媒体库，期间可以照常使用 Peach。": "The first scan is queued and will organize your library in the background. You can continue using Peach.",
  "稍后在配置页开始扫描媒体库。": "You can start scanning the library later from Configuration.",
  "导入浏览器历史记录": "Import browser history",
  "进入 Peach": "Enter Peach",
  "运行信息": "Runtime information",
  "已有数据目录": "Existing data directory",
  "选择包含 config.toml 和 database 文件夹的数据目录。": "Select a data directory containing config.toml and the database folder.",
  "正在连接数据目录…": "Connecting to data directory…",
  "使用此目录": "Use this directory",
  "媒体目录": "Media folder",
  "数据目录": "Data directory",
  "读取方式": "Access method",
  "添加目录": "Add folder",
  "选择文件夹": "Choose folder",
  "读取": "Read",
  "写入": "Write",
  "启动": "Start",
  "稍后": "Later",
  "已连接": "Connected",
  "浏览器": "Browser",
  "打开浏览器": "Open browser",
  "浏览器记录": "Browser records",
  "首选项": "Preferences",
  "数据备份": "Data backup",
  "恢复备份": "Restore backup",
  "从备份恢复": "Restore from backup",
  "确认密码": "Confirm password",
  "输入密码": "Enter password",
  "登录 Peach": "Sign in to Peach",
  "开始使用": "Get started",
  "密码不匹配": "Passwords do not match",
  "隐藏密码": "Hide password",
  "显示密码": "Show password",
  "许可证": "License",
  "目录不存在": "Directory does not exist",
  "连接失败": "Connection failed",
  "读取失败": "Read failed",
  "稍后再试": "Try again later",
  "错误详情": "Error details",
  "打开配置": "Open configuration"
};
  const locale = (() => {
    try { return localStorage.getItem(KEY) === 'zh-CN' ? 'zh-CN' : 'en-US'; }
    catch { return 'en-US'; }
  })();
  document.documentElement.lang = locale;
  const title = locale === 'en-US' ? 'Peach' : 'Peach · 蜜桃';
  document.title = title;

  function installSelector() {
    const select = document.getElementById('peachLocale');
    if (!select) return;
    select.value = locale;
    select.addEventListener('change', () => {
      const next = select.value === 'zh-CN' ? 'zh-CN' : 'en-US';
      try { localStorage.setItem(KEY, next); }
      catch { /* Language preference cannot persist in restricted storage. */ }
      document.dispatchEvent(new CustomEvent('peach:locale-changed', { detail: next }));
      window.location.reload();
    });
  }

  if (locale !== 'en-US') {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', installSelector, { once: true });
    else installSelector();
    return;
  }

  const skipSelector = 'script,style,noscript,svg,pre,code,textarea,[contenteditable="true"],[data-i18n-skip]';
  const attrs = ['title', 'aria-label', 'aria-placeholder', 'placeholder', 'data-placeholder'];
  const hasChinese = /[\u3400-\u9fff]/;
  const originals = new WeakMap();

  function translate(value) {
    const trimmed = value.trim();
    if (!trimmed || !hasChinese.test(trimmed)) return null;
    const english = translations[trimmed];
    return english === undefined ? null : value.replace(trimmed, english);
  }

  function eligible(el) {
    if (!el || el.closest(skipSelector)) return false;
    // Skip searchable media results and creator names, but retain control labels inside cards.
    if (el.closest('#grid, [data-media-id], [data-work-id], .media-card, .catalog-card, .performer-card')
        && !el.closest('button, label, select, [role="button"], [role="tab"]')) return false;
    return true;
  }

  function translateText(node) {
    const el = node.parentElement;
    if (!eligible(el)) return;
    const value = node.nodeValue || '';
    if (value.length > 120) return;
    const en = translate(value);
    if (en !== null && en !== value) {
      originals.set(node, value);
      node.nodeValue = en;
    }
  }

  function translateElement(el) {
    if (!eligible(el)) return;
    for (const name of attrs) {
      if (!el.hasAttribute(name)) continue;
      const original = el.getAttribute(name) || '';
      if (original.length > 120) continue;
      const en = translate(original);
      if (en !== null && en !== original) el.setAttribute(name, en);
    }
  }

  function scan(node) {
    if (node.nodeType === Node.TEXT_NODE) { translateText(node); return; }
    if (node.nodeType !== Node.ELEMENT_NODE && node.nodeType !== Node.DOCUMENT_NODE) return;
    const element = node.nodeType === Node.ELEMENT_NODE ? node : null;
    if (element && element.matches(skipSelector)) return;
    if (element) translateElement(element);
    const walker = document.createTreeWalker(node, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT, {
      acceptNode(candidate) {
        if (candidate.nodeType === Node.ELEMENT_NODE &&
            candidate.matches(skipSelector)) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      },
    });
    while (walker.nextNode()) {
      const current = walker.currentNode;
      if (current.nodeType === Node.TEXT_NODE) translateText(current);
      else translateElement(current);
    }
  }

  function start() {
    installSelector();
    scan(document.body);
    const pending = new Set();
    let scheduled = false;
    const flush = () => {
      scheduled = false;
      for (const node of pending) scan(node);
      pending.clear();
    };
    const observer = new MutationObserver(records => {
      for (const record of records) {
        if (record.type === 'childList') {
          for (const node of record.addedNodes) pending.add(node);
        } else if (record.type === 'characterData') pending.add(record.target);
        else if (record.type === 'attributes') pending.add(record.target);
      }
      if (!scheduled && pending.size) { scheduled = true; requestAnimationFrame(flush); }
    });
    observer.observe(document.body, {
      subtree: true, childList: true, characterData: true, attributes: true, attributeFilter: attrs,
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, { once: true });
  else start();
})();
