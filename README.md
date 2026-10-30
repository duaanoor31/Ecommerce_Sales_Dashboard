# Commerce Pulse dashboard

An interactive Streamlit dashboard based on `Untitled2.ipynb` and its e-commerce sales analysis.

## Run it

From this folder, activate the existing virtual environment and start Streamlit:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

Streamlit, pandas, and Plotly are already installed in this workspace's `.venv`. The install command is included for other environments.

## Data

The notebook's original `ecommerce_sales_data.csv` was not present in the project folder. Until it is supplied, the dashboard starts with the 10 rows preserved in the notebook's head and tail outputs. It labels these as a preview and separately displays the notebook's recorded totals and data-quality findings for all 1,000 rows.

To explore the complete dataset, either upload the CSV in the sidebar or put it beside `app.py` as `ecommerce_sales_data.csv`. The CSV must include `Year`, `Month`, `Category`, `Region`, `Units_Sold`, `Revenue`, `Profit`, `Customer_Rating`, and `Ad_Spend`.

## Dashboard views

- **Overview:** selected KPIs, monthly or yearly trend, cumulative totals, category mix, revenue leaders, and profit/revenue relationship.
- **Products & regions:** category ranking, category-by-region revenue heatmap, seasonal comparison, and profit outlier view.
- **Marketing & customers:** advertising spend versus revenue, ROAS distribution, and category customer ratings.
- **Data explorer:** filtered rows, CSV download, missing-value counts, duplicate check, and date/revenue quality checks.

Dates and seasons are derived from both `Year` and `Month`, so monthly trends use the actual month. This also avoids the notebook's year-only date conversion, which placed every row in January.
# Ecommerce_Sales_Dashboard
