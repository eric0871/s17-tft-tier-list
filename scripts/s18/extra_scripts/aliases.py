"""Name aliases for matching the 40 players across GanglyStats / Liquipedia / Riot pages (lower-case, no spaces)."""
import re
EXTRA = {  # names seen on Liquipedia pages that differ from GanglyStats names
    "wasianiverson": ["wasian"], "bopster": ["bopster"], "ego": ["egoillusions", "ego"], "Yakumo": ["yatora", "yakumo", "yakumomurai"],
    "Cynarr": ["cynar"], "AQ1H": ["alphaqi"], "Milo": ["miloo"], "WithoutYou": ["cantwithoutyou"], "Baizhi": ["pale", "baizhi"],
    "CSFX": ["cangshan"], "Hanxing": ["hanxing"], "Iron_Bog": ["ironbog"], "L3SCoco": ["l3scoco", "l3s_coco"], "ZyK0o": ["zyk0o"],
    "JosueDeleted": ["deleted", "josuedeleted"], "iCeEmperoz": ["iceemperoz"], "diaomei": ["diaomei"],
}
def aliases_for(site_id, gp):
    s = {site_id.lower().replace("_", "")}
    for x in [gp.get("id"), gp.get("name"), gp.get("displayname")] + list(gp.get("names_seen") or []):
        if x:
            x = re.sub(r"#.*$", "", x)
            s.add(x.lower().replace(" ", ""))
            s.add(re.sub(r"^[A-Z0-9]{2,6}[ .]", "", x).lower().replace(" ", ""))  # drop team tag
    s.update(EXTRA.get(site_id, []))
    return s
