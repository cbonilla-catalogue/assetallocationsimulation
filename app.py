import dash
import dash_snapshots
import os


app = dash.Dash(__name__, suppress_callback_exceptions = True)

app.index_string = """<!DOCTYPE html>
<html>
    <head>
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-7E8827JN8S"></script>
        <script>
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', 'G-7E8827JN8S');
        </script>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>"""

# Use DATABASE_URL as provided by Dash Enterprise
# If on Windows use the default Postgres URL
# Fallback to SQLite on Mac and Linux
# On Windows you’ll need to download and run Postgres as built in SQLite is not supported
os.environ["SNAPSHOT_DATABASE_URL"] = os.environ.get("DATABASE_URL", "postgres://username:password@127.0.0.1:5432") if os.name == 'nt' else os.environ.get("DATABASE_URL", "sqlite:///snapshot-dev.db")

snap = dash_snapshots.DashSnapshots(app,permissions='creator')
