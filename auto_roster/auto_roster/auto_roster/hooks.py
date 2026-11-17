from . import __version__ as app_version

app_name = "auto_roster"
app_title = "Auto Roster Engine"
app_publisher = "System"
app_description = "Fully automated 24/48hr shift engine"
app_email = "admin@localhost"
app_license = "mit"

# Fires instantly when the module is installed
after_install = "auto_roster.setup.install.after_install"

# Fires every night at midnight to extend the calendar
scheduler_events = {
    "daily": [
        "auto_roster.tasks.engine.plot_rosters"
    ]
}