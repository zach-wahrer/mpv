"""Graphing functions for the MPV web app."""

import statistics
from bokeh.embed import components
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure
from bokeh.transform import dodge
from mysql.connector import MySQLConnection

TOOLS = "reset,pan,wheel_zoom,box_zoom,save"


def height_climbed(cursor: MySQLConnection.cursor, mp_user_id: int, units: str) -> dict:
    """Compute height climbed and return a graph."""
    # Get the years the current user user was active
    years = get_years(cursor, mp_user_id)
    # Set vars for ticks with no heights
    year_height = dict()
    defaults = {"Aid": 75, "Boulder": 8, "Ice": 100, "Mixed": 100,
                "Snow": 200, "Sport": 75, "TR": 50, "Trad": 150}
    # Get ticks for each year
    for year in years:
        select = """SELECT `height`, `type`.`type` FROM `%s`
                 JOIN `mpv`.`type` ON `mpv`.`type`.`id` = `%s`.`type`
                 WHERE YEAR(`date`) = '%s';"""
        cursor.execute(select, (mp_user_id, mp_user_id, year))
        ticks = cursor.fetchall()
        # Check that climbs have heights, set defualts if not
        for row in ticks:
            if row[0] is None:
                for key in defaults:
                    if row[1] == key:
                        year_height = add_to_year(year,
                                                  defaults[key], year_height)
            else:
                year_height = add_to_year(year, row[0], year_height)

    # Calculate total height climbed
    total_height = int()
    for year in year_height.keys():
        total_height += year_height[year]

    height = list(year_height.values())

    # Convert height to meters if required
    if units == "meters":
        for i in range(0, len(height)):
            height[i] = int(height[i] / 3.28)
        total_height = int(total_height / 3.28)

    # Add commas to the total height output
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
    if units == "meters":
        plot.yaxis.axis_label = 'Meters'
    else:
        plot.yaxis.axis_label = 'Feet'
    plot.add_tools(HoverTool(tooltips=TOOLTIPS, mode='vline'))
    plot.toolbar.active_drag = None
    script, div = components(plot)

    return {"total": total_height, "plot": [script, div]}


def pitches_climbed(cursor: MySQLConnection.cursor, mp_user_id: int) -> dict:
    """Pitches, routes, problems graph and info."""
    pitches = list()
    routes = list()
    problems = list()

    # Get all-time pitch count
    select = "SELECT SUM(`pitches`) FROM `%s`;"
    cursor.execute(select, (mp_user_id,))
    sum = cursor.fetchone()

    # Get the years the current user user was active
    years = get_years(cursor, mp_user_id)

    # Get total routes climbed for each year
    select = """SELECT COUNT('name') from `%s`
                JOIN `mpv`.`type` ON `mpv`.`type`.`id` = `%s`.`type`
                WHERE YEAR(`date`) = '%s' AND `type`.`type` != 'Boulder';"""
    for year in years:
        cursor.execute(select, (mp_user_id, mp_user_id, year))
        routes.append(cursor.fetchone())

    # Get all pitches/problems for a given year
    types = ["!= 'Boulder';", "= 'Boulder';"]
    select = """SELECT SUM(`pitches`) FROM `%s`
                JOIN `mpv`.`type` ON `mpv`.`type`.`id` = `%s`.`type`
                WHERE YEAR(`date`) = '%s' AND `type`.`type` %s"""
    for type in types:
        for year in years:
            cursor.execute(select % (mp_user_id, mp_user_id, year, type))
            if type == "= 'Boulder';":
                problems.append(cursor.fetchone())
            else:
                tmp = cursor.fetchone()
                pitches.append(tmp[0])

    # Generate the graph
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


