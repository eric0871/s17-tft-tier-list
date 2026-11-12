# 重新生成 S18 数据

1. 下载 GanglyStats 数据：`curl -o core.js https://ganglystats.com/data/core.js`（放在本目录，别提交）
2. `python data.py core.js players.json` —— 解码 GanglyStats 的打包数据，算出 40 人的赛季/生涯/最近 20 局/世界赛履历
3. `python final.py` —— 加上手工字段（中国选手中文 ID、CN 晋级方式、战队全称），输出 site_players.json
4. `python assemble.py ../../index.html` —— 把数据塞进 template.html 生成 index.html

改页面样式或功能：改 template.html，再跑第 4 步。不要直接改 index.html（会被覆盖）。
名单在 data.py 的 R 列表里（GanglyStats 的选手 key、显示名、战队缩写、赛区、国旗代码）。
