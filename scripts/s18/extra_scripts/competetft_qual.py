"""Parse Riot's official Crown qualification page (competetft.com, Next.js RSC payload).

Usage: python3 -I competetft_qual.py <qual.html>  -> prints sections + participants, writes JSON next to the html
"""
import json, re, sys, os

path = sys.argv[1]
t = open(path, encoding="utf-8").read()
chunks = re.findall(r'self\.__next_f\.push\(\[1,("(?:[^"\\]|\\.)*")\]\)', t)
payload = "".join(json.loads(c) for c in chunks)
# walk the payload in order, tracking the latest heading seen
tok = re.compile(r'"heading":"([^"]*)"(?:,"subHeading":"([^"]*)")?|\{"__typename":"CompeteTournamentParticipant".*?"displayName":"[^"]*"\}\}')
out, heads = [], []
for m in tok.finditer(payload):
    if m.group(1) is not None:
        heads.append(m.group(1))
        continue
    o = json.loads(m.group(0))
    out.append(dict(section=" / ".join(heads[-2:]), position=o.get("position"), qualifierType=o.get("qualifierType"),
                    qualifierEsportsId=o.get("qualifierEsportsId"), shard=o["player"].get("shard"),
                    displayName=o["player"].get("displayName"), trDisplayName=o["player"].get("trDisplayName"),
                    tagLine=o["player"].get("tagLine")))
json.dump(out, open(os.path.splitext(path)[0] + "_parsed.json", "w"), ensure_ascii=False, indent=1)
for x in out:
    print(x["position"], "|", x["section"], "|", x["qualifierType"], x["qualifierEsportsId"], "|", x["shard"], "|", x["displayName"], "|", x["trDisplayName"])
print(len(out), "participants;", "headings seen:", heads)
