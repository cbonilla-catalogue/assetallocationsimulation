import dash_design_kit as ddk
import plotly.express as px
import pandas as pd

from app import snap

@snap.celery_instance.task
@snap.snapshot_async_wrapper(save_pdf=True, pdf_ssl_verify=True, pdf_orientation = 'landscape')#change back to True when we install the security certificate
def run_model(rows=None,financialAdvisor=None, clientName=None, reportName=None,businessType=None):
    # This function is called in a separate task queue managed by celery
    # This function's parameters (temperature, pressure, humidity) are
    # provided by the callback above with `snap.snapshot_save_async`

    # Whatever is returned by this function will be saved to the database
    # with the `snapshot_id`. It needs to be JSON-serializable

    # In this case, we're just returning a pandas dataframe
    # This dataframe is loaded by `snapshot.layout` and transformed
    # into a set of `ddk.Report` & `ddk.Page` components.
    # This allows you to change your `ddk.Report` & `ddk.Page` reports
    # for older datasets.

    # You could also return a `ddk.Report` etc here if you want previously
    # saved reports to not change when you deploy new changes to your
    # `ddk.Report` layout code
    # in practice, these will be generated from
    # your expensive, time-consuming code
    df = pd.DataFrame(rows)
    return {
        'uploadedData': df.to_dict(),
        'financialAdvisor' : financialAdvisor,
        'clientName': clientName,
        'reportName': reportName,
        'businessType':businessType,
    }
