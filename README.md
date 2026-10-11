# 尹晨 · AI 选题三件套

打包日期：2026-10-11
来源：`~/.workbuddy/skills/`

## 这三个技能是什么关系

**选题只有一个出口，一条主线、多个渠道落点。** 三个技能分工如下：

| 技能 | 在选题链路里的角色 |
|---|---|
| **文案自动化输出工作台**<br>`copy-auto-output-workbench` | **选题池的唯一口径来源。** 每日四栏 × 4 = 16 题；每题带「渠道落点」；另含「平台适配判定」（拿到公众号稿 → 先判定能不能转短视频/小红书，再决定怎么写）。 |
| **短视频工作台**<br>`短视频工作台` | **下游消费者。** 不另立选题标准，直接引用上面那份池子里标了 `✅ 可转` / `🔄 换角度` 的题，进入口播 → 录音 → 合成 → 封面。 |
| **小红书搜索词工作台**<br>`小红书搜索词工作台` | **上游供给 + 判定依据。** 抓小红书站内搜索下拉联想词，做成本赛道词表：①给选题的小红书落点当判定依据（这个词到底有没有人搜）②反向从词表倒推选题。 |

一句话：**选题池（工作台）→ 判定能不能吃（适配判定 + 搜索词表）→ 分发（短视频/小红书/播客）。**

---

## 安装

把三个文件夹整个拷到 `~/.workbuddy/skills/` 下即可：

```bash
cp -r copy-auto-output-workbench 短视频工作台 小红书搜索词工作台 ~/.workbuddy/skills/
```

重启 WorkBuddy（或重开会话）后，技能会被自动识别。触发词：

- 出选题 / 今天写什么 / 走内容生产线 → 文案自动化输出工作台
- 今天出片 / 写口播文案 / 合成口播成片 → 短视频工作台
- 抓小红书下拉词 / 更新小红书搜索词 / 这个小红书词有没有人搜 → 小红书搜索词工作台

---

## 运行依赖（换机器要留意）

所有路径都做成了**环境变量可覆盖**，不必改源码。

**文案自动化输出工作台**
- Python + PIL：脚本绘图（封面、小红书 6 图）用。
- 字体：思源黑体 Heavy（`SourceHanSansCN-Heavy.otf`）。**该字体文件不在本包内**，需自备并设 `SM_FONT`。
- 飞书归档：走 `lark-cli`，需要你自己的飞书授权。
- ImageGen：走宿主 AI 的内置出图能力。

**短视频工作台**
- `ffmpeg` / `ffprobe`（音频切片、混音、合成）
- `faster-whisper`（转写；需本地模型快照路径 + **取消代理**再跑，否则会去联网下载）

| 环境变量 | 用途 | 默认值 |
|---|---|---|
| `SM_BASE` | 单条视频的工作目录（口播、卡片、字幕、BGM 都在这下面找） | `~/single-video-demo` |
| `SM_FONT` | 思源黑体 Heavy 字体文件路径 | `~/fonts/SourceHanSansCN-Heavy.otf` |
| `WHISPER_MODEL` | faster-whisper 本地模型快照目录 | `~/.cache/huggingface/.../faster-whisper-small/...` |
| `CARD_FOOTER` | 卡片右下角落款文案 | `你的品牌 · AI+电商` |

工作目录里需要准备：`cards/anim.json`、`art_dark/`、`hypit_assets/`、`subpng/`、`bgm_real.wav` 等中间产物（由 `make_cards.py` / `gen_subs_overlay.py` 生成）。

**小红书搜索词工作台**
- Python 包 `websocket-client`（CDP 通信）
- 本机 Chrome：`/Applications/Google Chrome.app`
- 端口 **9335**、独立 profile（默认 `~/xhs-keywords/.chrome-profile`）

| 环境变量 | 用途 | 默认值 |
|---|---|---|
| `XHS_PORT` | Chrome 调试端口 | `9335` |
| `XHS_KEYWORDS_DIR` | 词表工作目录（profile / seeds / output 都在这下面） | `~/xhs-keywords` |

- 用法：
  ```bash
  bash scripts/start-chrome.sh                  # 起独立 Chrome
  python3 scripts/collect.py --seeds seeds.txt --out output
  ```
  `seeds.txt` 一行一个种子词；抓出来的词表在 `output/词表-YYYY-MM-DD.md`。
- **实测：不登录也能拿到下拉词**，不需要扫码。
- 注意：启动 Chrome 时不要用 `open -a`，也不要用 `pkill -f` 清理——会误杀正在用的浏览器。


---

## 文件清单

```
尹晨-AI选题三件套/
├── copy-auto-output-workbench/
│   ├── SKILL.md                      主流程（选题 / 判定 / 创作 / 配图 / 交付）
│   ├── references/
│   │   ├── topic-guide.md            ★ 选题池四栏口径 + 渠道落点格式（核心）
│   │   ├── platform-fit-check.md     ★ 平台适配判定（三关尺子 + 三平台差异）
│   │   ├── （style-profile.md        未开源：作者的个人风格画像）
│   │   ├── （industry-knowledge.md   未开源：付费教程提炼内容）
│   │   ├── cover-sop.md              配图规范
│   │   └── podcast-script.md         指针 → 播客技能
│   └── README.md / CODE_X.md
├── 短视频工作台/
│   ├── SKILL.md
│   ├── scripts/                      gen_audio / transcribe / render_frames /
│   │                                 make_cards / mix_bgm / gen_subs_overlay
│   └── assets/                       示意素材
└── 小红书搜索词工作台/
    ├── SKILL.md
    └── scripts/
        ├── start-chrome.sh           起独立 Chrome（端口 9335）
        └── collect.py                CDP 驱动打字 → 抓 recommend 接口 → 出词表
```

---

## 两处硬性规则（别改，改了会出问题）

1. **短视频封面：文字左右各留 14.5%，文字最大占宽 71%。** 这是实测出来的安全值，超过会被平台裁字。
2. **选题池不建第二套。** 公众号是主战场、其余渠道是衍生；给小红书单独出一套池子会把"一条主线"变成"两条主线"。
   正确做法是给每个选题标「渠道落点」，把"能不能转"的判定从写完之后提前到立项时。
