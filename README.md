# S18 世界赛选手评级 (TFT Enchanted Wilds Tactician's Crown Tier List)

可拖拽的选手评级：把 40 名 TFT Set 18「Enchanted Wilds」Tactician's Crown（2026-11-13 ~ 15）世界赛选手放进 S / A / B / C / 金铲铲 五档。

**在线版**：https://eric0871.github.io/s17-tft-tier-list/

## 功能
- 点击或拖动选手，右侧显示他的数据：晋级方式、S18 本赛季平均名次 / 前四率 / 吃鸡率（含 40 人中的排名）、最近 20 局名次、历届世界赛名次、本赛季最佳战绩、生涯数据
- 放进档位时有落位动效（S 档和金铲铲档更大）
- 「导出图片」把评级板导出成 PNG
- 选中选手后按 `S` `A` `B` `C` `G`（或 `1`–`5`）直接放进对应档位，`0` 退回选手池
- 选手池可按赛区筛选；评级存在浏览器本地，刷新不丢
- 针对 iPad 横屏（Safari / 添加到主屏幕全屏）设计：触控拖动、点选手再点档位两种放法，一屏装下不滚动；电脑 1920×1080 也能用
- 设计理念、配色、字体和交互规则见 [DESIGN.md](DESIGN.md)（「暗场闪卡」）

## 数据
- 选手名单：Riot 官方 Enchanted Wilds Tactician's Crown Primer
- 比赛数据：[GanglyStats](https://ganglystats.com/)（2026-11-11 更新），世界赛履历覆盖 Set 3 起所有 Championship / Tactician's Crown
- 头像：官方 Pick'em 网站（pickem.competetft.com）的统一定妆照，抠掉了赛区色底：`photos/s18/<id>.png`（透明底）/ `.jpg`（深灰底）。`python scripts/fetch_photos_s18.py` 可重新生成。官方 Pick'em 上 Maris 那张其实是 Milo 的照片，Maris 改用 Liquipedia 定妆照
- 国旗：`flags/`（来自 flagcdn.com）

## 旧版
- S17 Space Gods 版本：[archive/s17.html](archive/s17.html)
