"""按页面实际用到的字，把得意黑（Smiley Sans）子集化成 fonts/smiley-sub.woff2。

可重复跑：assemble.py 每次生成 index.html 前都会自动调用。
单独跑：python3 subset_fonts.py

扫描范围：template.html（静态文案 + JS 里的中文）+ site_players.json（中文 ID、晋级方式、战队名、赛事名）
再加一小段预留字（以后面板可能新加的数据标签），避免加一个小字段就漏字。
源字体：font-src/SmileySans-Oblique.woff2（OFL 1.1，来自 npm @fontpkg/smiley-sans 2.0.4）
"""
import os
import sys

from fontTools import subset
from fontTools.ttLib import TTFont

H = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(H, "..", ".."))
SRC = os.path.join(H, "font-src", "SmileySans-Oblique.woff2")
OUT = os.path.join(ROOT, "fonts", "smiley-sub.woff2")

# 预留：以后面板可能新增的小数据（奖金、生涯、排名等）常用字
RESERVE = "累计职业生涯总奖金美元万千百亿约届次场局名第冠亚季军前四吃鸡垫底率均平排行最佳高低新旧首登上赛季世界选手评级档位池全部导出图片重置确认存储相册分享保存下载取消关闭返回退回已清空数据来源更新于快捷键放入对应一二三四五六七八九十零个人数"


def collect_chars():
    chars = set(RESERVE)
    for name in ("template.html", "site_players.json"):
        p = os.path.join(H, name)
        if os.path.exists(p):
            chars |= set(open(p, encoding="utf-8").read())
    # 只要非 ASCII 的字符（拉丁字母和数字由 Tektur 负责）
    return sorted(c for c in chars if ord(c) > 0x7F)


def main():
    chars = collect_chars()
    font = TTFont(SRC)
    cmap = font.getBestCmap()
    have = [c for c in chars if ord(c) in cmap]
    font.close()
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["*"]
    opts.name_IDs = ["*"]  # 保留版权和授权信息
    opts.notdef_outline = True
    sub = subset.Subsetter(options=opts)
    f = TTFont(SRC)
    sub.populate(unicodes=[ord(c) for c in have])
    sub.subset(f)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    f.flavor = "woff2"
    f.save(OUT)
    print(f"smiley-sub.woff2: {len(have)} 字 / {os.path.getsize(OUT)//1024} KB"
          f"（{len(chars)-len(have)} 个字符字体里没有，由 Tektur / 系统字体兜底）")


if __name__ == "__main__":
    main()
