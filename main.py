from turtle import color
from numpy import column_stack
import pandas as pd

from bokeh.plotting import figure
from bokeh.io import output_file, show
from bokeh.models import NumeralTickFormatter, DatetimeTickFormatter
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource
from bokeh.layouts import layout
from bokeh.models import RangeSlider

data = pd.read_csv('data/nyc_tlc_yellow_trips_2018_subset_1.csv')

# filter out outliers


def cap_data(df):
    for col in df.columns:
        print("capping the ", col)
        if (((df[col].dtype) == 'float64') | ((df[col].dtype) == 'int64')):
            percentiles = df[col].quantile([0.01, 0.99]).values
            df[col][df[col] <= percentiles[0]] = percentiles[0]
            df[col][df[col] >= percentiles[1]] = percentiles[1]
        else:
            df[col] = df[col]
    return df


data = cap_data(data)

# only tip counted data
tip_data = data.loc[data["tip_amount"] > 0.01]

# format the dates

# tip_data["pickup_datetime"] = pd.to_datetime(tip_data["pickup_datetime"])
# to handle SettingWithCopyWarning : dataframe.copy() used
date_tip = tip_data.copy()

date_tip['pickup_datetime'] = pd.to_datetime(
    tip_data['pickup_datetime'])


# split data to vendors
vendor1 = tip_data.loc[tip_data["vendor_id"] == 1]
vendor2 = tip_data.loc[tip_data["vendor_id"] == 2]

source1 = ColumnDataSource(data=vendor1)
source2 = ColumnDataSource(data=vendor2)

fig = figure(x_axis_label="Trip Distance (mi)", y_axis_label="Tip Amount($)",
             title="Trip distances and Tip amount by Vendor type")
fig.circle(x="trip_distance", y="tip_amount",
           color="blue", legend_label="vendor1", source=source1)
fig.circle(x="trip_distance", y="tip_amount",
           color="red", legend_label="vendor2", source=source2)

# Legend Title and Location
fig.legend.title = "Vendors"
fig.legend.location = "bottom_right"

# Displaying an interactive legend
fig.legend.click_policy = "hide"
y_slider = RangeSlider(title="Tip Amount($)", start=0,
                       end=12, value=(0, 12), step=0.5)
y_slider.js_link("value", fig.y_range, "start", attr_selector=0)
y_slider.js_link("value", fig.y_range, "end", attr_selector=1)
fig.yaxis[0].formatter = NumeralTickFormatter(format="$0.0a")

# group by pickup date
# date_tip = date_tip.groupby("pickup_datetime", as_index=False)[
#    ["passenger_count", "trip_distance", "tip_amount", "total_amount"]].mean()

source3 = ColumnDataSource(data=date_tip)
TOOLTIPS = [("Distance (mi)", "@trip_distance{(0.0)}"),
            ("Tip Amount", "@tip_amount{($ 0.00 a)}"),
            ("Total Amount", "@total_amount{($ 0.00 a)}")]
fig_two = figure(x_axis_label="Pickup Date",
                 y_axis_label="Tip Amount($)", tooltips=TOOLTIPS, title="Tip amount by Date")
fig_two.dot(x="pickup_datetime",
            y="tip_amount", size=10, source=source3)
fig_two.xaxis[0].formatter = DatetimeTickFormatter(months="%b %Y")
fig_two.yaxis[0].formatter = NumeralTickFormatter(format="$0.0a")

# fig_two.width = 1450
# fig_two.height = 900
output_file(filename="index.html")
show(row(layout([fig, y_slider]), fig_two))
