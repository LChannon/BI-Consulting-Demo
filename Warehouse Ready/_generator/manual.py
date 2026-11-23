"""Warehouse Ready demo data: user-maintained Excel tables (data/Manual).
ProductMapping.xlsx  ERP item -> packhouse variety, VarietyDefault flag (one item per variety), Range.
                     Gift/mixed items have a Range but no variety; one Coral Dawn item is missing entirely.
Budget.xlsx          one sheet per FY, Range x Channel x Measure rows, months across (needs unpivoting).
Usage: python manual.py [data folder]   (run after dims.py and sales.py)
"""
import csv, os, sys, random
from collections import defaultdict
from datetime import date, datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

random.seed(2026)
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "01 The Decision", "data")
os.makedirs(os.path.join(OUT, "Manual"), exist_ok=True)

def read(p):
    with open(os.path.join(OUT, p), encoding="utf-8") as f:
        return list(csv.DictReader(f))

items = read("ERP/Items.csv")
varieties = read("Production/Varieties.csv")
customers = {c["CustomerCode"]: c for c in read("ERP/Customers.csv")}
headers = {h["OrderNumber"]: h for h in read("ERP/SalesOrderHeader.csv")}
lines = read("ERP/SalesOrderLines.csv")
HDR = Font(bold=True, color="FFFFFF")
FILL = PatternFill("solid", fgColor="1F4E79")

def sheet(ws, header, rows, widths):
    ws.append(header)
    for c in ws[1]:
        c.font, c.fill = HDR, FILL
    for r in rows:
        ws.append(r)
    for col, wd in zip("ABCDEFGHIJKLMNOP", widths):
        ws.column_dimensions[col].width = wd
    ws.freeze_panes = "A2"

# ---------------- ProductMapping ----------------
# One hand-kept workbook: ERP item -> packhouse variety, a default item per variety (so variety-level
# facts such as Harvest can join the item-level product dimension), and the user-defined Range.
PREMIUM_MIN = {"rose": 60, "lily": 80, "chrys": 80, "gerbera": 55, "lisianthus": 70}
range_of = {}
for it in items:
    d = it["ItemDescription"].strip().lower()
    if it["ProductGroup"] in ("GIFT", "MIXED"):
        range_of[it["ItemCode"]] = "Seasonal"
    else:
        range_of[it["ItemCode"]] = "Premium" if int(it["StemLengthCm"]) >= PREMIUM_MIN[d.split()[0]] else "Everyday"

sold = defaultdict(int)  # bunches sold per item, to pick each variety's default (popular, long-running) item
for l in lines:
    sold[l["ItemCode"]] += int(l["QuantityBunches"])

vname = {v["VarietyCode"]: v["VarietyName"].strip().lower() for v in varieties}
users = ["j.morgan", "k.reid", "a.harris"]
map_rows, forgot, item_var = [], None, {}
for it in items:
    d = it["ItemDescription"].strip().lower()
    vc = next((c for c, n in vname.items() if n in d), None)
    if vc is None:
        continue  # gift and mixed items added below, with no variety
    created = datetime.strptime(it["CreatedDate"], "%d/%m/%Y").date()
    if "coral dawn" in d and forgot is None and "60cm" in d:
        forgot = it["ItemCode"]  # added to the ERP but never added to the mapping
        continue
    code = vc
    if random.random() < 0.06:
        code = vc.lower()
    elif random.random() < 0.05:
        code = vc + " "
    mapped = created if created > date(2020, 1, 1) else date(2021, 2, 15)
    item_var[it["ItemCode"]] = vc
    map_rows.append([it["ItemCode"], it["ItemDescription"].strip(), code, "", range_of[it["ItemCode"]],
                     random.choice(users), mapped])
default = {}
for ic, vc in item_var.items():
    if vc not in default or sold[ic] > sold[default[vc]]:
        default[vc] = ic
for r in map_rows:
    if default[item_var[r[0]]] == r[0]:
        r[3] = "Y"
