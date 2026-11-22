"""Warehouse Ready demo data: Production Harvest and PackOut.
Worked back from ERP sales so packed vs sold shows a 3 to 8% weekly gap (waste / unsold).
Gift and mixed items are assembled from bought-in and surplus stems, so they have no pack-out rows.
Usage: python production.py [data folder]   (run after dims.py and sales.py)
"""
import csv, os, sys, random
from collections import defaultdict
from datetime import date, timedelta, datetime

random.seed(2025)
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "01 The Decision", "data")
START, END = date(2023, 4, 1), date(2026, 3, 31)

def read(p):
    with open(os.path.join(OUT, p), encoding="utf-8") as f:
        return list(csv.DictReader(f))

def pnz(s):
    return datetime.strptime(s, "%d/%m/%Y").date()

varieties = read("Production/Varieties.csv")
greenhouses = read("Production/Greenhouses.csv")
staff = read("Production/Staff.csv")
items = {i["ItemCode"]: i for i in read("ERP/Items.csv")}
headers = {h["OrderNumber"]: h for h in read("ERP/SalesOrderHeader.csv")}
lines = read("ERP/SalesOrderLines.csv")

# item -> variety by cultivar name in the description (the generator knows; the model will need ItemVarietyMap)
vname = {v["VarietyCode"]: v["VarietyName"].strip().lower() for v in varieties}
vcrop = {v["VarietyCode"]: v["Crop"] for v in varieties}
item_var = {}
for code, it in items.items():
    d = it["ItemDescription"].strip().lower()
    for vc, n in vname.items():
        if n in d:
            item_var[code] = vc

def pack_day(order_date):
    d = order_date - timedelta(days=1)
    if d.weekday() == 6:  # Sunday -> Saturday
        d -= timedelta(days=1)
    return d

# ---- packed bunches per day / variety / grade / bunch size ----
week_waste = {}
packed = defaultdict(int)
for l in lines:
    h = headers[l["OrderNumber"]]
    if h["OrderStatus"] != "Invoiced" or l["ItemCode"] not in item_var:
        continue
    it = items[l["ItemCode"]]
    pd_ = pack_day(pnz(h["OrderDate"]))
    if pd_ < START:
        continue
    key = (pd_, item_var[l["ItemCode"]], int(it["StemLengthCm"]), int(it["StemsPerBunch"]))
    packed[key] += int(l["QuantityBunches"])

pack_rows = []
stems_needed = defaultdict(int)  # (day, variety) -> stems picked
for (d, vc, g, b), q in sorted(packed.items()):
    wk = d.isocalendar()[:2]
    if wk not in week_waste:
        week_waste[wk] = random.uniform(0.03, 0.08)
    bunches = max(q, round(q * (1 + week_waste[wk] * random.uniform(0.6, 1.4))))
    stems = bunches * b
    rejected = round(stems * random.uniform(0.04, 0.09))
    line = "L1" if vcrop[vc] in ("ROSE", "GERBERA") else "L2"
    pack_rows.append([d.isoformat(), line, vc, f"G{g}", b, bunches, rejected])
    # picked over the pack day and the working day before it (Mon to Sat)
    prev = d - timedelta(days=1)
    if prev.weekday() == 6:
        prev -= timedelta(days=1)
    prev = max(prev, START)
    total = stems + rejected
    first = round(total * random.uniform(0.4, 0.6))
    stems_needed[(prev, vc)] += first
    stems_needed[(d, vc)] += total - first

# ---- harvest: picker x greenhouse x variety x day ----
RATE = {"ROSE": 320, "LILY": 210, "CHRYSANTHEMUM": 260, "GERBERA": 400, "LISIANTHUS": 240}  # stems per hour
def gh_for(vc, d):
    crop = vcrop[vc]
    if crop == "ROSE":
        opts = ["GH01", "GH02"] + (["GH06"] if d >= date(2025, 7, 14) else [])
        return random.choice(opts)
    return {"LILY": "GH03", "CHRYSANTHEMUM": "GH04", "GERBERA": "GH05", "LISIANTHUS": "GH05"}[crop]

pickers = []
for s in staff:
    if s["Role"] != "Picker":
        continue
    pickers.append(dict(id=s["StaffID"], start=date.fromisoformat(s["StartDate"]),
                        end=date.fromisoformat(s["EndDate"]) if s["EndDate"] else END,
                        seasonal=s["EmploymentType"] == "Seasonal", skill=random.uniform(0.8, 1.2)))

