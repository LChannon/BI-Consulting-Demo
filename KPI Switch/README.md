# The KPI Matrix Problem Nobody Talks About in Power BI

> [Read the article on LinkedIn](#) *(link to be added on publish)*

The demo for building a dynamic KPI matrix that displays multiple measures as rows with MTD and YTD columns, each row formatted differently, with conditional formatting driven by a single companion measure. It uses the `SWITCH(TRUE())` pattern with two disconnected tables.

## What This Demonstrates

A standard matrix forces every value to share the same format string and the same conditional formatting rules. That falls apart the moment you want revenue as currency, margin as a percentage, and order count as a whole number in the same matrix. This demo shows how to break that constraint using:

- Two disconnected tables to drive the rows (the measures) and the columns (the time periods)
- A `SWITCH(TRUE())` measure that returns the right calculation for each row and column combination
- A companion measure that applies per row conditional formatting from a single rule

## Files

- `KPI Switch.pbip` - the completed Power BI project with all measures, disconnected tables, and conditional formatting configured
- `KPI Switch.Report` - report definition (visuals, layout, formatting)
- `KPI Switch.SemanticModel` - model definition (tables, relationships, measures)
- `data/Fact_Sales.csv` - sample daily sales transactions for January through March 2025
- `data/Budget.csv` - monthly sales targets for the same period

## Setup

1. Open `KPI Switch.pbip` in Power BI Desktop
2. The model, measures, disconnected tables, and conditional formatting are all pre-built, so the report is ready to explore straight away
3. The source CSVs in the `data` folder are included so you can reload or inspect the sample data

The article walks through building this from scratch. This project is the finished result to compare against.

## Key Things to Look At

- The disconnected tables that supply the row and column selections
- The `SWITCH(TRUE())` measure that maps each selection to its calculation and format
- The companion measure wired into the matrix conditional formatting