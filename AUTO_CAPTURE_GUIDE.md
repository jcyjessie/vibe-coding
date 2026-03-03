# 全自动浏览器抓取使用指南

## 快速开始

### 步骤 1: 启动 Chrome 调试模式

在终端运行:

```bash
# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222

# Linux
chrome --remote-debugging-port=9222

# Windows
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
```

### 步骤 2: 登录 CAM

在刚才打开的 Chrome 窗口中:
1. 访问 https://cam.cammaster.org
2. 登录你的账号

### 步骤 3: 运行自动抓取脚本

在**另一个终端窗口**运行:

```bash
cd /Users/jessiecao/.claude/skills/cam-user-guide-writer/scripts

# 全自动模式 (推荐)
python auto_browse_cam.py \
  --url https://cam.cammaster.org/v3/analysis/reporting/routine \
  --feature-name routine-report
```

**就这样!** 脚本会自动:
- 导航到页面
- 点击所有下拉菜单、按钮、日期选择器
- 在每次交互后截图
- 提取 UI 标签和按钮文字
- 保存所有数据到 JSON

### 步骤 4: 查看结果

输出文件:
- `captured_data/routine-report_captured.json` - 结构化数据
- `captured_data/screenshots/` - 所有截图

## 两种模式对比

### 模式 1: 全自动 (推荐)

```bash
python auto_browse_cam.py --url <url> --feature-name <name>
```

**优点**:
- ✅ 完全自动,无需手动操作
- ✅ 快速 (30秒内完成)
- ✅ 一致性好 (每次抓取相同元素)
- ✅ 覆盖全面 (自动发现所有常见 UI 模式)

**适用于**: 标准 CAM 功能 (下拉菜单、日期选择器、过滤器等)

### 模式 2: 交互式

```bash
python browse_cam.py --url <url> --feature-name <name>
```

**工作流程**:
1. 你在浏览器中手动点击/输入
2. 按 ENTER 键截图
3. 描述你做了什么
4. 输入 'done' 完成

**适用于**: 复杂工作流、自定义交互、或自动模式遗漏的元素

## 自动模式工作原理

脚本分 3 个阶段探索页面:

**阶段 1: 初始状态**
- 截取页面加载后的状态
- 提取所有可见的按钮、输入框、下拉菜单

**阶段 2: 交互元素**
自动查找并点击:
- 日期/时间选择器
- 下拉菜单和选择框
- 过滤按钮
- 导出按钮
- 设置按钮

每次点击后自动截图

**阶段 3: 模态框/对话框**
- 检测打开的模态框
- 截取其内容

## 输出格式

```json
{
  "feature_name": "routine-report",
  "capture_date": "2026-03-02T10:30:00",
  "capture_mode": "automatic",
  "total_steps": 5,
  "steps": [
    {
      "step_number": 1,
      "step_name": "01-initial-page",
      "description": "Initial page load",
      "url": "https://cam.cammaster.org/...",
      "title": "Routine Report",
      "screenshot": "01-initial-page_20260302_103000.png",
      "buttons": ["Export", "Filter", "Refresh"],
      "input_fields": [...],
      "dropdowns": [...]
    }
  ]
}
```

## 常见问题

### Q: Chrome 连接失败?
A:
1. 确认 Chrome 用 `--remote-debugging-port=9222` 启动
2. 检查端口 9222 没有被其他进程占用
3. 尝试关闭所有 Chrome 窗口后重新启动

### Q: 自动模式遗漏了某些元素?
A:
1. 使用交互式模式手动控制
2. 或修改 `auto_browse_cam.py` 添加自定义选择器

### Q: 截图是空白的?
A:
1. 增加页面加载等待时间 (`wait_for_timeout`)
2. 检查元素是否真的可见
3. 使用交互式模式在正确时机截图

### Q: 截图中有中文字符?
A: 在抓取前将 CAM UI 语言设置为英文

## 高级用法

### 自定义选择器

编辑 `auto_browse_cam.py`,在 `selectors_to_try` 中添加:

```python
selectors_to_try = [
    # 你的自定义选择器
    ("[data-testid='my-element']", "my element"),
    ("button:has-text('My Button'):visible", "my button"),
]
```

### 调整等待时间

如果页面加载慢,修改:

```python
self.page.wait_for_timeout(2000)  # 改为 5000 (5秒)
```

## 完整示例

```bash
# 1. 启动 Chrome
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222

# 2. 在 Chrome 中登录 CAM

# 3. 在另一个终端运行
cd /Users/jessiecao/.claude/skills/cam-user-guide-writer/scripts
python auto_browse_cam.py \
  --url https://cam.cammaster.org/v3/analysis/reporting/routine \
  --feature-name routine-report

# 4. 查看结果
ls captured_data/screenshots/
cat captured_data/routine-report_captured.json
```

## 与 Skill 集成

当使用 `cam-user-guide-writer` skill 时:

1. Skill 会询问: "What materials do you have?"
2. 选择 **Option A: Live browser automation**
3. 选择 **Automatic mode**
4. Skill 会自动运行 `auto_browse_cam.py`
5. 使用抓取的数据生成文档

完全自动化,无需手动操作!

## V3 Improvements (March 2026)

### New Features
- **State-driven capture**: Detects URL and DOM changes to prevent duplicate captures
- **Selector abstraction**: Priority system (data-testid → aria-label → role → text)
- **Retry mechanism**: Exponential backoff for transient failures
- **Headless mode**: CI/CD compatible with `--headless` flag
- **Improved error handling**: Specific exceptions with context logging

### Usage
```bash
# Login with headless mode
python auto_login_cam_v3.py --username admin --password pwd --headless

# Capture with headless mode
python auto_browse_cam_v3.py --url <url> --feature-name <name> --headless
```
