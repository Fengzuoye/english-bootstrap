# 第三方数据与许可

| 数据/资源 | 用途 | 许可与来源 |
|---|---|---|
| WordNet 3.1 | 一般词释义、词义范畴、词频次序 | Princeton University；WordNet License（自由使用，保留版权声明） |
| CMUdict | 美式发音（ARPAbet） | Carnegie Mellon University；BSD-2-Clause |
| ipa-dict (en_US) | 补充 IPA | open-dict-data；MIT |
| Oxford 3000 词表 | 仅作为目标词表/排期，不包含牛津释义文本 | © Oxford University Press；本仓库不重新分发其释义内容 |
| ECDICT | 可选的中文释义源（脚本备选，未随仓库分发） | MIT（skywind3000/ECDICT） |

本仓库的 `layers/` 自举文本、`tools/` 脚本、App/网页代码为原创，采用 MIT 许可。
生成物 `dict.json` / `general.json` / `grammar.json` 由上述数据派生：
- `general.json` 的释义文本来自 WordNet，属 WordNet License 覆盖范围；
- 音标来自 CMUdict / ipa-dict；
- 分类与情景标注为派生数据。

若你要二次分发，请保留本文件与 `LICENSE`。
