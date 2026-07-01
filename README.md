# Power BI Article Demos

Demo files and sample data to accompany Power BI articles for LinkedIn.

Each folder contains everything you need to follow along with the article - sample data, and a completed Power BI file with all measures and formatting in place.

**Author:** Lee Channon (https://www.linkedin.com/in/lee-channon/)

**Company:** Montage Business Intelligence Limited (https://www.linkedin.com/company/montage-business-intelligence-limited)

---

## Articles

### 01 - The KPI Matrix Problem Nobody Talks About in Power BI

> [Read the article on LinkedIn](#) *(link to be added on publish)*

How to build a dynamic KPI matrix in Power BI that displays multiple measures as rows with MTD and YTD columns, each formatted differently per row, with conditional formatting driven by a single companion measure. Uses the SWITCH(TRUE()) pattern with two disconnected tables.

**Files**
- `KPI_Matrix_Demo.pbix` - completed Power BI file with all measures, disconnected tables, and conditional formatting configured
- `Fact_Sales.csv` - sample daily sales transactions for January through March 2025
- `Budget.csv` - monthly sales targets for the same period

**Setup**
1. Load `Fact_Sales.csv` and `Budget.csv` into Power BI Desktop
2. Create the `Dim_Date` calculated table using the DAX provided in the article
3. Set relationships as shown in the article model diagram
4. All measures and disconnected tables are pre-built in the PBIX file

---

## About This Repo

These files are provided for learning and reference purposes. Feel free to use and adapt them in your own work.

See [LICENSE](LICENSE) for terms.