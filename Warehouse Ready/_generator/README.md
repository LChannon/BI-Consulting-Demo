# Data Generator

Python scripts that produce the sample data for the Warehouse Ready series. Each script uses a fixed random seed, so running them again gives identical files.

You don't need these to follow the series. The generated files are already in each part's `data` folder. They're here so the data can be rebuilt or adjusted.

## Requirements

- Python 3.10 or later
- `openpyxl` (for the Excel files): `pip install openpyxl`

## Run Order

Each script reads the output of the ones before it, so run them in this order from inside the `_generator` folder:

| Order | Script | Writes | Reads |
|---|---|---|---|
| 1 | `dims.py` | `ERP/Customers.csv`, `ERP/Items.csv`, `Production/Varieties.csv`, `Production/Greenhouses.csv`, `Production/Staff.csv` | nothing |
| 2 | `sales.py` | `ERP/SalesOrderHeader.csv`, `ERP/SalesOrderLines.csv` | customers, items |
| 3 | `production.py` | `Production/Harvest.csv`, `Production/PackOut.csv` | dimensions, sales |
| 4 | `manual.py` | `Manual/ItemVarietyMap.xlsx`, `Manual/ProductRange.xlsx`, `Manual/Budget.xlsx` | items, varieties, sales |
| 5 | `report.py` | `01 The Decision/NVX Weekly Report w-e 16-02-2025.xlsx` | all of the above |

```
python dims.py
python sales.py
python production.py
python manual.py
python report.py
```

By default the scripts write to `../01 The Decision/data`. To write somewhere else, pass the data folder as the first argument, for example `python dims.py C:\temp\data`. `report.py` also takes an optional second argument for the workbook path.

## What the Scripts Build In

- **Seasonality:** Valentine's Day, Mother's Day and December peaks, a winter dip and growth of about 5% a year
- **Events:** the Coral Dawn rose from 2 September 2024, greenhouse GH06 from 14 July 2025, staff leaving and being replaced
- **Reconciliation:** bunches packed run 3 to 8% above bunches sold each week, and stems picked equal stems packed plus rejects
- **Mess:** inconsistent case, trailing spaces, `dd/mm/yyyy` dates in the ERP and ISO dates in the packhouse system, gift items with no variety, and one Coral Dawn item missing from the mapping
- **Budget:** set from actuals with noise, 3% over in FY24, 6% over in FY25 and 2% under in FY26

## Changing the Data

Edit the constants near the top of each script (date range, volumes, crops, channels) and re-run from that script onwards. Changing an earlier script changes everything after it, so re-run the full sequence and re-copy the data into the later parts.
