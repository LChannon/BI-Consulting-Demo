# Field Parameters: Letting Your Users Drive the Report

> [Read the article on LinkedIn](#) *(link to be added on publish)*

The demo for using field parameters to let the user choose which dimension sits on the axis and which measure sits in the values, all from a single slicer, so one visual can support several views instead of building a copy per view. This is a direct sequel to the KPI Matrix demo, where the developer controlled the layout; here that control is handed to the user.

## What This Demonstrates

Field parameters turn a small generated table into a list of selectable fields, so a slicer chooses which field a visual uses rather than filtering the data. This demo builds two of them, plus a comparison extension:

- A **dimension switcher** (`View By`) that swaps the axis between Region, Product Category and Channel while the measure stays put
- A **measure switcher** (`Metric`) that flips the value between Revenue, Units, Margin % and Budget, including one metric that lives in a separate fact table
- A **two measure comparison** using a second parameter, so the user picks two metrics and plots them against each other over time

## The Model

Unlike the lean single fact model in the KPI Matrix demo, this one is a conventional star schema so there are dimensions to slice by:

- `Fact_Sales` at daily grain, with keys for Date, Region, Product and Channel
- `Fact_Budget` at monthly grain, with keys for Region, Product, Channel and Month
- `Dim_Date` (built in DAX), plus `Dim_Region`, `Dim_Product` and `Dim_Channel`, each carrying a Sort_Order column

Because the two facts meet the date dimension at different grains (daily vs monthly), the Budget measure behaves differently below month level. The article explains this grain caveat in full.

## Files

- `Field Parameters.pbip` - the completed Power BI project with both field parameters, all measures, and the star schema configured
- `Field Parameters.Report` - report definition (visuals, layout, formatting)
- `Field Parameters.SemanticModel` - model definition (tables, relationships, measures)
- `data/Fact_Sales.csv` - sample daily sales transactions
- `data/Fact_Budget.csv` - monthly budget targets at Region, Product, Channel and Month grain
- `data/Dim_Region.csv`, `data/Dim_Product.csv`, `data/Dim_Channel.csv` - the shared dimensions

## Setup

1. Open `Field Parameters.pbip` in Power BI Desktop
2. The model, both field parameters, and all measures are pre-built, so the report is ready to explore straight away
3. The source CSVs in the `data` folder are included so you can reload or inspect the sample data

The article walks through building both parameters from scratch. This project is the finished result to compare against.

## Key Things to Look At

- The two generated parameter tables (`View By` and `Metric`), and how their slicers are set to single-select
- How the `Metric` switcher spans both fact tables because the dimensions are conformed
- How Margin % stays correct when swapped in, because the correctness lives in the measure rather than the parameter
- The Budget measure behaviour when the axis is drilled below month level