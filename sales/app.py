import pandas
import plotly.express as px
import calendar
from pathlib import Path
from shiny import reactive
from shiny.express import render, input, ui
from shinywidgets import render_plotly

ui.page_opts(title="Sales Dashboard -- Video 1 of 5", fillable=False)

@reactive.calc
def dat():
    infile = Path(__file__).parent / "data/sales.csv"
    # input.n()  # Ensure that this reactive depends on the input value
    df = pandas.read_csv(infile)
    df["order_date"] = pandas.to_datetime(df["order_date"])
    df["month"] = df["order_date"].dt.month_name()
    return df

with ui.card():  
    ui.card_header("Top Selling Products")

    with ui.layout_sidebar():  
        with ui.sidebar(bg="#f8f8f8", open='closed'): 
            ui.input_numeric("n", "Number of Items", 5, min=2, max=20)

        @render_plotly
        def plot1():
            df = dat()
            #top_sales = df.groupby('product')['quantity_ordered'].nlargest(5).reset_index()
            top_sales = df.groupby('product')['quantity_ordered'].sum().nlargest(input.n()).reset_index() 
            fig = px.histogram(top_sales, x='product', y="quantity_ordered", title=f"Top {input.n()} Products by Quantity Ordered")
            return fig
with ui.navset_card_underline(id="tab"):  
    with ui.nav_panel("A"):
        "Panel A content"

    with ui.nav_panel("B"):
        "Panel B content"

    with ui.nav_panel("C"):
        "Panel C content"

    with ui.nav_menu("Other links"):
        with ui.nav_panel("D"):
            "Page D content"

        "----"
        "Description:"
        with ui.nav_control():
            ui.a("Shiny", href="https://shiny.posit.co", target="_blank")

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
        #    print(list(df.city.unique()))

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
