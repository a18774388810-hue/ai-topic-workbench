# 文案自动化输出工作台（copy-auto-output-workbench）

电商 + AI 博主（尹晨）的文案自动化输出工作台：**热点选题 → 选稿 → 风格化创作 → 配图 → 交付**，五步闭环一次成型。

## 这是什么

一套把「每日内容创作」固化成标准动作的 Skill，包含四块核心资产：

- **四栏选题法**：①AI 素材创作 / ②AI 岗位提效 / ③AI+电商行业趋势 / ④AI+商业，每栏 5 个，每个选题给「是什么 + 为什么选」
- **风格画像**：`references/style-profile.md` —— **未随仓库开源**，请自备（下面「换用自己的风格」一节说明怎么写）
- **行业知识库**：`references/industry-knowledge.md` —— **未随仓库开源**，请自备自己领域的同结构文件
- **配图 SOP**：见 `references/cover-sop.md`（公众号封面 16:9 + 文内图 3 张 + 小红书 6 张带页码，科技风单元素配色）

## 安装（WorkBuddy）

1. 解压本包，得到 `copy-auto-output-workbench/` 文件夹
2. 把整个文件夹复制到 `~/.workbuddy/skills/` 目录下
3. 重启 WorkBuddy（或等待 skill 扫描生效）

## 调用

在对话里直接说：

- **「出选题」** / **「今天写什么」** —— 出四栏 × 5 = 20 个选题
- 选定后说 **「栏目 + 编号」**，例如「素材创作的第 2 个」
- 或直接说 **「走内容生产线」** / **「文案自动化输出工作台」**

## 在 Codex（或其他 AI CLI）里用

见同目录的 `CODE_X.md`——格式通用，复制到 `~/.agents/skills/` 即可，唯一要替换的是配图环节的图像生成工具（ImageGen 是 WorkBuddy 内置）。

## 环境依赖

| 依赖 | 说明 |
|---|---|
| ImageGen | WorkBuddy 内置，生成封面背景图（消耗 credit）；其他环境换成任意图像生成工具 |
| Python + Pillow | 配图脚本需要（`pip install pillow`） |
| 字体 | `assets/SourceHanSansCN-Heavy.otf`（配图叠字必需） |
| lark-cli + 飞书授权 | 仅原作者抓取风格素材时用，别人可跳过 |

## 重要：风格替换

`references/style-profile.md`（**未随仓库开源**）里是作者本人的风格画像、思维框架和创作红线。如果你想用自己的风格创作：

1. 自己写一份 `style-profile.md`：标题风格、语气、真实经历、观点、思维框架
2. 或把自己的历史内容喂给 AI，让它按「表层风格 + 深层思维框架」两层提炼一份画像
3. 行业知识和金句也换成你自己领域的，另存为 `industry-knowledge.md`

## 配图脚本路径说明

`assets/` 里的 `make_*.py` 是配图模板脚本，里面的路径是原作者的绝对路径，**使用前请改成你自己的**：

- `FONT` → 字体文件路径
- `COVERS` / `OUT` → 你的工作目录
- `GZH_BG` / `XHS_BG` → 你的 AI 生成背景图路径

新选题复用：复制脚本 → 改 OUT 目录名、背景图路径、标题与卡片文案 → 运行。
