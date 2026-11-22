"""Warehouse Ready demo data: ERP sales orders (header + lines).
Reads the dimension CSVs written by dims.py. Seeded, so re-running gives the same output.
Usage: python sales.py [data folder]
"""
import csv, os, sys, random
from datetime import date, timedelta, datetime

random.seed(2024)
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "01 The Decision", "data")
START, END = date(2023, 4, 1), date(2026, 3, 31)

def read(p):
    with open(os.path.join(OUT, p), encoding="utf-8") as f:
        return list(csv.DictReader(f))

def pnz(s):
    return datetime.strptime(s, "%d/%m/%Y").date()

def nz(d):
    return d.strftime("%d/%m/%Y")

customers = read("ERP/Customers.csv")
items = read("ERP/Items.csv")

def mothers_day(y):  # second Sunday of May (NZ)
    d = date(y, 5, 1)
    d += timedelta(days=(6 - d.weekday()) % 7)
    return d + timedelta(days=7)

def crop_of(it):
    d = it["ItemDescription"].strip().lower()
    for k, c in [("rose", "ROSE"), ("lily", "LILY"), ("chrys", "CHRYS"), ("gerbera", "GERBERA"),
                 ("lisianthus", "LISIANTHUS")]:
        if d.startswith(k):
            return c
    return "GIFT"

for it in items:
    it["crop"] = crop_of(it)
    it["created"] = pnz(it["CreatedDate"])
    it["len"] = int(it["StemLengthCm"]) if it["StemLengthCm"] else 0
    it["price"] = float(it["ListPriceNZD"])
    it["red"] = " red" in it["ItemDescription"].lower() or "crimson" in it["ItemDescription"].lower() \
        or "velvet" in it["ItemDescription"].lower()

CROP_W = {"ROSE": 45, "CHRYS": 20, "LILY": 15, "GERBERA": 12, "LISIANTHUS": 8}
# channel: orders per week, lines per order (min,max), qty per line (min,max), discount, length preference
CH = {
    "Florist":     (1.5, (1, 4), (2, 8), 0.00, "long"),
    "Wholesaler":  (2.0, (2, 6), (10, 40), 0.12, "any"),
    "Supermarket": (3.0, (2, 5), (20, 60), 0.18, "short"),
    "Export":      (1.0, (3, 7), (30, 120), 0.08, "long"),
    "Online":      (2.0, (1, 3), (1, 5), 0.00, "any"),
}

def season_factor(d):
    f = 1.0
    if d.month in (6, 7, 8):
        f *= 0.85
    if d.month == 12 and d.day <= 23:
        f *= 1.4
    if date(d.year, 2, 1) <= d <= date(d.year, 2, 14):
        f *= 1.8
    md = mothers_day(d.year)
    if md - timedelta(days=9) <= d <= md - timedelta(days=1):
        f *= 1.6
    years = (d - START).days / 365.0
    return f * (1 + 0.05 * years)  # ~5% growth per year

def pick_item(d, pref):
    md = mothers_day(d.year)
    val = date(d.year, 2, 5) <= d <= date(d.year, 2, 13)
    mdw = md - timedelta(days=7) <= d <= md - timedelta(days=1)
    avail = [i for i in items if i["created"] <= d and i["Active"] == "Y"]
    weights = []
    for i in avail:
        if i["crop"] == "GIFT":
            desc = i["ItemDescription"].lower()
            if "valentine" in desc:
                w = 25 if val else 0
            elif "mothers" in desc:
                w = 25 if mdw else 0
            else:
                w = 1.5
        else:
            n_in_crop = sum(1 for j in avail if j["crop"] == i["crop"])
            w = CROP_W[i["crop"]] / n_in_crop * 10
            if pref == "long":
                w *= 1 + i["len"] / 60
            elif pref == "short":
                w *= 2.0 if i["len"] and i["len"] <= 50 else 0.6
            if val and i["crop"] == "ROSE" and i["red"]:
                w *= 6
        weights.append(w)
    return random.choices(avail, weights)[0]

# per-customer active window
cust = []
for c in customers:
    start = max(pnz(c["CreatedDate"]), START)
    end = END
    if c["Active"] == "N":
        end = START + timedelta(days=random.randint(150, 900))
    cust.append((c, start, end))

headers, lines = [], []
so = 400100
d = START
while d <= END:
    if d.weekday() < 5:
        for c, cs, ce in cust:
            if not (cs <= d <= ce):
                continue
            per_week, lpo, qty, disc, pref = CH[c["Channel"]]
            p = per_week / 5 * season_factor(d)
            if c["Channel"] == "Export":
                p = per_week / 5 if d.weekday() == 1 else 0  # export ships Tuesdays
                p *= min(season_factor(d), 1.5)
            if random.random() >= p:
                continue
            so += random.randint(1, 3)
            order = f"SO{so}"
            status = "Cancelled" if random.random() < 0.012 else "Invoiced"
            lead = 1 if c["Channel"] != "Export" else 3
            po = "" if random.random() < 0.4 else f"PO{random.randint(1000, 99999)}"
            headers.append([order, nz(d), nz(d + timedelta(days=lead)), c["CustomerCode"], status, po])
            n_lines = random.randint(*lpo)
            used = set()
            ln = 0
            for _ in range(n_lines):
                it = pick_item(d, pref)
                if it["ItemCode"] in used:
                    continue
                used.add(it["ItemCode"])
                ln += 1
                q = random.randint(*qty)
                if it["crop"] == "GIFT":
                    q = max(1, q // 3)
                price = it["price"]
                if random.random() < 0.05:  # occasional price override
                    price = round(price * random.uniform(0.85, 1.05), 2)
                amount = round(q * price * (1 - disc), 2)
                lines.append([order, ln, it["ItemCode"], q, f"{price:.2f}", f"{disc * 100:.0f}", f"{amount:.2f}"])
    d += timedelta(days=1)

def w(path, header, rows):
    with open(os.path.join(OUT, path), "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(header)
        wr.writerows(rows)

w("ERP/SalesOrderHeader.csv", ["OrderNumber", "OrderDate", "DeliveryDate", "CustomerCode", "OrderStatus",
                               "CustomerPO"], headers)
w("ERP/SalesOrderLines.csv", ["OrderNumber", "LineNumber", "ItemCode", "QuantityBunches", "UnitPriceNZD",
                              "DiscountPct", "LineAmountNZD"], lines)
print("orders", len(headers), "lines", len(lines))
