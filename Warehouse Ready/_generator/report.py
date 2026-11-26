"""Warehouse Ready part 01: simulated manual weekly Excel report (the 'before').
Paste tabs hold the raw month-to-date extracts; helper columns VLOOKUP a hand-kept Lookups tab;
the Report tab uses SUMIFS driven by a typed week-ending date. Budgets are typed in (grey cells).
The Lookups tab is a stale copy: the Coral Dawn rose and its items are missing, so the check cells show a gap.
Usage: python report.py [data folder] [output xlsx]
"""
import csv, os, sys
from collections import defaultdict
from datetime import date, datetime, timedelta
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "01 The Decision", "data")
OUTF = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "01 The Decision",
                                                         "NVX Weekly Report w-e 16-02-2025.xlsx")
WE = date(2025, 2, 16)                       # week ending (Sunday)
MS = date(WE.year, WE.month, 1)               # month start = first date in the paste extracts
CROPS = ["Rose", "Lily", "Chrysanthemum", "Gerbera", "Lisianthus"]
RANGES = ["Premium", "Everyday", "Seasonal"]

def read(p):
    with open(os.path.join(DATA, p), encoding="utf-8") as f:
        return list(csv.DictReader(f))

def pnz(s):
    return datetime.strptime(s, "%d/%m/%Y").date()

items = {i["ItemCode"]: i for i in read("ERP/Items.csv")}
cust = {c["CustomerCode"]: c for c in read("ERP/Customers.csv")}
hdr = {h["OrderNumber"]: h for h in read("ERP/SalesOrderHeader.csv")}
varieties = read("Production/Varieties.csv")

# ---------- styles ----------
B = Font(bold=True)
TITLE = Font(bold=True, size=14)
SEC = Font(bold=True, size=11, underline="single")
GREY = PatternFill("solid", fgColor="D9D9D9")
HEAD = PatternFill("solid", fgColor="F2F2F2")
thin = Side(style="thin", color="808080")
BOX = Border(top=thin, bottom=thin, left=thin, right=thin)
TOP = Border(top=thin)
CEN = Alignment(horizontal="center")

wb = Workbook()
rep = wb.active
rep.title = "Report"

# ---------- ERP Paste ----------
ep = wb.create_sheet("ERP Paste")
ecols = ["Order Date", "Order No", "Status", "Customer", "Customer Name", "Item", "Description", "Qty", "Amount"]
ep.append(ecols + ["Range", "Crop"])
r = 2
for l in read("ERP/SalesOrderLines.csv"):
    h = hdr[l["OrderNumber"]]
    d = pnz(h["OrderDate"])
    if not (MS <= d <= WE):
        continue
    it = items[l["ItemCode"]]
    ep.append([d, l["OrderNumber"], h["OrderStatus"].upper(), h["CustomerCode"], cust[h["CustomerCode"]]["CustomerName"],
               l["ItemCode"], it["ItemDescription"], int(l["QuantityBunches"]), float(l["LineAmountNZD"]),
               f"=VLOOKUP(F{r},Lookups!$A:$C,2,FALSE)", f"=VLOOKUP(F{r},Lookups!$A:$C,3,FALSE)"])
    ep.cell(r, 1).number_format = "dd/mm/yyyy"
    r += 1
ERP_N = r - 1
for c in ep[1]:
    c.font, c.fill = B, HEAD
for col, w in zip("ABCDEFGHIJK", [11, 10, 10, 9, 28, 9, 32, 6, 10, 10, 13]):
    ep.column_dimensions[col].width = w

# ---------- Harvest Paste / PackOut Paste ----------
def paste(name, src, datecol, cols, lookup_col):
    ws = wb.create_sheet(name)
    ws.append(cols + ["Crop"])
    n = 2
    for row in read(src):
        d = date.fromisoformat(row[datecol])
        if not (MS <= d <= WE):
            continue
        vals = [d] + [row[k] for k in list(row)[1:]]
        vals = [int(v) if isinstance(v, str) and v.isdigit() else v for v in vals]
        vals = [float(v) if isinstance(v, str) and v.replace(".", "", 1).isdigit() else v for v in vals]
        ws.append(vals + [f"=VLOOKUP({lookup_col}{n},Lookups!$E:$F,2,FALSE)"])
        ws.cell(n, 1).number_format = "dd/mm/yyyy"
        n += 1
    for c in ws[1]:
        c.font, c.fill = B, HEAD
    for i in range(1, len(cols) + 2):
        ws.column_dimensions[L(i)].width = 13
    return n - 1

