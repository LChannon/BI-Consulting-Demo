# The Anchor Pattern: One Selection, Many Historical Windows

> [Read the article on LinkedIn](#) *(link to be added on publish)*

The demo for driving an entire multi-page report from a single month selection. The user picks one month, the anchor, and every page reports back from it over a different window: 24 months on one page, 50 months on another, 10 years on a third. One selection, synced across the report, with each page showing whatever span it needs.

## What This Demonstrates

A relative date filter is anchored to today and set per page, so it can't report "as of a chosen historical month" or drive different windows from one shared selection. The anchor pattern does both, by treating the slicer selection as information rather than a filter:

- A **single-select month slicer** (the anchor) that sets the endpoint and is synced across every page
- A **window measure** that reads the anchor, walks back by a set number of months with `EDATE`, and gates each row so only the months inside the window appear
- A **display field on the fact table** that survives the date filter being stripped, so each visual shows a full range of months instead of collapsing to the selected one
- **Honest edges**: anchor to a month with less history than the window asks for, and the visual shows what exists, with no padding or false zeros

## The Model

A simple star, with everything clever living in the measures rather than the model:

- `Imports` fact at monthly grain, with a Date, a Country, and the raw figures (kilograms imported and dollar value)
- `Dim_Country` for slicing by region
- `Dim_Date` (built in DAX with `CALENDAR()`), carrying a contiguous date column, a month-year column for the slicer, and the usual sort keys

The sample data spans about a decade of monthly figures, with a deliberate shape (steady growth and a supply-driven price spike) so the ten-year window has a real story to show.

## Files

- `The Anchor Pattern.pbip` - the completed Power BI project with the three window measures and the synced anchor slicer
- `The Anchor Pattern.Report` - report definition (visuals, layout, formatting)
- `The Anchor Pattern.SemanticModel` - model definition (tables, relationships, measures)
- `data/Imports.csv` - sample monthly import figures (kilograms and dollar value) by country
- `data/Dim_Country.csv` - the country dimension (country, code, region)

`Dim_Date` is built in DAX, so there is no date CSV to load.

## Setup

1. Open `The Anchor Pattern.pbip` in Power BI Desktop
2. The model, the Date table, the measures, and the synced anchor slicer are all pre-built, so the report is ready to explore straight away
3. The source CSVs in the `data` folder are included so you can reload or inspect the sample data

The article walks through building this from scratch. This project is the finished result to compare against.

## Key Things to Look At

- The single-select month slicer, and how Sync Slicers shares it across every page
- The window measure: the endpoint from `MAX(Dim_Date[Date])`, the `EDATE` walk-back, and the `IF` gate that shows only the months in range
- How the display field sits on the fact table and survives `ALL(Dim_Date)`, which is what lets a visual show a range rather than a single month
- How the three windows differ by only two things: the `EDATE` offset and the base measure being wrapped
- The edge behaviour: anchor to an early month (for example Jul 2020) and watch the ten-year window show a clean partial range