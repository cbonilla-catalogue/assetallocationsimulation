import dash
from dash.dependencies import Input, Output
import dash_design_kit as ddk
from dash import dcc, html, dash_table
import dash_enterprise_auth
import dash_user_analytics

from app import app, snap
import pages
server = app.server
celery_instance = snap.celery_instance

app.layout = ddk.App(show_editor=False, children=[
    ddk.Header([
        dcc.Link(
            ddk.Logo(src=app.get_relative_path('/assets/logo.png')),
            href=app.get_relative_path('/')
        ),
        ddk.Title('Analytics'),
        ddk.Menu([
            #dcc.Link(
            #    href=app.get_relative_path('/'),
            #    children='Home'
            #),
            dcc.Link(
                href=app.get_relative_path('/'),
                children='Asset Allocation Builder'
            ),
            #dcc.Link(
            #    href=app.get_relative_path('/addeparAssetAllocation'),
            #    children='Addepar Portfolio Review'
            #),
            dcc.Link(
                href=app.get_relative_path('/archive'),
                children='Archive'
            )
        ])
    ]),
    dcc.Location(id='url'),
    html.Div(id='content')
])

analytics = dash_user_analytics.DashUserAnalytics(
    app, automatic_routing=False
)

@app.callback(
    Output('content', 'children'),
    [Input('url', 'pathname')])
def display_content(pathname):
    page_name = app.strip_relative_path(pathname)
    #if not page_name:  # None or ''
    #    return pages.home.layout()
    if not page_name:  # None or ''
        return pages.assetAllocation.layout()
    elif page_name == 'assetAllocation':
        return pages.assetAllocation.layout()
    elif pathname.endswith('addeparAssetAllocation') and (dash_enterprise_auth.get_username() == 'carlos.bonilla_insigneo.com' or dash_enterprise_auth.get_username() == 'miguel.reyes_insigneo.com' or dash_enterprise_auth.get_username() == 'sofia.berrosteguieta_insigneo.com'):
        return pages.addeparAssetAllocation.layout()
    elif page_name == 'archive':
        return pages.archive.layout()
    elif page_name.startswith("snapshot-"):
        return pages.snapshot.layout(page_name)
    elif pathname.endswith('/_analytics') and (dash_enterprise_auth.get_username() == 'carlos.bonilla_insigneo.com' or dash_enterprise_auth.get_username() == 'miguel.reyes_insigneo.com' or dash_enterprise_auth.get_username() == 'sofia.berrosteguieta_insigneo.com'):
        return analytics.display_analytics()
    #elif page_name == 'dev':
        # Display a report with mock data for development purposes
    #    return pages.snapshot.report()
    else:
        return '404'

if __name__ == '__main__':
    app.run_server(debug=True)
