# Warehouse Ready: The Decision

> [Read the article on LinkedIn](#) *(link to be added on publish)*

Part 1 of the Warehouse Ready series. This folder holds the starting point: the source data from two systems and a handful of spreadsheets, and the weekly Excel report that was built from them by hand every week. Parts 2 to 4 replace this report with a Power BI model shaped like a data warehouse, grow that model, and then migrate it onto a real warehouse.

There is no Power BI project in this part. The workbook is the "before" that the rest of the series improves on.

## The Scenario

NVX Flowers is a fictional greenhouse grower of cut flowers (roses, lilies, chrysanthemums, gerberas and lisianthus). Its data lives in three places:

- An **ERP** holding customers, items and sales orders, using its own item codes
- A **packhouse system** holding varieties, greenhouses, staff, harvest and pack-out records, using different codes for the same flowers
- **Spreadsheets** kept by hand: a product mapping from ERP items to packhouse varieties, which also holds a range grouping that exists in neither system, and the sales budget

Each week someone exported from both systems, pasted the extracts into a workbook, filled the formulas down, typed in the budget and sent the report out. The sample data covers April 2023 to March 2026 (three financial years) and includes the kind of mess real extracts carry: inconsistent case, trailing spaces, two date formats and codes that don't line up between systems.

All company, customer, staff and variety names are invented.

## The Weekly Report

`NVX Weekly Report w-e 16-02-2025.xlsx` is the report for Valentine's week 2025, one of the busiest weeks of the year.

- **Report** tab: sales by range against budget, production by crop, daily stems picked and packed vs sold, for the week and the month to date
- **ERP Paste**, **Harvest Paste** and **PackOut Paste** tabs: the raw extracts from 1 to 16 February, with lookup columns added by hand to the right of each paste
- **Lookups** tab: a hand-kept copy of the item and variety mappings that the report depends on

Grey cells are typed in each week: the week ending date, who prepared the report, and every budget figure.

## Files

- `NVX Weekly Report w-e 16-02-2025.xlsx` - the manual weekly report
- `data/ERP/Customers.csv` - 60 customers across five channels (florist, wholesaler, supermarket, export, online)
- `data/ERP/Items.csv` - 115 sellable items by variety, stem length and bunch size, plus three gift and mixed items
- `data/ERP/SalesOrderHeader.csv` - one row per sales order
- `data/ERP/SalesOrderLines.csv` - one row per order line, with quantity in bunches and value in NZD
- `data/Production/Varieties.csv` - 24 varieties across five crops, including one introduced in September 2024
- `data/Production/Greenhouses.csv` - six greenhouses, one commissioned in July 2025
- `data/Production/Staff.csv` - pickers, packers and supervisors, including leavers and their replacements
- `data/Production/Harvest.csv` - stems picked and harvest hours by picker, greenhouse, variety and day
- `data/Production/PackOut.csv` - bunches packed and stems rejected by variety, grade and bunch size per day
- `data/Manual/ProductMapping.xlsx` - maintained by hand: each ERP item's packhouse variety, a default item for each variety, and its range (Premium, Everyday or Seasonal)
- `data/Manual/Budget.xlsx` - monthly sales budget, one sheet per financial year, with months across the columns

ERP files use `dd/mm/yyyy` dates and packhouse files use `yyyy-mm-dd`, as the two systems exported them.

## Setup

1. Open the workbook in Excel. The formulas recalculate on opening
2. Change the week ending date on the Report tab to see the formulas respond, bearing in mind the paste tabs only hold 1 to 16 February 2025
3. The `data` folder is the source data for every later part of the series

## Key Things to Look At

- The **check row** under Total Sales. It should be zero, and it isn't: $4,936 for the week and $13,871 for the month are missing from the report
- The cause, on the **Lookups** tab: the Coral Dawn rose was added in September 2024 and never added to the hand-kept lookups, so its sales and stems drop out of every total without an error
- The **lookup columns** on each paste tab, which have to be filled down to match the number of pasted rows every week
- **Packed vs sold** for roses: fewer bunches packed than sold, because Monday's Valentine orders were packed the Saturday before, in the previous week. A weekly cut-off can't line up packing and sales in a peak week
- What the report **can't** show: anything outside the pasted month. There is no trend, no comparison with last year and no history, which is where part 2 starts

## About the Data

The data in this folder was generated with the Python scripts in `../_generator`, seeded so they produce the same files every time. Later parts copy this data into their own folders.
