# English Bootstrap · 英语自举词库与 App

从 201 个公理词出发，只用**已经定义过的英语词**解释新词，一层层扩展到牛津 3000，
并把这套词库做成可离线使用的 Android App 与网页版。

## 1. 实现了什么

### 1.1 分层自举词库（layers/）
- `layer0.md`：201 个公理词（不解释，直接记忆，含中文速记）。
- `layer1.md` / `layer2.md`：**语法自举**，共 117 条语法知识（词性、句子结构、
  名词与冠词、代词、时态、语态、比较、从句、条件句、间接引语、非谓语、
  there be/it、连接词……），每条含英文定义与例句。
- `layer3.md` ~ `layer29.md`：牛津 3000 逐批定义（每批 25–308 词）。
- 硬规则：定义只能使用「第 0 层 + 之前已定义词」；例句从第 24 层起不再限制用词。
- `tools/check.py` 逐层严格校验（词性、词形变化、用词是否超纲、重复定义等）。

当前状态：**L0–L29 全部通过校验**；对照公开牛津 3000 清单（2967 项，英美拼写归并）
**剩余待定义 0 项**；累计定义 3258 词 + 27 词组。

### 1.2 App 词典数据（App 内离线）
| 数据 | 条数 | 说明 |
|---|---|---|
| `dict.json` | 3285 | 自举词条（其中 2937 条属于牛津 3000），带词性/释义/例句/音标/层级/大小范畴 |
| `general.json` | 131092 | 一般词（WordNet 全量），含 77 个小情景分类、音节音标；其中 1577 条是“释义里出现但未收录”的低频学术词补全（allele、chromosome、adenosine…） |
| `grammar.json` | 19 主题 / 117 词卡 / 79 例句 | 语法 Accordion 数据（讲解 + 例句 + 词汇卡片） |
| 音标覆盖 | dict 3280/3285，general 74247/131092 | 来源 CMUdict + ipa-dict，ARPAbet→IPA 并标注重音 |

### 1.3 Android App（android/english-bootstrap-app）
- 三个页签：**文章**（粘贴/抓取网页，逐词点查）、**词典**、**词库**。
- 词库导航：词库 → 牛津 3000 / 一般词 → 层或大范畴 → 小情景 → 词卡；
  分类条与搜索框**吸顶固定**，分类区与词卡区**各自独立滚动**；
  小分类支持**左右滑动**选择。
- 词卡直接展开陈列：单词、词性、音标、释义、例句、层级注释。
- **全词典搜索**：任何位置的搜索框都同时搜三千词 + 一般词。
- **双击释义中的单词**继续查词（单击只高亮），弹层带「← 上一个」。
- **序号跳转**：固定头部有 `跳转至 [输入] / 总词数`，数字键盘、回车/按钮跳转、
  越界自动纠正、滚动时自动回填当前序号。
- **层级返回**：返回按钮 / Android 返回键 / 左边缘右滑 Pop 回上一级，
  并恢复搜索词、层级与滚动位置。
- **外部图片搜索**：满足「词性 AND 分类」的词卡显示 44×44 图标 →
  打开百度图片搜索（国内可访问），专属领域动词使用人工关键词
  （如 `suture medical procedure`、`weld mechanical action`）。
- 发布包：`dist/EnglishBootstrapReader-v1.4.apk`（约 5.5 MB，Android 7.0+，调试签名）。

### 1.4 网页版与阅读版
- 网页版（`web/`）：单文件夹，双击 `index.html` 即可用（数据以 `data-*.js` 加载，
  不需要服务器、不受 `file://` fetch 限制），功能与 App 一致。
- 阅读版（`read/`）：`tools/build_read.py` 生成的逐层阅读 HTML，
  支持自测模式（遮住释义）。

## 2. 获取方式

### A. 直接使用（推荐）
1. 手机：安装 `dist/EnglishBootstrapReader-v1.4.apk`（允许“未知来源”）。
2. 电脑：解压 `dist/BootstrapReader-web.zip`，双击 `index.html`。
3. GitHub 发布建议：把 APK 与网页 zip 作为 **Release assets** 上传，
   源码仓库只保留代码与 markdown。
   （`english-bootstrap-v1.4-source.zip` 为纯源码包，不含 `dist/` 产物。）

