"""Warehouse Ready demo data: dimension tables (NVX greenhouse cut flowers).
Range Apr 2023 to Mar 2026. ERP dates dd/mm/yyyy, Production dates ISO. Deliberate mess included.
"""
import random, csv, os
from datetime import date, timedelta

random.seed(2023)
# Default output: "01 The Decision/data" next to this _generator folder. Override with an argument.
import sys
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "01 The Decision", "data")
for sub in ("ERP", "Production", "Manual"):
    os.makedirs(os.path.join(OUT, sub), exist_ok=True)

def w(path, header, rows):
    with open(os.path.join(OUT, path), "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(header)
        wr.writerows(rows)

def nz(d):  # ERP export format
    return d.strftime("%d/%m/%Y") if d else ""

def iso(d):
    return d.isoformat() if d else ""

# ---------------- Production: Varieties ----------------
# crop, prefix, [(cultivar, colour)], grades (cm), bunch sizes
CROPS = [
    ("ROSE", "RS", [("Crimson Star", "Red"), ("Velvet Night", "Red"), ("Snowdrift", "White"),
                    ("Blush Pearl", "Pink"), ("Sunburst", "Yellow"), ("Amber Glow", "Orange"),
                    ("Lavender Mist", "Purple")], [40, 50, 60, 70], [10, 20]),
    ("LILY", "LL", [("Starlight", "White"), ("Rosa Bella", "Pink"), ("Golden Crown", "Yellow"),
                    ("Ruby Flame", "Red")], [60, 70, 80], [5, 10]),
    ("CHRYSANTHEMUM", "CH", [("Polar Disc", "White"), ("Lime Spray", "Green"), ("Bronze Spray", "Bronze"),
                             ("Sunny Disc", "Yellow"), ("Plum Spray", "Purple")], [70, 80], [10]),
    ("GERBERA", "GB", [("Scarlet Ray", "Red"), ("Candy Ray", "Pink"), ("Citrus Ray", "Orange"),
                       ("Cream Ray", "White")], [45, 55], [10]),
    ("LISIANTHUS", "LS", [("Snow Bell", "White"), ("Violet Bell", "Purple"), ("Champagne Bell", "Cream")],
     [60, 70], [10]),
]
NEW_VARIETY = ("ROSE", "Coral Dawn", "Coral", date(2024, 9, 2))  # year 2 introduction

varieties = []  # dicts
for crop, pre, cults, grades, bunches in CROPS:
    for i, (cv, col) in enumerate(cults, 1):
        varieties.append(dict(code=f"{pre}{i:02d}", crop=crop, name=cv, colour=col,
                              grades=grades, bunches=bunches, intro=date(2019, 7, 1)))
crop, cv, col, intro = NEW_VARIETY
cdef = next(c for c in CROPS if c[0] == crop)
varieties.append(dict(code=f"{cdef[1]}{len(cdef[2]) + 1:02d}", crop=crop, name=cv, colour=col,
                      grades=cdef[3], bunches=cdef[4], intro=intro))

rows = []
for v in varieties:
    name = v["name"].upper() if random.random() < 0.25 else v["name"]       # inconsistent case
    name = name + "  " if random.random() < 0.2 else name                     # trailing spaces
    colour = v["colour"].lower() if random.random() < 0.3 else v["colour"]
    rows.append([v["code"], name, v["crop"], colour, iso(v["intro"]), "Y"])
w("Production/Varieties.csv", ["VarietyCode", "VarietyName", "Crop", "Colour", "IntroducedDate", "Active"], rows)

# ---------------- Production: Greenhouses ----------------
gh = [
    ("GH01", "North House 1", "Home Block", 4200, "ROSE", date(2015, 8, 1)),
    ("GH02", "North House 2", "Home Block", 4200, "ROSE", date(2015, 8, 1)),
    ("GH03", "South House", "Home Block", 3600, "LILY", date(2017, 3, 1)),
    ("GH04", "Long House", "River Block", 5000, "CHRYSANTHEMUM", date(2018, 10, 1)),
    ("GH05", "Glasshouse A", "River Block", 3000, "GERBERA/LISIANTHUS", date(2020, 6, 1)),
    ("GH06", "North House 3", "Home Block", 4500, "ROSE", date(2025, 7, 14)),  # year 3 expansion
]
w("Production/Greenhouses.csv", ["GreenhouseCode", "GreenhouseName", "Site", "AreaM2", "PrimaryCrop", "CommissionedDate"],
  [[c, n, s, a, p, iso(d)] for c, n, s, a, p, d in gh])

# ---------------- Production: Staff ----------------
first = ["Aroha", "Mere", "Tama", "Wiremu", "Sione", "Losa", "Priya", "Arjun", "Mei", "Jun", "Sarah", "James",
         "Emma", "Liam", "Grace", "Noah", "Ana", "Mateo", "Hana", "Ravi", "Chloe", "Ben", "Isla", "Tevita",
         "Kiri", "Daniel", "Olivia", "Sam", "Ruby", "Leon"]
last = ["Ngata", "Walker", "Tupou", "Patel", "Chen", "Smith", "Brown", "Wilson", "Taufa", "Singh", "Kaur",
        "Nguyen", "Te Rangi", "Fraser", "Morgan", "Reid", "Faleolo", "Kim", "Harris", "Campbell"]
random.shuffle(first)
staff = []
roles = (["Supervisor"] * 2) + (["Picker"] * 15) + (["Packer"] * 8)
fy_start, fy_end = date(2023, 4, 1), date(2026, 3, 31)
for i, role in enumerate(roles, 1):
    seasonal = role != "Supervisor" and random.random() < 0.35
    start = date(2018, 1, 8) + timedelta(days=random.randint(0, 1900))
    end = None
    if random.random() < 0.25 and role != "Supervisor":
        end = fy_start + timedelta(days=random.randint(120, 900))
    if start > fy_end - timedelta(days=60):
        start = fy_end - timedelta(days=200)
    staff.append([f"S{i:04d}", first[i - 1], random.choice(last), role,
                  "Seasonal" if seasonal else "Permanent", iso(start), iso(end)])

# ---------------- ERP: Items ----------------
# ERP item code numeric, description free text, its own product group. Prices NZD per bunch.
base_price = {"ROSE": 1.10, "LILY": 2.40, "CHRYSANTHEMUM": 0.95, "GERBERA": 1.00, "LISIANTHUS": 1.60}  # per stem
erp_group = {"ROSE": "ROSES", "LILY": "Lilies", "CHRYSANTHEMUM": "CHRYSANTHS", "GERBERA": "Gerberas",
             "LISIANTHUS": "LISIANTHUS"}
items, item_rows = [], []
n = 10100
for v in varieties:
    for g in v["grades"]:
        for b in v["bunches"]:
            n += 7
            stem = base_price[v["crop"]] * (1 + (g - v["grades"][0]) / 100 * 1.5)
            price = round(stem * b * (0.95 if b >= 20 else 1.0), 2)
            crop_word = v["crop"].title() if v["crop"] != "CHRYSANTHEMUM" else "Chrys"
            desc = f"{crop_word} {v['name']} {g}cm x{b}"
            r = random.random()
            if r < 0.15:
                desc = desc.upper()
            elif r < 0.25:
                desc = desc + " "
            created = max(v["intro"], date(2019, 7, 1))
            code = f"FL{n}"
            items.append(dict(code=code, variety=v["code"], crop=v["crop"], grade=g, bunch=b, price=price,
                              created=created, composite=False))
            item_rows.append([code, desc, erp_group[v["crop"]], g, b, "BUNCH", f"{price:.2f}", nz(created), "Y"])
# composite items with no single variety (deliberately unmapped later)
for desc, grp, b, price in [("Valentine Rose Box 12 Mixed", "GIFT", 12, 29.50),
                            ("Seasonal Mixed Bunch", "MIXED", 15, 18.00),
                            ("Mothers Day Bouquet Premium", "GIFT", 20, 42.00)]:
    n += 7
    code = f"FL{n}"
    items.append(dict(code=code, variety=None, crop="MIXED", grade=None, bunch=b, price=price,
                      created=date(2021, 1, 15), composite=True))
    item_rows.append([code, desc, grp, "", b, "EACH", f"{price:.2f}", nz(date(2021, 1, 15)), "Y"])
w("ERP/Items.csv", ["ItemCode", "ItemDescription", "ProductGroup", "StemLengthCm", "StemsPerBunch", "UOM",
                    "ListPriceNZD", "CreatedDate", "Active"], item_rows)

# ---------------- ERP: Customers ----------------
channels = (["Florist"] * 30) + (["Wholesaler"] * 12) + (["Supermarket"] * 6) + (["Export"] * 8) + (["Online"] * 4)
nz_places = [("Auckland", "Auckland"), ("Wellington", "Wellington"), ("Christchurch", "Canterbury"),
             ("Hamilton", "Waikato"), ("Tauranga", "Bay of Plenty"), ("Dunedin", "Otago"),
             ("Napier", "Hawke's Bay"), ("Nelson", "Nelson"), ("Palmerston North", "Manawatu-Whanganui"),
             ("Queenstown", "Otago"), ("New Plymouth", "Taranaki"), ("Whangarei", "Northland")]
export_places = [("Sydney", "NSW", "Australia"), ("Melbourne", "VIC", "Australia"), ("Tokyo", "Tokyo", "Japan"),
                 ("Osaka", "Osaka", "Japan"), ("Singapore", "Singapore", "Singapore"),
                 ("Los Angeles", "CA", "United States"), ("Hong Kong", "Hong Kong", "Hong Kong"),
                 ("Brisbane", "QLD", "Australia")]
fl_a = ["Petal", "Bloom", "Stem", "Posy", "Fern", "Willow", "Juniper", "Magnolia", "Poppy", "Kowhai",
        "Harbour", "Hill Street", "Garden Gate", "Wild", "Little", "Blossom", "Ivy", "Meadowlark", "Rata", "Tui",
        "Lantern", "Bluebell", "Dahlia", "Orchard Lane", "Clover", "Primrose", "Kauri", "Thistle", "Sage", "Hazel"]
fl_b = ["Florist", "Flowers", "Floral Studio", "Flower Co", "Botanics"]
random.shuffle(fl_a)
cust = []
fl_i = 0
ws_names = ["Central Flower Markets", "Southern Floral Wholesale", "Island Bloom Distributors", "Metro Stems Ltd",
            "Coastline Flower Supply", "Pacific Petal Traders", "Northern Flower Exchange", "Capital Wholesale Flowers",
            "Plains Floral Supply", "Bay Flower Hub", "Lakes Wholesale Blooms", "Mainland Stems"]
sm_names = ["FreshMart Supermarkets", "ValuePlus Foods", "Corner Grocer Group", "UrbanFresh Markets",
            "HomeBasket Stores", "GreenLeaf Grocers"]
ex_names = ["Harbour Bloom Imports Pty", "Southern Cross Flowers Pty", "Sakura Flower Trading KK",
            "Kansai Hana Imports", "Lion City Florals Pte", "Pacific Coast Blooms Inc", "Victoria Petal Imports",
            "Sunshine Coast Stems Pty"]
on_names = ["FlowersToday Online", "BloomBox NZ", "Same Day Stems", "PostAPosy"]
counters = {"Wholesaler": 0, "Supermarket": 0, "Export": 0, "Online": 0}
for i, ch in enumerate(channels, 1):
    if ch == "Florist":
        name = f"{fl_a[fl_i]} {random.choice(fl_b)}"; fl_i += 1
        city, region = random.choice(nz_places); country = "New Zealand"
    elif ch == "Export":
        k = counters[ch]; name = ex_names[k]; counters[ch] += 1
        city, region, country = export_places[k]
    else:
        lst = {"Wholesaler": ws_names, "Supermarket": sm_names, "Online": on_names}[ch]
        k = counters[ch]; name = lst[k]; counters[ch] += 1
        city, region = random.choice(nz_places); country = "New Zealand"
    terms = {"Florist": "20M", "Wholesaler": "20M", "Supermarket": "30D", "Export": "CIA", "Online": "7D"}[ch]
    created = date(2016, 3, 1) + timedelta(days=random.randint(0, 2900))
    if random.random() < 0.15:  # some customers join during the demo range
        created = date(2023, 5, 1) + timedelta(days=random.randint(0, 900))
    active = "N" if random.random() < 0.08 else "Y"
    if random.random() < 0.1:
        name = name.upper()
    if random.random() < 0.1:
        name = name + " "
    cust.append([f"C{10000 + i * 3}", name, ch, city, region, country, terms, nz(created), active])
w("ERP/Customers.csv", ["CustomerCode", "CustomerName", "Channel", "City", "Region", "Country", "PaymentTerms",
                        "CreatedDate", "Active"], cust)

# replacements for leavers (added after the other tables so their random sequence is unchanged)
rep_first = ["Tane", "Lucy", "Hemi", "Zara", "Kai", "Maya", "Finn", "Leilani", "Oscar", "Anahera"]
for s_ in list(staff):
    if s_[6]:
        end = date.fromisoformat(s_[6])
        start = end + timedelta(days=random.randint(14, 45))
        if start <= fy_end:
            staff.append([f"S{len(staff) + 1:04d}", rep_first.pop(0), random.choice(last), s_[3],
                          s_[4], iso(start), ""])
w("Production/Staff.csv", ["StaffID", "FirstName", "LastName", "Role", "EmploymentType", "StartDate", "EndDate"], staff)

print("varieties", len(varieties), "greenhouses", len(gh), "staff", len(staff), "items", len(item_rows),
      "customers", len(cust))
