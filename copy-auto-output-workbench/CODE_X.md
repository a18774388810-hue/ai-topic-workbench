# 在 Codex（或其他 AI CLI）里使用本 Skill

本 Skill 的格式（`SKILL.md` + `name/description` + `references/` + `assets/`）与 Codex 通用，几乎无缝迁移，只有「配图背景生成」一处需要替换。

## 1. 复制到 Codex 的 skill 目录

```bash
mkdir -p ~/.agents/skills
cp -r copy-auto-output-workbench ~/.agents/skills/
```

> 旧版 Codex 用 `~/.codex/skills/` 也兼容；项目级可放 `项目目录/.agents/skills/`。

## 2. 触发方式

- **手动**：输入 `/skills` 选择本 skill，或直接说「出选题」「文案自动化输出工作台」。
- **自动**：`description` 已写清触发条件，Codex 会根据任务自动匹配。

## 3. 唯一需要替换的：配图背景生成

- 本 skill 配图环节里的 **`ImageGen` 是 WorkBuddy 内置工具，Codex 里没有**。
- 在 Codex 里，把「AI 生成封面背景图」这一步替换成你环境可用的任意图像生成方式（OpenAI 图像 API / DALL-E / 其他图像 MCP）。
- 生成时照 `cover-sop.md` 的 prompt 要求（**no text + 留白方位 + 克制**），拿到背景图后再交给 `make_*.py` 叠字。
- `assets/` 里的 `make_*.py` 是纯 Python，装 Pillow + 字体（`assets/SourceHanSansCN-Heavy.otf`）即可跑，只需改脚本里 `FONT` / `OUT` / 背景图路径。

## 4. 其他说明

- `style-profile.md` / `industry-knowledge.md` 是纯知识文档，直接读即可，**无需重新抓飞书**（本仓库未包含这两个文件，需自备）。
- 风格画像默认取自作者本人；用你自己的风格，替换 `style-profile.md` 里的画像和思维框架即可。
- `industry-knowledge.md` 里的行业知识和金句，也换成你自己领域的。
