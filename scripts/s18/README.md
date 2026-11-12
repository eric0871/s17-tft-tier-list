# 重新生成 S18 数据

1. 下载 GanglyStats 数据：`curl -o core.js https://ganglystats.com/data/core.js`（放在本目录，别提交）
2. `python data.py core.js players.json` —— 解码 GanglyStats 的打包数据，算出 40 人的赛季/生涯/最近 20 局/世界赛履历
3. `python final.py` —— 加上手工字段（中国选手中文 ID、CN 晋级方式、战队全称、已核实的数据更正）和 `extra.json` 里的补充数据（Liquipedia 累计奖金、GanglyStats 世界赛场均和最常同桌对手），输出 site_players.json
   - `extra.json` 由 `extra_scripts/` 生成（Liquipedia 只能走 API，限速很严，首次约 35 分钟；说明见各脚本开头）
4. `python assemble.py ../../index.html` —— 先按页面用到的字把中文字体子集化（需要 `pip install fonttools`），再把数据塞进 template.html 生成 index.html

改页面样式或功能：改 template.html，再跑第 4 步。不要直接改 index.html（会被覆盖）。
名单在 data.py 的 R 列表里（GanglyStats 的选手 key、显示名、战队缩写、赛区、国旗代码）。
