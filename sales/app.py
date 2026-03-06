import pandas
import plotly.express as px
import calendar
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from pathlib import Path
from shiny import reactive
from shiny.express import render, input, ui
from shiny.ui import layout_column_wrap, layout_columns
from shinywidgets import render_plotly, render_altair, render_widget

ui.page_opts(title="Sales Dashboard -- Video 1 of 5", fillable=False)

@reactive.calc
def dat():
    infile = Path(__file__).parent / "data/sales.csv"
    df = pandas.read_csv(infile)
    df["order_date"] = pandas.to_datetime(df["order_date"])
    df["month"] = df["order_date"].dt.month_name()
    df["hour"] = df["order_date"].dt.hour
    df["value"] = df["quantity_ordered"] * df["price_each"]
    return df

with layout_column_wrap(width=1/2):
    with ui.navset_card_underline(id="tab", footer=ui.input_numeric("n", "Number of Items", 5, min=2, max=20)):  
        with ui.nav_panel("Top Selling Products"):
            @render_plotly
            def plot_top_sellers():
                df = dat()
                top_sales = df.groupby('product')['quantity_ordered'].sum().nlargest(input.n()).reset_index() 
                fig = px.bar(top_sales, x='product', y="quantity_ordered", title=f"Top {input.n()} Products by Quantity Ordered")
                return fig

        with ui.nav_panel("Top Seller Value($)"):
            @render_plotly
            def plot_top_sellers_value():
                df = dat()
                top_sales = df.groupby('product')['value'].sum().nlargest(input.n()).reset_index() 
                fig = px.bar(top_sales, x='product', y="value", title=f"Top {input.n()} Products by Value")
                return fig

        with ui.nav_panel("Lowest Sellers"):
            @render_plotly
            def plot_lowest_sellers():
                df = dat()
                top_sales = df.groupby('product')['quantity_ordered'].sum().nsmallest(input.n()).reset_index() 
                fig = px.bar(top_sales, x='product', y="quantity_ordered", title=f"Top {input.n()} Products by Quantity Ordered")
                return fig

        with ui.nav_panel("Lowest Seller Value($)"):
            @render_plotly
            def plot_lowest_sellers_value():
                df = dat()
                top_sales = df.groupby('product')['value'].sum().nsmallest(input.n()).reset_index() 
                fig = px.bar(top_sales, x='product', y="value", title=f"Top {input.n()} Products by Value")
                return fig
            
    with ui.card():
        ui.card_header("Sales by Time of Day Heatmap")
        @render.plot
        def plot_sales_by_time():
            df = dat()
            sales_by_hour = df['hour'].value_counts().reindex(np.arange(0,24), fill_value=0)#.reset_index()
            heatmap_data = sales_by_hour.values.reshape(24, 1)  # Reshape for heatmap
            sns.heatmap(heatmap_data, annot=True, fmt="d", cmap="YlGnBu", cbar=False,
                        xticklabels=[],
                        yticklabels=[f"{hour}:00" for hour in range(24)])
            plt.title("Number of Orders by Hour of Day")
            plt.ylabel("Hour of Day")
            plt.xlabel("Order Count")

with ui.card():
    ui.card_header("Sales by location Map")
    "Content Here"

with ui.card():
    ui.card_header("Sales by City in 2023")
    with ui.layout_sidebar():  
        with ui.sidebar(bg="#f8f8f8", open='closed'): 
            ui.input_selectize(
                "city",
                "Select a city :",
                [
                    "Dallas (TX)",
                    "Boston (MA)",
                    "Los Angeles (CA)",
                    "San Francisco (CA)",
                    "Seattle (WA)",
                    "Atlanta (GA)",
                    "New York City (NY)",
                    "Portland (OR)",
                    "Austin (TX)",
                    "Portland (ME)",
                ],
                multiple=False,
                selected='Boston (MA)'
            )


        @render_plotly
        def sales_over_time():
            df = dat()

            sales = df.groupby(["city", "month"])["quantity_ordered"].sum().reset_index()
            sales_by_city = sales[sales["city"] == input.city()]
            month_order = calendar.month_name[1:]  # Get month names from January to December
            fig = px.bar(
                sales_by_city,
                x="month",
                y="quantity_ordered",
                title=f"SalesOver Time -- {input.city()}",
                category_orders={"month": month_order},
            )
            return fig

with ui.card():
    ui.card_header("Sample Sales Data")

    @render.data_frame
    def sample_sales_data():
        return dat().head(50)