for i, it in enumerate(i for i in items if i["ProductGroup"] in ("GIFT", "MIXED")):
    map_rows.append([it["ItemCode"], it["ItemDescription"].strip(), "", "", "Seasonal", users[i % 3],
                     date(2021, 2, 15)])
wb = Workbook()
ws = wb.active
ws.title = "Mapping"
sheet(ws, ["ItemCode", "ItemDescription", "VarietyCode", "VarietyDefault", "Range", "MappedBy", "MappedDate"],
      map_rows, [12, 36, 12, 14, 12, 12, 12])
for r in ws.iter_rows(min_row=2, min_col=7, max_col=7):
    r[0].number_format = "dd/mm/yyyy"
ws2 = wb.create_sheet("Range List")
sheet(ws2, ["Range", "SortOrder", "Description"],
      [["Premium", 1, "Long stem grades for florists and export"],
       ["Everyday", 2, "Shorter grades for supermarkets and volume buyers"],
       ["Seasonal", 3, "Gift and mixed items for peak occasions"]], [12, 10, 50])
wb.save(os.path.join(OUT, "Manual/ProductMapping.xlsx"))
pr_rows = map_rows

# ---------------- Budget ----------------
# Built from actuals with noise, as if set before each year: bunches and revenue by Range x Channel x month.
act = defaultdict(lambda: [0, 0.0])
for l in lines:
    h = headers[l["OrderNumber"]]
    if h["OrderStatus"] != "Invoiced":
        continue
    d = datetime.strptime(h["OrderDate"], "%d/%m/%Y").date()
    ch = customers[h["CustomerCode"]]["Channel"]
    a = act[(d.year, d.month, range_of[l["ItemCode"]], ch)]
    a[0] += int(l["QuantityBunches"])
    a[1] += float(l["LineAmountNZD"])

FY = {"FY24": 2023, "FY25": 2024, "FY26": 2025}
months = [(4, 0), (5, 0), (6, 0), (7, 0), (8, 0), (9, 0), (10, 0), (11, 0), (12, 0), (1, 1), (2, 1), (3, 1)]
bias = {"FY24": 1.02, "FY25": 1.06, "FY26": 0.97}  # FY25 optimistic, FY26 cautious
wb = Workbook()
wb.remove(wb.active)
for fy, y0 in FY.items():
    ws = wb.create_sheet(fy)
    mnames = [date(y0 + off, m, 1).strftime("%b-%y") for m, off in months]
    rows = []
    for rng in ["Premium", "Everyday", "Seasonal"]:
        for ch in ["Florist", "Wholesaler", "Supermarket", "Export", "Online"]:
            bunches, revenue = [], []
            for m, off in months:
                a = act.get((y0 + off, m, rng, ch), [0, 0.0])
                f = bias[fy] * random.uniform(0.9, 1.1)
                bunches.append(int(round(a[0] * f, -1)))
                revenue.append(int(round(a[1] * f * random.uniform(0.98, 1.02), -2)))
            if sum(bunches) == 0:
                continue
            rows.append([rng, ch, "Bunches"] + bunches)
            rows.append([rng, ch, "Revenue NZD"] + revenue)
    ws.append([f"NVX Sales Budget {fy} (Apr {y0} to Mar {y0 + 1})"])
    ws["A1"].font = Font(bold=True, size=13)
    ws.append([f"Approved {date(y0, 3, 20).strftime('%d %b %Y')}"])
    ws.append([])
    hdr_row = 4
    ws.append(["Range", "Channel", "Measure"] + mnames + ["Total"])
    for c in ws[hdr_row]:
        c.font, c.fill = HDR, FILL
    for i, r in enumerate(rows):
        rn = hdr_row + 1 + i
        ws.append(r + [sum(r[3:])])  # value, not formula: Power Query reads cached values only
        for c in ws[rn][3:]:
            c.number_format = "#,##0"
    ws.column_dimensions["A"].width = 12
    ws.column_dimensions["B"].width = 13
    ws.column_dimensions["C"].width = 13
    ws.freeze_panes = "D5"
wb.save(os.path.join(OUT, "Manual/Budget.xlsx"))
print("map rows", len(map_rows), "forgotten", forgot, "range rows", len(pr_rows))
