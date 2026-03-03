# 分享 CAM User Guide Writer Skill 给同事

## 📦 分享文件

**文件位置**: `/Users/jessiecao/.claude/skills/cam-user-guide-writer/cam-user-guide-writer.skill`

**文件大小**: 3.3 MB (包含示例截图)

## 🚀 快速分享步骤

### 1. 发送文件

通过以下任一方式发送 `cam-user-guide-writer.skill` 文件:

- 企业微信/钉钉
- 内部文件服务器
- 邮件附件
- 共享网盘

### 2. 同事安装

同事收到文件后,执行以下命令:

```bash
# 方法 1: 使用 Claude Code CLI (推荐)
claude skill install cam-user-guide-writer.skill

# 方法 2: 手动安装
mkdir -p ~/.claude/skills/cam-user-guide-writer
tar -xzf cam-user-guide-writer.skill -C ~/.claude/skills/cam-user-guide-writer
```

### 3. 验证安装

```bash
# 检查 skill 是否安装成功
ls ~/.claude/skills/cam-user-guide-writer

# 应该看到以下文件:
# README.md
# SKILL.md
# OPTIMIZATION_SUMMARY.md
# references/
# scripts/
```

## 📖 使用说明

安装后,同事可以查看 `README.md` 获取完整使用说明:

```bash
cat ~/.claude/skills/cam-user-guide-writer/README.md
```

或者在 Claude Code 中直接触发 skill:

```
"I want to write a user guide for [feature name]"
```

## ⚙️ 配置要求

### 必须配置

同事需要提供自己的路径:

- **CAM docs 路径**: 默认 `/Users/jessiecao/src/cam-docs/`
- **CAM 代码路径**: 默认 `/Users/jessiecao/src/cam/`

Skill 会在首次使用时询问路径,或者同事可以直接告诉 skill:

```
"My CAM docs are at /path/to/cam-docs"
```

### 可选配置 (浏览器自动化)

如果同事想使用自动截图功能:

```bash
pip install playwright
playwright install chromium
```

## 📝 给同事的消息模板

你可以复制以下消息发送给同事:

---

**主题**: CAM User Guide Writer Skill - 自动化文档撰写工具

Hi,

我分享一个 Claude Code skill 给你,可以帮助快速撰写 CAM 用户指南文档。

**功能亮点**:
- ✅ 自动评估复杂度,选择合适的文档方法
- ✅ 可选浏览器自动截图 (省去手动截图时间)
- ✅ 自动搜索前后端代码,发现未记录的功能
- ✅ 遵循 CAM docs 规范 (VuePress frontmatter, 格式规则)
- ✅ 防止常见错误 (中文字符检测, markdown 语法检查)

**安装方法**:
```bash
claude skill install cam-user-guide-writer.skill
```

**使用方法**:
在 Claude Code 中说:
```
"I want to write a user guide for [功能名称]"
```

**完整文档**: 安装后查看 `~/.claude/skills/cam-user-guide-writer/README.md`

**注意事项**:
1. 首次使用时需要配置你的 CAM docs 和代码路径
2. 如果想用自动截图功能,需要安装 Playwright: `pip install playwright && playwright install chromium`

有问题随时找我!

---

## 🔄 版本更新

如果你后续更新了 skill,重新打包并分享:

```bash
cd /Users/jessiecao/.claude/skills/cam-user-guide-writer
rm -f cam-user-guide-writer.skill

python3 -c "
import tarfile
from pathlib import Path

with tarfile.open('cam-user-guide-writer.skill', 'w:gz') as tar:
    for item in Path('.').rglob('*'):
        if item.is_file() and not item.name.endswith('.skill'):
            tar.add(item, arcname=item.relative_to('.'))
"

echo "✅ 新版本已打包: cam-user-guide-writer.skill"
```

## 📊 Skill 统计

- **核心文件**: 310 行 (优化后,原 490 行)
- **参考文件**: 3 个 (按需加载)
- **Token 节省**: 简单文档节省 40%
- **支持复杂度**: Low / Medium / High 三级
- **自动化功能**: 浏览器截图 + 代码搜索

## 🆘 常见问题

### Q: 同事的路径和我不一样怎么办?
A: Skill 会自动询问路径,或者同事可以在对话中提供路径。

### Q: 浏览器自动化失败?
A: 检查 Chrome 是否用 `--remote-debugging-port=9222` 启动,并且已登录 CAM。

### Q: Skill 没有触发?
A: 确保消息中包含 "user guide", "documentation" 或 "docs" 关键词。

### Q: 如何更新 skill?
A: 重新打包并发送新的 `.skill` 文件,同事重新安装即可覆盖旧版本。

## 📞 支持

如果同事遇到问题:
1. 先查看 `README.md`
2. 查看 `OPTIMIZATION_SUMMARY.md` 了解架构
3. 联系你 (skill 创建者)
