from tkinter import font

import pandas
import plotly.express as px
import calendar
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

import folium
from folium.plugins import HeatMap

from pathlib import Path
from shiny import reactive
from shiny.express import render, input, ui
from shiny.ui import layout_column_wrap, layout_columns
from shinywidgets import render_plotly, render_altair, render_widget


import altair as alt

ui.tags.style("""
        .header-container {
            display: flex;  
            align-items: center;
            justify-content: center;
            height: 80px;
        }
        .logo-container {
            margin-right: 5px;
            height: 100%;
            display: flex;
            padding: 20px;
        }

        .logo-container img {
            height: 50px !important;
        }

        .title-container h2{
            color: white;
            background-color: #5DADE2;
            padding: 10px;
            border-radius: 5px;
            margin: 0;
        } 

        body {
            background-color: #5DADE2;     
        }

        .modebar {
            display: none;
        }

        .custom-sidebar {
            background-color: #f8f8f8;
            padding: 15px;
            border-radius: 5px;
        }

  """)

FONT_COLOR = "#4C78A8"
FONT_TYPE = "Arial"


def style_plotly_chart(fig, yaxis_title):
    fig.update_layout(
        xaxis_title="",
        yaxis_title=yaxis_title,
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        coloraxis_showscale=False,
        font=dict(family=FONT_TYPE, size=12, color=FONT_COLOR),
        # config={"displayModeBar": False}
        # config=dict(
        #             displayModeBar=False
        #         )
    )

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    return fig


ui.page_opts(window_title="Sales Dashboard", fillable=False)


@reactive.calc
def dat():
    infile = Path(__file__).parent / "data/sales.csv"
    df = pandas.read_csv(infile)
    df["order_date"] = pandas.to_datetime(df["order_date"])
    df["month"] = df["order_date"].dt.month_name()
    df["hour"] = df["order_date"].dt.hour
    df["value"] = df["quantity_ordered"] * df["price_each"]
    return df


with ui.div(class_="header-container"):
    with ui.div(class_="logo-container"):

        @render.image
        def image():
            here = Path(__file__).parent.parent
            img = {"src": here / "images/shiny-logo.png"}
            return img

    with ui.div(class_="title-container"):
        ui.h2("Sales Dashboard")

with layout_column_wrap(width=1 / 2):
    with ui.navset_card_underline(
        id="tab", footer=ui.input_numeric("n", "Number of Items", 5, min=2, max=20)
    ):
        with ui.nav_panel("Top Selling Products"):

            @render_plotly
            def plot_top_sellers():
                df = dat()
                top_sales = (
                    df.groupby("product")["quantity_ordered"]
                    .sum()
                    .nlargest(input.n())
                    .reset_index()
                )
                fig = px.bar(
                    top_sales,
                    x="product",
                    y="quantity_ordered",
                    color="quantity_ordered",
                    color_continuous_scale="Blues",
                )

                fig = style_plotly_chart(
                    fig, f"Top {input.n()} Products by Quantity Ordered"
                )
                return fig

        with ui.nav_panel("Top Seller Value($)"):

            @render_plotly
            def plot_top_sellers_value():
                df = dat()
                top_sales = (
                    df.groupby("product")["value"]
                    .sum()
                    .nlargest(input.n())
                    .reset_index()
                )
                fig = px.bar(
                    top_sales,
                    x="product",
                    y="value",
                    color="value",
                    color_continuous_scale="Blues",
                )

                fig = style_plotly_chart(fig, "Ordered Value ($)")
                return fig

        with ui.nav_panel("Lowest Sellers"):

            @render_plotly
            def plot_lowest_sellers():
                df = dat()
                top_sales = (
                    df.groupby("product")["quantity_ordered"]
                    .sum()
                    .nsmallest(input.n())
                    .reset_index()
                )
                fig = px.bar(
                    top_sales,
                    x="product",
                    y="quantity_ordered",
                    color="quantity_ordered",
                    color_continuous_scale="Reds",
                )
                fig = style_plotly_chart(
                    fig, f"Bottom {input.n()} Products by Quantity Ordered"
                )
                return fig

        with ui.nav_panel("Lowest Seller Value($)"):

            @render_plotly
            def plot_lowest_sellers_value():
                df = dat()
                top_sales = (
                    df.groupby("product")["value"]
                    .sum()
                    .nsmallest(input.n())
                    .reset_index()
                )
                fig = px.bar(
                    top_sales,
                    x="product",
                    y="value",
                    color="value",
                    color_continuous_scale="Reds",
                )

                fig = style_plotly_chart(fig, f"Bottom {input.n()} Products by Value")
                return fig

    with ui.card():
        ui.card_header("Sales by Time of Day Heatmap")

        @render.plot
        def plot_sales_by_time():
            df = dat()
            sales_by_hour = (
                df["hour"].value_counts().reindex(np.arange(0, 24), fill_value=0)
            )  # .reset_index()
            heatmap_data = sales_by_hour.values.reshape(24, 1)  # Reshape for heatmap
            sns.heatmap(
                heatmap_data,
                annot=True,
                fmt="d",
                cmap="Blues",  # sns.light_palette(FONT_COLOR, as_cmap=True),
                cbar=False,
                xticklabels=[],
                yticklabels=[f"{hour}:00" for hour in range(24)],
            )
            #            plt.title("Number of Orders by Hour of Day")
            plt.xlabel("Order Count", color=FONT_COLOR, fontname=FONT_TYPE)
            plt.ylabel("Hour of Day", color=FONT_COLOR, fontname=FONT_TYPE)

            plt.yticks(color=FONT_COLOR, fontname=FONT_TYPE)
            plt.yticks(color=FONT_COLOR, fontname=FONT_TYPE)


