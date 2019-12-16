"""Graphing functions for the MPV web app."""

from bokeh.models import ColumnDataSource, HoverTool, Legend
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.transform import dodge


def height_climbed(cursor, userid, units):
    """Compute height climbed and make graph."""
    # Get the years for current user
    years = get_years(cursor, userid)
    # Set the vars for ticks with no heights
    year_height = dict()
    defaults = {"Aid": 75, "Boulder": 8, "Ice": 100, "Mixed": 100,
                "Snow": 200, "Sport": 75, "TR": 50, "Trad": 150}
    # Get ticks for each year
    for year in years:
        select = """SELECT `height`, `type`.`type` FROM `%s`
                 JOIN `mpv`.`type` ON `mpv`.`type`.`id` = `%s`.`type`
                 WHERE YEAR(`date`) = '%s';"""
        cursor.execute(select, (userid, userid, year))
        ticks = cursor.fetchall()
        # Loop through all ticks for current year
        for row in ticks:
            # Check if height is undefined, add a variable amount
            if row[0] is None:
                for key in defaults:
                    if row[1] == key:
                        year_height = add_to_year(year,
                                                  defaults[key], year_height)
            # Otherwise add it to the yearly total
            else:
                year_height = add_to_year(year, row[0], year_height)

    # Calculate total height
    total_height = int()
    for year in year_height.keys():
        total_height += year_height[year]

    years = list(year_height.keys())
    height = list(year_height.values())

    # Convert height to meters if required
    if units == "meters":
        for i in range(0, len(height)):
            height[i] = int(height[i] / 3.28)
        total_height = int(total_height / 3.28)

    # Add commas to the total height
    total_height = format(total_height, ',d')

    # Generate a graph
    TOOLTIPS = [
        ("Year", "@x"),
        ("Height", "@y{0,0}")
    ]
    tools = "reset,pan,wheel_zoom,box_zoom,save"
    plot = figure(title="Height Per Year", plot_height=400,
                  sizing_mode='scale_both', tools=tools)
    plot.line(years, height, line_width=2, line_color="blue")
    plot.circle(years, height, size=8, fill_color="white", line_color="blue")
    # Set label for selected units
    if units == "meters":
        plot.yaxis.axis_label = 'Meters'
    else:
        plot.yaxis.axis_label = 'Feet'
    plot.add_tools(HoverTool(tooltips=TOOLTIPS, mode='vline'))
    plot.toolbar.active_drag = None
    script, div = components(plot)

    return {"total": total_height, "plot": [script, div]}


def pitches_climbed(cursor, userid):
    """Pitches, routes, problems graph and info."""
    # Get all-time pitch count
    select = "SELECT SUM(`pitches`) FROM `%s`;"
    cursor.execute(select, (userid,))
    sum = cursor.fetchone()

    # Get data for routes/pitches/problems graph
    years = get_years(cursor, userid)

    routes = list()
    select = """SELECT COUNT('name') from `%s`
                JOIN `mpv`.`type` ON `mpv`.`type`.`id` = `%s`.`type`
                WHERE YEAR(`date`) = '%s' AND `type`.`type` != 'Boulder';"""
    for year in years:
        # Get total routes climbed for each year
        cursor.execute(select, (userid, userid, year))
        routes.append(cursor.fetchone())

    pitches = list()
    problems = list()
    types = ["!= 'Boulder';", "= 'Boulder';"]
    select = """SELECT SUM(`pitches`) FROM `%s`
                JOIN `mpv`.`type` ON `mpv`.`type`.`id` = `%s`.`type`
                WHERE YEAR(`date`) = '%s' AND `type`.`type` %s"""

    # Loop through years for each type
    for type in types:
        for year in years:
            # Get all pitches/problems for year
            cursor.execute(select % (userid, userid, year, type))
            if type == "= 'Boulder';":
                problems.append(cursor.fetchone())
            else:
                tmp = cursor.fetchone()
                pitches.append(tmp[0])

    # Generate graph
    TOOLTIPS = [
        ("Year", "@years"),
        ("Routes", "@routes{0,0}"),
        ("Pitches", "@pitches{0,0}"),
        ("Problems", "@problems{0,0}")
    ]
    data = {'years': years,
            'routes': routes,
            'pitches': pitches,
            'problems': problems}

    tools = "reset,pan,wheel_zoom,box_zoom,save"

    plot = figure(title="Pitches / Routes / Problems Per Year",
                  plot_height=400, sizing_mode='stretch_both', tools=tools)

    re1 = plot.vbar(x=dodge('years', -0.211, range=plot.x_range),
                    top='pitches', bottom=0, width=0.4, color="blue",
                    legend_label="Pitches", source=ColumnDataSource(data=data))
    plot.vbar(x=dodge('years', -0.211, range=plot.x_range), top='routes',
              bottom=0, width=0.4, color="red", legend_label="Routes",
              source=ColumnDataSource(data=data))
    re2 = plot.vbar(x=dodge('years', 0.211, range=plot.x_range),
                    top='problems', bottom=0, width=0.4, color="orange",
                    legend_label="Problems",
                    source=ColumnDataSource(data=data))
    plot.yaxis.axis_label = 'Amount'
    plot.toolbar.active_drag = None
    legend = Legend(location="top_left", margin=0, label_text_font_size="8pt",
                    label_text_baseline="bottom", glyph_height=6,
                    glyph_width=6, click_policy="hide", label_height=4)
    plot.add_layout(legend)
    plot.add_tools(HoverTool(tooltips=TOOLTIPS, renderers=[re1, re2]))
    script, div = components(plot)

    return {"total": sum[0], "plot": [script, div]}


def get_years(cursor, userid):
    """Get all years for user."""
    select = "SELECT DISTINCT YEAR(`date`) FROM `%s`"
    cursor.execute(select, (userid,))
    years = cursor.fetchall()
    # Format the get_years
    for i in range(0, len(years)):
        years[i] = years[i][0]
    return years


def add_to_year(year, height, year_height):
    """Add height to a given year."""
    if year in year_height:
        year_height[year] = year_height[year] + height
    else:
        year_height.update({year: height})
    return year_height