HV_N = paste("Harvest Paste", "Production/Harvest.csv", "HarvestDate",
             ["Date", "Staff", "House", "Variety", "Stems", "Hours"], "D")
PK_N = paste("PackOut Paste", "Production/PackOut.csv", "PackDate",
             ["Date", "Line", "Variety", "Grade", "Bunch Size", "Bunches", "Rejects"], "C")

# ---------- Lookups (hand-kept, out of date: no Coral Dawn) ----------
lk = wb.create_sheet("Lookups")
lk.append(["Item", "Range", "Crop", None, "Variety", "Crop"])
crop_word = {"rose": "Rose", "lily": "Lily", "chrys": "Chrysanthemum", "gerbera": "Gerbera",
             "lisianthus": "Lisianthus"}
item_rows = []
for code, it in items.items():
    d = it["ItemDescription"].strip().lower()
    if "coral dawn" in d:
        continue  # never added
    first = d.split()[0]
    crop = crop_word.get(first, "Gift")
    if it["ProductGroup"] in ("GIFT", "MIXED"):
        rng = "Seasonal"
    else:
        prem = {"rose": 60, "lily": 80, "chrys": 80, "gerbera": 55, "lisianthus": 70}[first]
        rng = "Premium" if int(it["StemLengthCm"]) >= prem else "Everyday"
    item_rows.append([code, rng, crop])
var_rows = [[v["VarietyCode"], v["Crop"].title().replace("Chrysanthemum", "Chrysanthemum")]
            for v in varieties if "coral" not in v["VarietyName"].lower()]
for i in range(max(len(item_rows), len(var_rows))):
    a = item_rows[i] if i < len(item_rows) else [None] * 3
    b = var_rows[i] if i < len(var_rows) else [None] * 2
    lk.append(a + [None] + b)
for c in lk[1]:
    c.font = B
for col, w in zip("ABCDEF", [10, 11, 14, 3, 9, 14]):
    lk.column_dimensions[col].width = w

# ---------- typed budgets (from the monthly budget, pro-rata, rounded by hand) ----------
bud = load_workbook(os.path.join(DATA, "Manual/Budget.xlsx"), data_only=True)["FY25"]
mcol = None
for c in bud[4]:
    if c.value == WE.strftime("%b-%y"):
        mcol = c.column
month_b = defaultdict(float)
for row in bud.iter_rows(min_row=5, values_only=True):
    if row[0]:
        month_b[(row[0], row[1])] += row[mcol - 1] or 0
days_in_month = 28
def typed(v, days, rnd):
    return int(round(v * days / days_in_month, rnd))

# ---------- Report ----------
ER, HR, PR = f"'ERP Paste'!", f"'Harvest Paste'!", f"'PackOut Paste'!"
rep.column_dimensions["A"].width = 18
for i in range(2, 22):
    rep.column_dimensions[L(i)].width = 12
rep["A1"] = "NVX Flowers"; rep["A1"].font = TITLE
rep["A2"] = "Weekly Production and Sales Report"; rep["A2"].font = B
rep["A4"] = "Week Ending"; rep["A4"].font = B
rep["B4"] = WE; rep["B4"].number_format = "dd/mm/yyyy"; rep["B4"].fill = GREY; rep["B4"].border = BOX
rep["C4"] = "Week Start"; rep["D4"] = "=B4-6"; rep["D4"].number_format = "dd/mm/yyyy"
rep["E4"] = "Month Start"; rep["F4"] = "=DATE(YEAR(B4),MONTH(B4),1)"; rep["F4"].number_format = "dd/mm/yyyy"
rep["H4"] = "Prepared"; rep["I4"] = date(2025, 2, 17); rep["I4"].number_format = "dd/mm/yyyy"; rep["I4"].fill = GREY
rep["J4"] = "by"; rep["K4"] = "k.reid"; rep["K4"].fill = GREY

def wtd(rng_):  # SUMIFS criteria pair for week to date on a date column
    return f'{rng_},">="&$D$4,{rng_},"<="&$B$4'
def mtd(rng_):
    return f'{rng_},">="&$F$4,{rng_},"<="&$B$4'

def headrow(row, labels, start_col):
    for i, t in enumerate(labels):
        c = rep.cell(row, start_col + i, t)
        c.font, c.fill, c.border = B, HEAD, BOX
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    rep.row_dimensions[row].height = 30

def num(c, fmt="#,##0"):
    c.number_format = fmt
    c.border = BOX

