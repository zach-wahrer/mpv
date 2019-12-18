"""Graphing functions for the MPV web app."""

import statistics
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.transform import dodge

TOOLS = "reset,pan,wheel_zoom,box_zoom,save"


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
    plot = figure(title="Height Per Year", plot_height=400,
                  sizing_mode='scale_both', tools=TOOLS)
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
        ("Pitches", "@pitches{0,0}"),
        ("Routes", "@routes{0,0}"),
        ("Problems", "@problems{0,0}")
    ]
    data = {'years': years,
            'routes': routes,
            'pitches': pitches,
            'problems': problems}

    plot = figure(title="Pitches / Routes / Problems Per Year",
                  plot_height=400, sizing_mode='stretch_both', tools=TOOLS)

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
    plot.legend.location = "top_left"
    plot.legend.margin = 0
    plot.legend.label_text_font_size = "8pt"
    plot.legend.label_text_baseline = "bottom"
    plot.legend.glyph_height = 6
    plot.legend.glyph_width = 6
    plot.legend.click_policy = "hide"
    plot.legend.label_height = 4
    plot.add_tools(HoverTool(tooltips=TOOLTIPS, renderers=[re1, re2]))
    script, div = components(plot)

    return {"total": sum[0], "plot": [script, div]}


def grade_scatter(cursor, userid, type):
    """Create grade scatter graph."""
    # Get grades ticked each year
    years = get_years(cursor, userid)
    grades = get_grades(cursor, userid, type)
    grade_data = list()
    year_data = list()
    year_mean = list()
    year_mode = list()
    year_mean_year = list()
    year_mode_year = list()
    select = """SELECT `code`.`id`, `code`.`code` FROM `%s`
            JOIN `mpv`.`type` ON `mpv`.`type`.`id` = `%s`.`type`
            JOIN `mpv`.`code` ON `mpv`.`code`.`id` = `%s`.`code`
            WHERE YEAR(`date`) = '%s' AND `type`.`type` = '%s'
            ORDER BY `code`.`id` ASC;"""
    for year in years:
        cursor.execute(select % (userid, userid, userid, year, type))
        tmp_grades = list()
        for row in cursor.fetchall():
            grade_data.append(row[1])
            year_data.append(year)
            tmp_grades.append(row[0])

        # Get mode/mean grade ticked for year
        if tmp_grades:
            mode = max(tmp_grades, key=tmp_grades.count)
            mean = statistics.median(tmp_grades)
            query = """SELECT `code` FROM `code`
                    ORDER BY ABS(`code`.`id` - '%s') LIMIT 1;"""
            cursor.execute(query % (mode,))
            for row in cursor.fetchone():
                year_mode.append(row)
                year_mode_year.append(year)
            cursor.execute(query % (mean,))
            for row in cursor.fetchone():
                year_mean.append(row)
                year_mean_year.append(year)

    # Check for MP no code bug, return nothing if so
    if not grade_data:
        return False

    # Generate graph
    data = {"years": year_data,
            "grades": grade_data}
    mean_mode = {"year_mode_year": year_mode_year,
                 "year_mean_year": year_mean_year,
                 "year_mode": year_mode,
                 "year_mean": year_mean}
    TOOLTIPS = [
        ("Year:", "@year_mode_year"),
        ("Most Ticked:", "@year_mode"),
        ("Average Grade:", "@year_mean")
    ]

    plot = figure(title=(type + " Grades By Year"), y_range=grades,
                  sizing_mode='stretch_both', tools=TOOLS)
    plot.scatter('years', 'grades', size=14, alpha=0.2,
                 source=ColumnDataSource(data=data))
    # Don't draw mean/mode if only 1 year of data
    if len(year_mode_year) > 1:
        re = plot.line("year_mode_year", "year_mode", line_width=2,
                       line_color="red", legend_label="Most Ticked",
                       source=ColumnDataSource(data=mean_mode))
        plot.line("year_mean_year", "year_mean", line_width=2,
                  line_color="orange", legend_label="Average Grade",
                  source=ColumnDataSource(data=mean_mode))
        plot.add_tools(HoverTool(tooltips=TOOLTIPS, mode='vline',
                                 renderers=[re]))
        plot.legend.location = "top_left"
        plot.legend.margin = 0
        plot.legend.label_text_font_size = "8pt"
        plot.legend.label_text_baseline = "bottom"
        plot.legend.glyph_height = 6
        plot.legend.glyph_width = 6
        plot.legend.click_policy = "hide"
        plot.legend.label_height = 4
    plot.toolbar.active_drag = None
    script, div = components(plot)

    return [script, div]


def get_grades(cursor, userid, type):
    """Get all grades user has ticked of specified type."""
    select = """SELECT DISTINCT `code`.`code`, `code`.`id` FROM `%s`
             JOIN `mpv`.`type` ON `mpv`.`type`.`id` = `%s`.`type`
             JOIN `mpv`.`code` ON `mpv`.`code`.`id` = `%s`.`code`
             WHERE `type`.`type` = '%s' ORDER BY `code`.`id` ASC;"""
    cursor.execute(select % (userid, userid, userid, type))
    grades = cursor.fetchall()
    # Format the grades
    for i in range(0, len(grades)):
        grades[i] = grades[i][0]
    return grades


def get_years(cursor, userid):
    """Get all years for user."""
    select = "SELECT DISTINCT YEAR(`date`) FROM `%s`;"
    cursor.execute(select, (userid,))
    years = cursor.fetchall()
    # Format the get_years
    for i in range(0, len(years)):
        years[i] = years[i][0]
    return years


def get_types(cursor, userid):
    """Get all of the types of climbing a user did."""
    select = """SELECT DISTINCT `type`.`type` FROM `%s`
                JOIN `mpv`.`type` ON `mpv`.`type`.`id` = `%s`.`type`;"""
    cursor.execute(select, (userid, userid))
    types = cursor.fetchall()
    # Format the types
    for i in range(0, len(types)):
        types[i] = types[i][0]
    return types


def add_to_year(year, height, year_height):
    """Add height to a given year."""
    if year in year_height:
        year_height[year] = year_height[year] + height
    else:
        year_height.update({year: height})
    return year_height
