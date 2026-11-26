# Warehouse Ready: The Model Grows

> [Read the article on LinkedIn](#) *(link to be added on publish)*

Part 3 of the Warehouse Ready series. The part 2 model takes on new data: the product mapping moves to SharePoint, a sales budget arrives at a different grain from sales, and a new energy monitoring system adds daily gas and electricity use per greenhouse. Each change slots into the existing structure without rebuilding what was already there.

## What This Demonstrates

- **A source moving location**: the product mapping now comes from SharePoint. Only `stg_ProductMapping` and `stg_RangeList` change; every output query, measure and visual stays the same
- **A budget at a different grain**: set by range and month, joined to the product dimension through one default item per range, and spread evenly across the days of each month so weekly and month-to-date budgets work like any other measure
- **A new source system**: energy meters with their own IDs, matched to greenhouses through the meter list, and costed at the tariff in force on each day
- **A new report page** for energy trends, alongside the unchanged weekly report

## The Model

The part 2 star schema with two new facts:

- `Fact_Budget` - budgeted bunches and sales by day and item, from the monthly budget by range. Report it at range level and above
- `Fact_Energy` - gas and electricity use and cost by meter and day. It relates to `Dim_Greenhouse` and `Dim_Date` only, so it can be reported by greenhouse or in total but not by product

`Fact_Sales`, `Fact_Harvest`, `Fact_PackOut` and the dimensions are as in part 2. The new measures are in the `Budget`, `Energy` and `Month to Date` folders of `_Measures`.

## Files

- `Warehouse Ready - The Model Grows.pbip` - the completed Power BI project
- `Warehouse Ready - The Model Grows.Report` - report definition (Weekly Report and Energy Trends pages)
- `Warehouse Ready - The Model Grows.SemanticModel` - model definition
- `data/ERP/` and `data/Production/` - the same extracts as part 2
- `data/Manual/SP_ProductMapping.xlsx` - the product mapping as if extracted from SharePoint, now with a `RangeDefault` flag for the budget
- `data/Manual/Budget.xlsx` - the sales budget, one sheet per financial year, ranges down the side and months across
- `data/Manual/EnergyTariffs.xlsx` - rate per unit for gas and electricity, with the date each rate took effect
- `data/Energy/Meters.csv` - the energy system's meter list: meter ID, fuel, unit and greenhouse
- `data/Energy/MeterUsage.csv` - daily usage per meter (gas in GJ, electricity in kWh)

## Setup

1. Open `Warehouse Ready - The Model Grows.pbip` in Power BI Desktop
2. In Power Query, set the `FilePath` parameter to the `data` folder in this directory
3. Refresh. The energy query is the slowest step

To read the mapping from SharePoint instead, `stg_ProductMapping` has the `SharePoint.Files` version of its source step as a comment above the local one.

## Key Things to Look At

- `stg_ProductMapping` before and after: the source step changes, and nothing downstream does
- `stg_Budget`, which appends the three year sheets, skips the title rows down to the header and unpivots the months
- `Fact_Budget`, where each monthly figure is divided by the days in the month and spread across them
- `Fact_Energy`, where each reading picks up the latest tariff on or before its date
- The **Weekly Report** page for week ending 16/02/2025: budget columns now sit beside actuals, and the Unmapped row has actuals but no budget
- The **Energy Trends** page: winter peaks, the gas price rise from July 2024, and GH06 starting in July 2025