# SALES
r0 = 6
rep.cell(r0, 1, "SALES").font = SEC
rep.cell(r0, 2, "Week to Date").font = B
rep.cell(r0, 11, "Month to Date").font = B
sub = ["Bunches", "Bunch Bgt", "% Bgt", "Sales $", "Sales Bgt", "% Bgt", "$/Bunch", "Bgt $/Bunch"]
headrow(r0 + 1, sub, 2)
headrow(r0 + 1, sub, 11)
q, a, rg, d_, st = f"{ER}$H$2:$H${ERP_N}", f"{ER}$I$2:$I${ERP_N}", f"{ER}$J$2:$J${ERP_N}", \
    f"{ER}$A$2:$A${ERP_N}", f"{ER}$C$2:$C${ERP_N}"
for i, R in enumerate(RANGES):
    row = r0 + 2 + i
    rep.cell(row, 1, R).font = B
    for base, crit, days in ((2, wtd, 7), (11, mtd, WE.day)):
        cl = lambda k: L(base + k)
        rep.cell(row, base, f'=SUMIFS({q},{rg},$A{row},{st},"INVOICED",{crit(d_)})')
        rep.cell(row, base + 1, typed(month_b[(R, "Bunches")], days, -1)).fill = GREY
        rep.cell(row, base + 2, f"={cl(0)}{row}/{cl(1)}{row}")
        rep.cell(row, base + 3, f'=SUMIFS({a},{rg},$A{row},{st},"INVOICED",{crit(d_)})')
        rep.cell(row, base + 4, typed(month_b[(R, "Revenue NZD")], days, -2)).fill = GREY
        rep.cell(row, base + 5, f"={cl(3)}{row}/{cl(4)}{row}")
        rep.cell(row, base + 6, f"={cl(3)}{row}/{cl(0)}{row}")
        rep.cell(row, base + 7, f"={cl(4)}{row}/{cl(1)}{row}")
        for k, fmt in enumerate(["#,##0", "#,##0", "0%", "$#,##0", "$#,##0", "0%", "$0.00", "$0.00"]):
            num(rep.cell(row, base + k), fmt)
tot = r0 + 2 + len(RANGES)
rep.cell(tot, 1, "Total Sales").font = B
for base in (2, 11):
    for k, fmt in enumerate(["#,##0", "#,##0", "0%", "$#,##0", "$#,##0", "0%", "$0.00", "$0.00"]):
        col = L(base + k)
        if k in (0, 1, 3, 4):
            f = f"=SUM({col}{r0 + 2}:{col}{tot - 1})"
        else:
            f = {2: f"={L(base)}{tot}/{L(base + 1)}{tot}", 5: f"={L(base + 3)}{tot}/{L(base + 4)}{tot}",
                 6: f"={L(base + 3)}{tot}/{L(base)}{tot}", 7: f"={L(base + 4)}{tot}/{L(base + 1)}{tot}"}[k]
        c = rep.cell(tot, base + k, f)
        num(c, fmt); c.font = B
# check: everything invoiced in the paste vs what the report picked up
chk = tot + 1
rep.cell(chk, 1, "Check $ (should be 0)").font = Font(italic=True, color="C00000")
rep.cell(chk, 5, f'=SUMIFS({a},{st},"INVOICED",{wtd(d_)})-E{tot}')
rep.cell(chk, 14, f'=SUMIFS({a},{st},"INVOICED")-N{tot}')
for cc in (5, 14):
    rep.cell(chk, cc).number_format = "$#,##0.00;[Red]-$#,##0.00"
    rep.cell(chk, cc).font = Font(italic=True, color="C00000")

# PRODUCTION
p0 = chk + 2
rep.cell(p0, 1, "PRODUCTION").font = SEC
rep.cell(p0, 2, "Week to Date").font = B
rep.cell(p0, 11, "Month to Date").font = B
psub = ["Stems Picked", "Hours", "Stems/Hr", "Bunches Packed", "Rejects", "Reject %"]
headrow(p0 + 1, psub, 2)
headrow(p0 + 1, psub, 11)
hs, hh, hc, hd = (f"{HR}$E$2:$E${HV_N}", f"{HR}$F$2:$F${HV_N}", f"{HR}$G$2:$G${HV_N}", f"{HR}$A$2:$A${HV_N}")
pb, prj, pc, pd_ = (f"{PR}$F$2:$F${PK_N}", f"{PR}$G$2:$G${PK_N}", f"{PR}$H$2:$H${PK_N}", f"{PR}$A$2:$A${PK_N}")
for i, C in enumerate(CROPS):
    row = p0 + 2 + i
    rep.cell(row, 1, C).font = B
    for base, crit in ((2, wtd), (11, mtd)):
        cl = lambda k: L(base + k)
        rep.cell(row, base, f"=SUMIFS({hs},{hc},$A{row},{crit(hd)})")
        rep.cell(row, base + 1, f"=SUMIFS({hh},{hc},$A{row},{crit(hd)})")
        rep.cell(row, base + 2, f"={cl(0)}{row}/{cl(1)}{row}")
        rep.cell(row, base + 3, f"=SUMIFS({pb},{pc},$A{row},{crit(pd_)})")
        rep.cell(row, base + 4, f"=SUMIFS({prj},{pc},$A{row},{crit(pd_)})")
        rep.cell(row, base + 5, f"={cl(4)}{row}/{cl(0)}{row}")
        for k, fmt in enumerate(["#,##0", "#,##0.0", "#,##0", "#,##0", "#,##0", "0.0%"]):
            num(rep.cell(row, base + k), fmt)
