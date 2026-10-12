# Functional Anchors: Refactoring the Anchor Pattern with One DAX Function

> [Read the article on LinkedIn](#) *(link to be added on publish)*

The demo for collapsing the Anchor Pattern's near-identical window measures into a single DAX user-defined function. This is a direct sequel to the Anchor Pattern demo: same model, same windows, but the repeated measure logic is written once as a function and called in a single line per window.

## What This Demonstrates

The Anchor Pattern left several window measures that were identical except for two things: how many months to reach back, and which base measure to wrap. Those two become the parameters of one function:

- A **user-defined function** (`WindowedMeasure`) that takes the base measure and the month offset, and holds the window logic once
- **One-line callers**, so `KGs 24M = WindowedMeasure ( [KGs], -24 )` replaces a full copied measure
- The **passing-mode lesson**: the base measure is passed as `ANYREF EXPR` (lazy) so it can be re-evaluated inside `CALCULATE ( ..., ALL ( Dim_Date ) )`. Pass it as a value (`ANYVAL VAL`) and the window collapses to a single month
- Built **natively in Power BI Desktop** using DAX query view, with no external tools

## The Model

The same star schema as the Anchor Pattern demo (the `Imports` fact, `Dim_Country`, and a DAX `Dim_Date`), with the window logic moved out of the individual measures and into the `WindowedMeasure` function. A dedicated page shows three arbitrary windows (10, 15 and 20 months) of the same base measure, each from its own one-line caller, so you can see they all run off the one function.

## Files

- `Functional Anchors.pbip` - the completed Power BI project with the `WindowedMeasure` function and the one-line caller measures
- `Functional Anchors.Report` - report definition (visuals, layout, formatting)
- `Functional Anchors.SemanticModel` - model definition (tables, relationships, measures, and the function in `functions.tmdl`)
- `data/Imports.csv` - sample monthly import figures (kilograms and dollar value) by country
- `data/Dim_Country.csv` - the country dimension (country, code, region)

`Dim_Date` is built in DAX, so there is no date CSV to load.

## Setup

1. Open `Functional Anchors.pbip` in Power BI Desktop
2. The model, the `WindowedMeasure` function, and the caller measures are all pre-built, so the report is ready to explore straight away
3. The source CSVs in the `data` folder are included so you can reload or inspect the sample data

The article walks through building the function from scratch, including the bug that makes the passing mode matter. This project is the finished result to compare against.

## Key Things to Look At

- The `WindowedMeasure` function under the Functions node in Model Explorer (stored in `functions.tmdl`)
- The `ANYREF EXPR` parameter, and why `CALCULATE ( BaseMeasure, ALL ( Dim_Date ) )` only works because the measure is passed lazily
- The one-line caller measures, and how each window is now a single call
- The comparison page: three different window lengths from the same function, agreeing exactly where they overlap
- How measures are passed unqualified (`[KGs]`), since measure names are unique across the model