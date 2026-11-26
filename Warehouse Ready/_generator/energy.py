"""Warehouse Ready demo data (part 03): greenhouse energy use from a separate monitoring system.
Energy/Meters.csv          meter list: meter IDs don't match greenhouse codes
Energy/MeterUsage.csv      daily usage per meter (gas in GJ, electricity in kWh)
Manual/EnergyTariffs.xlsx  hand-kept rate per unit with an effective-from date (gas price rise in July 2024)
Rates and usage intensities are plausible for a heated NZ greenhouse, not researched figures.
Usage: python energy.py [data folder]   (run after dims.py)
"""
import csv, os, sys, random, math
from datetime import date, timedelta
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

random.seed(2027)
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "01 The Decision", "data")
os.makedirs(os.path.join(OUT, "Energy"), exist_ok=True)
os.makedirs(os.path.join(OUT, "Manual"), exist_ok=True)
START, END = date(2023, 4, 1), date(2026, 3, 31)

with open(os.path.join(OUT, "Production/Greenhouses.csv"), encoding="utf-8") as f:
    ghs = list(csv.DictReader(f))

# meters: one gas and one electricity meter per greenhouse, numbered by the energy system, not by greenhouse
meters, n = [], 1040
for g in ghs:
    for fuel, unit in (("Gas", "GJ"), ("Electricity", "kWh")):
        n += random.randint(1, 4)
        meters.append(dict(MeterID=f"MTR-{n}", Fuel=fuel, Unit=unit, GreenhouseCode=g["GreenhouseCode"],
                           InstalledDate=max(date.fromisoformat(g["CommissionedDate"]), date(2019, 6, 1)),
                           area=int(g["AreaM2"])))
with open(os.path.join(OUT, "Energy/Meters.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["MeterID", "Fuel", "Unit", "GreenhouseCode", "InstalledDate"])
    for m in meters:
        w.writerow([m["MeterID"], m["Fuel"], m["Unit"], m["GreenhouseCode"], m["InstalledDate"].isoformat()])

def season(d):  # 1.0 at midwinter (mid July), 0.0 at midsummer (mid January), southern hemisphere
    return (1 + math.cos(2 * math.pi * (d.timetuple().tm_yday - 196) / 365.25)) / 2

rows = []
d = START
while d <= END:
    cold_snap = 1.25 if random.random() < 0.04 else 1.0
    for m in meters:
        if d < m["InstalledDate"]:
            continue
        s = season(d)
        if m["Fuel"] == "Gas":  # heating: about 1.2 GJ per m2 a year, mostly in winter
            base = m["area"] * (0.0008 + 0.0068 * s) * cold_snap
            use = round(base * random.uniform(0.9, 1.1), 2)
        else:  # fans, pumps and lighting: about 50 kWh per m2 a year, more in winter for lighting
            base = m["area"] * (0.105 + 0.07 * s)
            use = round(base * random.uniform(0.92, 1.08), 1)
        rows.append([d.isoformat(), m["MeterID"], use])
    d += timedelta(days=1)
with open(os.path.join(OUT, "Energy/MeterUsage.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["ReadingDate", "MeterID", "Usage"])
    w.writerows(rows)

tariffs = [("Gas", "GJ", 16.50, date(2023, 4, 1)), ("Electricity", "kWh", 0.19, date(2023, 4, 1)),
           ("Electricity", "kWh", 0.21, date(2024, 4, 1)), ("Gas", "GJ", 24.80, date(2024, 7, 1)),
           ("Gas", "GJ", 27.20, date(2025, 4, 1)), ("Electricity", "kWh", 0.23, date(2025, 4, 1))]
wb = Workbook()
ws = wb.active
ws.title = "Tariffs"
ws.append(["Fuel", "Unit", "RatePerUnitNZD", "EffectiveFrom"])
for c in ws[1]:
    c.font, c.fill = Font(bold=True, color="FFFFFF"), PatternFill("solid", fgColor="1F4E79")
for t in tariffs:
    ws.append(list(t))
    ws.cell(ws.max_row, 4).number_format = "dd/mm/yyyy"
for col, wd in zip("ABCD", [13, 8, 16, 14]):
    ws.column_dimensions[col].width = wd
wb.save(os.path.join(OUT, "Manual/EnergyTariffs.xlsx"))
print("meters", len(meters), "usage rows", len(rows))