def available(d):
    out = []
    for p in pickers:
        if not (p["start"] <= d <= p["end"]):
            continue
        if p["seasonal"] and d.month in (5, 6, 7, 8):  # seasonal pickers off over winter
            continue
        if random.random() < 0.06:  # leave / sick
            continue
        out.append(p)
    return out

by_day = defaultdict(list)
for (d, vc), st in stems_needed.items():
    by_day[d].append((vc, st))

harvest = []
for d in sorted(by_day):
    crew = available(d)
    if not crew:
        continue
    work = defaultdict(int)  # (gh, vc) -> stems
    for vc, st in by_day[d]:
        work[(gh_for(vc, d), vc)] += st
    # assign each picker to one greenhouse for the day, weighted by hours of work there
    gh_hours = defaultdict(float)
    for (gh, vc), st in work.items():
        gh_hours[gh] += st / RATE[vcrop[vc]]
    # pickers per greenhouse in proportion to hours needed (largest remainder), at least one each
    ghs = sorted(gh_hours, key=gh_hours.get, reverse=True)
    total = sum(gh_hours.values())
    n = len(crew)
    share = {g: max(1, int(n * gh_hours[g] / total)) for g in ghs}
    while sum(share.values()) > n:
        g = max((g for g in ghs if share[g] > 1), key=lambda g: share[g] - n * gh_hours[g] / total, default=None)
        if g is None:
            break
        share[g] -= 1
    while sum(share.values()) < n:
        g = max(ghs, key=lambda g: n * gh_hours[g] / total - share[g])
        share[g] += 1
    assign = defaultdict(list)
    random.shuffle(crew)
    i = 0
    for g in ghs:
        assign[g] = crew[i:i + share[g]] or [random.choice(crew)]
        i += share[g]
    for (gh, vc), st in work.items():
        team = assign.get(gh) or [random.choice(crew)]
        wts = [p["skill"] * random.uniform(0.7, 1.3) for p in team]
        tot = sum(wts)
        for p, wt in zip(team, wts):
            s = round(st * wt / tot)
            if s <= 0:
                continue
            hrs = s / (RATE[vcrop[vc]] * p["skill"] * random.uniform(0.9, 1.1))
            harvest.append([d.isoformat(), p["id"], gh, vc, s, f"{max(hrs, 0.25):.2f}"])

# rebalance: move whole rows off anyone over 10 harvest hours to the least-loaded picker that day
by_d = defaultdict(list)
for r in harvest:
    by_d[r[0]].append(r)
for d_, rows in by_d.items():
    for _ in range(50):
        load = defaultdict(float)
        for r in rows:
            load[r[1]] += float(r[5])
        hi = max(load, key=load.get)
        lo = min(load, key=load.get)
        if load[hi] <= 10 or hi == lo:
            break
        r = max((r for r in rows if r[1] == hi), key=lambda r: float(r[5]))
        if float(r[5]) > 6:  # split a large row in two
            half = r[4] // 2
            hrs = float(r[5])
            r[4] -= half
            r[5] = f"{hrs * r[4] / (r[4] + half):.2f}"
            rows.append([r[0], lo, r[2], r[3], half, f"{hrs * half / (r[4] + half):.2f}"])
        else:
            r[1] = lo
harvest = [r for rows in by_d.values() for r in rows]
# merge duplicate keys created by the moves
merged = {}
for r in harvest:
    k = tuple(r[:4])
    if k in merged:
        merged[k][4] += r[4]
        merged[k][5] = f"{float(merged[k][5]) + float(r[5]):.2f}"
    else:
        merged[k] = list(r)
harvest = list(merged.values())

def w(path, header, rows):
    with open(os.path.join(OUT, path), "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(header)
        wr.writerows(rows)

w("Production/PackOut.csv", ["PackDate", "PackLine", "VarietyCode", "GradeCode", "BunchSize", "BunchesPacked",
                             "StemsRejected"], pack_rows)
w("Production/Harvest.csv", ["HarvestDate", "StaffID", "GreenhouseCode", "VarietyCode", "StemsPicked",
                             "HarvestHours"], sorted(harvest))
print("packout", len(pack_rows), "harvest", len(harvest))
