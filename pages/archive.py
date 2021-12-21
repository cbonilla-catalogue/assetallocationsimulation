from dash import html
import dash_design_kit as ddk
import dash_snapshots

from app import snap

def layout():
    return html.Div([
        ddk.SectionTitle('Previous Results'),
        snap.ArchiveTable(
            columns=[
                # These are "built-in" meta data options
                {
                    'id': dash_snapshots.constants.KEYS['snapshot_id'],
                    'name': 'Web Report'
                },
                {
                    'id': dash_snapshots.constants.KEYS['pdf'],
                    'name': 'PDF Download'
                },
                {
                    'id': dash_snapshots.constants.KEYS['username'],
                    'name': 'Creator',
                },
                {
                    'id': dash_snapshots.constants.KEYS['created_time'],
                    'name': 'Created Date'
                },

                # Example of a custom meta data key
                {
                    'id': 'financialAdvisor',
                    'name': 'Financial Advisor'
                },
                {
                    'id': 'clientName',
                    'name': 'Client Name'
                },
                {
                    'id': 'reportName',
                    'name': 'Report Name'
                }
            ]
        )
    ])
