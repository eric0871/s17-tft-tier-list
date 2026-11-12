# 字体来源与授权

页面只自托管下面两个字体，都是 SIL Open Font License 1.1（OFL，允许网页嵌入、子集化、随网站分发，不可单独售卖字体本身）。

| 文件 | 字体 | 用在哪 | 来源 | 授权 |
|---|---|---|---|---|
| `tektur-latin-var.woff2`（19 KB）| **Tektur**（可变字体：字重 400–900、字宽 75–100%）| 选手名、档位字母 S/A/B/C、所有数字 | npm `@fontsource-variable/tektur@5.3.0`（Google Fonts 同款，作者 Adam Jagosz，github.com/hyvyys/Tektur）| OFL 1.1，全文见 `OFL-Tektur.txt` |
| `smiley-sub.woff2`（约 50 KB）| **得意黑 Smiley Sans**（斜体展示黑体）| 所有中文：标题、档名「金铲铲」、中文 ID、面板标签 | npm `@fontpkg/smiley-sans@2.0.4`（atelierAnchor 出品，github.com/atelier-anchor/smiley-sans）| OFL 1.1，全文见 `OFL-SmileySans.txt` |

两者合计约 70 KB，远低于 1.5 MB 上限。

## 中文字体子集化

得意黑完整字体 1.1 MB，页面只用到几百个字，所以按实际用字裁剪：

- 源字体：`scripts/s18/font-src/SmileySans-Oblique.woff2`（未裁剪原版，不会被网页加载）
- 脚本：`scripts/s18/subset_fonts.py` —— 扫描 `template.html` 和 `site_players.json` 里出现的所有非 ASCII 字符，再加一小段预留字（奖金 / 生涯之类以后可能新加的数据标签），输出 `fonts/smiley-sub.woff2`
- 已接进生成流程：`python3 assemble.py ../../index.html` 每次都会先自动重新子集化，改文案或数据后不用单独跑

需要 `pip install fonttools brotli`。