with ui.card():
    ui.card_header("Sales by location Map")

    @render.ui
    def plot_sales_map():
        df = dat()
        heatmap_data = df[["lat", "long", "quantity_ordered"]].values
        map = folium.Map(
            location=[37.0902, -95.7129], zoom_start=4
        )  # Центрируем карту на США
        # HeatMap(heatmap_data, radius=15).add_to(map)
        # print(map._repr_html_())  # Возвращаем HTML представление карты
        # print(heatmap_data)
        # HeatMap(heatmap_data).add_to(map)

        blue_gradient = {
            0.0: "#477F8E",
            0.2: "#3A668B",
            0.4: "#2E4E88",
            0.6: "#213586",
            0.8: "#141C85",
            1.0: "#070484",
        }
        HeatMap(heatmap_data, gradient=blue_gradient).add_to(map)
        return map


with ui.card():
    ui.card_header("Sales by City in 2023")
    with ui.layout_sidebar(class_="custom-sidebar"):
        with ui.sidebar(bg="#f8f8f8", open="closed"):
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
                selected="Boston (MA)",
            )

        @render_widget
        def sales_over_time_altair():
            df = dat()
            # Group the data by city and month, then sum the quantities ordered
            sales = (
                df.groupby(["city", "month"])["quantity_ordered"].sum().reset_index()
            )

            # Filter the sales data to only include the selected city
            sales_by_city = sales[sales["city"] == input.city()]

            # Define the order of months
            month_orders = list(calendar.month_name)[1:]

            font_props = alt.Axis(
                labelFont="Arial",
                labelColor=FONT_COLOR,
                titleFont="Arial",
                titleColor=FONT_COLOR,
                tickSize=0,
                labelAngle=0,
            )
            # Create the bar chart
            chart = (
                alt.Chart(sales_by_city)
                .mark_bar(color="#3485BF")
                .encode(
                    x=alt.X("month", sort=month_orders, title="Month", axis=font_props),
                    y=alt.Y(
                        "quantity_ordered", title="Quantity Ordered", axis=font_props
                    ),
                    tooltip=["month", "quantity_ordered"],
                )
                .properties(title=alt.Title(f"Sales over Time -- {input.city()}"))
                .configure_axis(grid=False)
                .configure_title(font="Arial", color=FONT_COLOR)
            )

            return chart


with ui.card():
    ui.card_header("Sample Sales Data")

    @render.data_frame
    def sample_sales_data():
        # return dat().head(50)
        #        return render.DataGrid(dat().head(100), filters=True)
        return render.DataTable(dat().head(100), selection_mode="row", filters=True)