### B. 从源码构建
环境：Python 3.10+；可选 JDK 11 + Android build-tools/platform（自行构建 APK）。

```bash
# 0) 取数据源（WordNet 3.1 需手动下载，其余自动）
python tools/fetch_data.py           # CMUdict / ipa-dict / Oxford 清单 → data_src/
#    WordNet 3.1: 下载 wn3.1.dict.tar.gz 解压到 data_src/wordnet_nltk/wordnet

# 1) 校验自举层
python tools/check.py                 # 期望：检查通过，累计 3258 词 + 27 词组

# 2) 生成 App 数据
export BOOTSTRAP_WORK=$(pwd)/../data_src   # Windows: $env:BOOTSTRAP_WORK="...\data_src"
python tools/export_dict.py           # → assets/dict.json
python tools/build_general.py         # → assets/general.json
python tools/build_orphans.py         # 补全释义中缺失的低频词
python tools/build_grammar.py         # → assets/grammar.json

# 3) 生成阅读版 / 网页版
python tools/build_read.py
python tools/build_web.py
```

一键脚本：`scripts/build_all.ps1`（Windows）与 `scripts/fetch_data.py` 配合使用。

### C. 只要数据
`android/english-bootstrap-app/app/src/main/assets/` 下的
`dict.json`（3285 条自举词）、`general.json`（131092 条一般词）、
`grammar.json`（语法 Accordion）可直接用于你自己的学习/查询程序。
仓库中不含这三个生成物时，按上面 B 步骤生成。

## 3. 目录结构

```
layers/           layer0..layer29 自举层（唯一事实来源）
tools/            构建与校验脚本（层校验、词典生成、音标、语法数据、网页版）
android/english-bootstrap-app/   Android 工程（Java + WebView）
read/             build_read.py 生成的阅读版 HTML
web/              build_web.py 生成的网页版（data-*.js 内嵌数据）
dist/             发布产物（APK、网页版 zip）
scripts/          fetch_data.py / build_all.ps1
```

## 4. 使用说明（App / 网页版）
- **查词**：任意页面的搜索框都是全词典搜索；结果带 3000/语法/一般 标记。
- **释义里查词**：点开词条后，双击释义中的任意单词查看它的释义，可「← 上一个」回退。
- **分类阅读**：牛津 3000 分 6 层（语法基础 / 入门基础 / 常用扩展 / 生活进阶 /
  社会抽象 / 高频收尾）；一般词按大范畴 → 小情景（77 个）。
- **词频分段**：单类超过 800 词自动分 高频/中频/低频，先读高频。
- **快速定位**：顶部 `跳转至 [序号] / 总词数`，输入后回车即可平滑滚到该卡。
- **图片辅助**：名词具体事物与专属领域动词的卡片右上角有图片搜索按钮，
  跳百度图片（外部浏览器打开，返回后仍在原位置）。

## 5. 数据来源与许可
- 自举层、分类词表、App 代码：见 `LICENSE`（MIT）。
- WordNet 3.1：Princeton University，WordNet License（可自由使用，需保留声明）。
- CMUdict：Carnegie Mellon University，BSD-2-Clause。
- ipa-dict（open-dict-data）：MIT。
- 牛津 3000 词表：© Oxford University Press，仅作为“目标词表”用于统计与排期，
  **不重新分发牛津释义文本**；App 内一般词释义来自 WordNet 等开源数据。
- 详见 `NOTICE.md`。

## 6. 已知限制
- 牛津词典释义无免费可打包数据，一般词使用 WordNet 英英释义（近似牛津风格）。
- IPA 覆盖：生僻、CMUdict 未收录的单词不显示音标，不硬造。
- 大小范畴/小情景为 WordNet 词法域 + 释义关键词自动标注，个别词可能归类不精确。
- APK 为调试签名；如需正式发布请自行生成签名密钥。