def grade_scatter(cursor: MySQLConnection.cursor, mp_user_id: int, type: str) -> list:
    """Create grade scatter graph."""
    # Get grades ticked each year
    years = get_years(cursor, mp_user_id)
    grades = get_grades(cursor, mp_user_id, type)
    grade_data = list()
    year_data = list()
    mean_values = list()
    mode_values = list()
    mean_years = list()
    mode_years = list()
    select = """SELECT `code`.`id`, `code`.`code` FROM `%s`
            JOIN `mpv`.`type` ON `mpv`.`type`.`id` = `%s`.`type`
            JOIN `mpv`.`code` ON `mpv`.`code`.`id` = `%s`.`code`
            WHERE YEAR(`date`) = '%s' AND `type`.`type` = '%s'
            ORDER BY `code`.`id` ASC;"""
    for year in years:
        tmp_grades = list()
        cursor.execute(select % (mp_user_id, mp_user_id, mp_user_id, year, type))
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
                mode_values.append(row)
                mode_years.append(year)
            cursor.execute(query % (mean,))
            for row in cursor.fetchone():
                mean_values.append(row)
                mean_years.append(year)

    # Check for MP no code bug, return nothing if so
    if not grade_data:
        return False

    # Generate graph
    data = {"years": year_data,
            "grades": grade_data}
    mean_mode = {"mode_years": mode_years,
                 "mean_years": mean_years,
                 "mode_values": mode_values,
                 "mean_values": mean_values}
    TOOLTIPS = [
        ("Year:", "@mode_years"),
        ("Most Ticked:", "@mode_values"),
        ("Average Grade:", "@mean_values")
    ]

    plot = figure(title=(type + " Grades By Year"), y_range=grades,
                  sizing_mode='stretch_both', tools=TOOLS)
    plot.scatter('years', 'grades', size=14, alpha=0.2,
                 source=ColumnDataSource(data=data))
    # Don't draw mean/mode if only 1 year of data
    if len(mode_years) > 1:
        re = plot.line("mode_years", "mode_values", line_width=2,
                       line_color="red", legend_label="Most Ticked",
                       source=ColumnDataSource(data=mean_mode))
        plot.line("mean_years", "mean_values", line_width=2,
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


def get_grades(cursor: MySQLConnection.cursor, mp_user_id: int, type: str) -> list:
    """Get all grades user has ticked of specified type."""
    select = """SELECT DISTINCT `code`.`code`, `code`.`id` FROM `%s`
             JOIN `mpv`.`type` ON `mpv`.`type`.`id` = `%s`.`type`
             JOIN `mpv`.`code` ON `mpv`.`code`.`id` = `%s`.`code`
             WHERE `type`.`type` = '%s' ORDER BY `code`.`id` ASC;"""
    cursor.execute(select % (mp_user_id, mp_user_id, mp_user_id, type))
    grades = cursor.fetchall()
    # Format the grades
    for i in range(0, len(grades)):
        grades[i] = grades[i][0]
    return grades


def get_years(cursor: MySQLConnection.cursor, mp_user_id: int) -> list:
    """Get all years a user was active."""
    select = "SELECT DISTINCT YEAR(`date`) FROM `%s`;"
    cursor.execute(select, (mp_user_id,))
    years = cursor.fetchall()
    # Format the years
    for i in range(0, len(years)):
        years[i] = years[i][0]
    years.sort()
    return years


def get_types(cursor: MySQLConnection.cursor, mp_user_id: int) -> list:
    """Get all of the types of climbing a user has done."""
    select = """SELECT DISTINCT `type`.`type` FROM `%s`
                JOIN `mpv`.`type` ON `mpv`.`type`.`id` = `%s`.`type`;"""
    cursor.execute(select, (mp_user_id, mp_user_id))
    types = cursor.fetchall()
    # Format the types
    for i in range(0, len(types)):
        types[i] = types[i][0]
    return types


def add_to_year(year: int, height: int, year_height: dict) -> dict:
    """Add height to a given year."""
    if year in year_height:
        year_height[year] = year_height[year] + height
    else:
        year_height.update({year: height})
    return year_height