ptot = p0 + 2 + len(CROPS)
rep.cell(ptot, 1, "Total Production").font = B
for base in (2, 11):
    for k, fmt in enumerate(["#,##0", "#,##0.0", "#,##0", "#,##0", "#,##0", "0.0%"]):
        col = L(base + k)
        f = {2: f"={L(base)}{ptot}/{L(base + 1)}{ptot}", 5: f"={L(base + 4)}{ptot}/{L(base)}{ptot}"}.get(
            k, f"=SUM({col}{p0 + 2}:{col}{ptot - 1})")
        c = rep.cell(ptot, base + k, f); num(c, fmt); c.font = B

# DAILY PICKING
d0 = ptot + 2
rep.cell(d0, 1, "DAILY STEMS PICKED").font = SEC
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun", "Total"]
headrow(d0 + 1, days, 2)
for i, C in enumerate(CROPS):
    row = d0 + 2 + i
    rep.cell(row, 1, C).font = B
    for k in range(7):
        rep.cell(row, 2 + k, f"=SUMIFS({hs},{hc},$A{row},{hd},$D$4+{k})")
        num(rep.cell(row, 2 + k))
    rep.cell(row, 9, f"=SUM(B{row}:H{row})"); num(rep.cell(row, 9)); rep.cell(row, 9).font = B
dt = d0 + 2 + len(CROPS)
rep.cell(dt, 1, "Total").font = B
for k in range(8):
    c = rep.cell(dt, 2 + k, f"=SUM({L(2 + k)}{d0 + 2}:{L(2 + k)}{dt - 1})"); num(c); c.font = B

# PACKED vs SOLD (week)
v0 = dt + 2
rep.cell(v0, 1, "PACKED vs SOLD").font = SEC
rep.cell(v0, 2, "Week to Date (bunches)").font = B
headrow(v0 + 1, ["Packed", "Sold", "Difference", "Diff %"], 2)
cr = f"{ER}$K$2:$K${ERP_N}"
for i, C in enumerate(CROPS):
    row = v0 + 2 + i
    rep.cell(row, 1, C).font = B
    rep.cell(row, 2, f"=E{p0 + 2 + i}")
    rep.cell(row, 3, f'=SUMIFS({q},{cr},$A{row},{st},"INVOICED",{wtd(d_)})')
    rep.cell(row, 4, f"=B{row}-C{row}")
    rep.cell(row, 5, f"=D{row}/C{row}")
    for k, fmt in enumerate(["#,##0", "#,##0", "#,##0", "0.0%"]):
        num(rep.cell(row, 2 + k), fmt)
vt = v0 + 2 + len(CROPS)
rep.cell(vt, 1, "Total").font = B
for k, fmt in enumerate(["#,##0", "#,##0", "#,##0", "0.0%"]):
    f = f"=D{vt}/C{vt}" if k == 3 else f"=SUM({L(2 + k)}{v0 + 2}:{L(2 + k)}{vt - 1})"
    c = rep.cell(vt, 2 + k, f); num(c, fmt); c.font = B
rep.cell(vt + 1, 1, "Gift and mixed items are made up from other stems and are not in this table.").font = \
    Font(italic=True, size=9)
rep.cell(vt + 3, 1, "Grey cells are typed in each week. Paste the ERP and packhouse extracts (1st of month to "
                    "week ending) into the paste tabs and fill the formula columns down.").font = Font(italic=True, size=9)
rep.freeze_panes = "B6"
rep.sheet_view.showGridLines = False
wb.save(OUTF)
print("saved", OUTF, "erp rows", ERP_N - 1, "harvest", HV_N - 1, "packout", PK_N - 1)
