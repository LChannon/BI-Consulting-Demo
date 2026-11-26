# Warehouse Ready: The Build

> [Read the article on LinkedIn](#) *(link to be added on publish)*

Part 2 of the Warehouse Ready series. This is the first Power BI model: the NVX source data shaped into facts and dimensions the way a data warehouse would hold them, with the manual weekly Excel report from part 1 rebuilt as a report page.

## What This Demonstrates

There is no warehouse yet, so Power Query is as far upstream as the transformations can go. The model is organised so that each table could later be swapped for a warehouse table:

- **Staging queries**, one per source file, that clean the data (trimming, code case, data types, date locales) and are not loaded to the model
- **Output queries**, one per fact and dimension, named and shaped like the warehouse tables they will become
- **Natural keys** from the source systems for every relationship
- **One product dimension** that matches ERP items to packhouse varieties through a hand-kept product mapping
- **Measures in their own table**, so the fact tables hold columns only

## The Model

A star schema with three facts at different grains, sharing their dimensions:

- `Fact_Sales` - one row per sales order line, with the order header joined in. Cancelled orders are kept and flagged
- `Fact_Harvest` - stems picked and harvest hours by picker, greenhouse, variety and day
- `Fact_PackOut` - bunches packed and stems rejected by day, pack line and item
- `Dim_Product` - one row per ERP item, with its packhouse variety, crop, colour and range from the product mapping
- `Dim_Customer`, `Dim_Greenhouse`, `Dim_Staff`
- `Dim_Date` - built from an M date generator driven by the `Start_Year`, `End_Year` and `FinYearStart` parameters, with an April financial year

Harvest is only recorded by variety, so it joins `Dim_Product` through one default item per variety, flagged in the mapping. Pack-out is matched to its item by variety, stem length and bunch size.

## Files

- `Warehouse Ready - The Build.pbip` - the completed Power BI project
- `Warehouse Ready - The Build.Report` - report definition (the Weekly Report page)
- `Warehouse Ready - The Build.SemanticModel` - model definition (queries, tables, relationships, measures)
- `data/ERP/` - customers, items, sales order headers and lines (`dd/mm/yyyy` dates)
- `data/Production/` - varieties, greenhouses, staff, harvest and pack-out (ISO dates)
- `data/Manual/ProductMapping.xlsx` - the hand-kept product mapping: each item's variety, the default item per variety, and its range
- `data/Manual/Budget.xlsx` - the sales budget, not used until part 3

## Setup

1. Open `Warehouse Ready - The Build.pbip` in Power BI Desktop
2. In Power Query, set the `FilePath` parameter to the `data` folder in this directory
3. Refresh. The model, measures and report page are all pre-built

## Key Things to Look At

- The **query groups**: Parameters, Source Files (staging, not loaded) and Report Tables (loaded)
- The staging queries, especially the `en-NZ` locale on the ERP dates and the grade code `G60` turned into a stem length in `stg_PackOut`
- How `Dim_Product` is built from the items, the product mapping and the varieties, and how gift items show as `Mixed` and the item missing from the mapping shows as `Unmapped`
- The three-column match from pack-out to item in `Fact_PackOut`
- The **Weekly Report** page for week ending 16/02/2025. Sales come to $124,921, against $119,985 in the part 1 workbook. The difference is the Coral Dawn rose, which the workbook's lookup tab was missing
- The page-level filter on `Dim_Product[Crop]` that excludes the blank row, so pack-out with no matching item stays off this page and its layout stays fixed. Those rows belong on a data-quality page of their own, which is why the production totals are slightly below the source data
- The month-to-date measures in the `Month to Date` folder, built with `DATESMTD`
