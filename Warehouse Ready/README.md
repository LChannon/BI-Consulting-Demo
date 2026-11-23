# Warehouse Ready

> A four-part series on building a Power BI model in the shape of a data warehouse before the warehouse exists, and what that made possible three years later.

Based on real client work. A business reporting from weekly copy-paste spreadsheets wasn't ready to invest in an information layer, so the Power BI model was built as a star schema from the start, with facts and dimensions shaped the way a warehouse would hold them. Three years on, when the warehouse was built, most of the report migration came down to re-pointing queries.

The series follows that journey using NVX Flowers, a fictional greenhouse grower of cut flowers, with sample data from an ERP, a packhouse system and hand-kept spreadsheets.

## The Parts

| Part | Folder | What it covers |
|---|---|---|
| 1 | [01 The Decision](01%20The%20Decision) | The starting point: the source data and the manual weekly Excel report, and why the model was built in the warehouse's shape |
| 2 | [02 The Build](02%20The%20Build) | The first model: staging queries, one output query per fact and dimension, natural keys and the first pass at matching products across systems |
| 3 | [03 The Model Grows](03%20The%20Model%20Grows) | New sources added without restructuring: the budget, more operational data, and the mappings moving from Excel to SharePoint |
| 4 | [04 The Migration](04%20The%20Migration) | Moving onto the warehouse: what was a simple swap, and what still took work |

Each part has its own README and is published with a LinkedIn article *(links to be added on publish)*.

## Folder Layout

Each part follows the same layout as the other demos in this repo:

- A `data` folder with the source data used in that part, split into `ERP`, `Production` and `Manual`
- A Power BI project (`.pbip`) with its `.Report` and `.SemanticModel` folders (from part 2 onwards)
- A `README.md` covering the files, setup and what to look at

The `_generator` folder holds the Python scripts that produced the sample data.

## The Sample Data

- **Period:** April 2023 to March 2026, three financial years starting in April
- **ERP:** customers, items, sales order headers and lines
- **Packhouse system:** varieties, greenhouses, staff, harvest and pack-out
- **Manual:** the product mapping (item to variety, plus the range grouping) and the sales budget, as Excel workbooks

The data includes peaks around Valentine's Day, Mother's Day and Christmas, a new variety in year 2, a new greenhouse in year 3, and the inconsistencies real extracts carry. All names are invented.
