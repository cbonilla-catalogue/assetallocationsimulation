# Generating PDF Reports from Background Task


Generate pixel-perfect PDF and web-based reports
with `ddk.Report` with data fetched or computed
in a long-running background task.

The background task simulates an capital market asset allocation
performance using a onte carlo simulation.

## Running this application

1. Install the Python dependencies
```
pip install -r requirements.txt
```

> For better database performance, we've included the `psycopg2` library in
> `requirements.txt`. 
> 
2. Install & Run Redis

 This application uses `celery` to run tasks in a background job queue.
 Celery uses Redis to transfer data between the Dash app and its job queue.
 See [Read this First]({base_url}/Docs/read-this-first) for instructions on how to install & run Redis.
 > Note: If you are using the Dash Enterprise's built-in development environment [Workspaces]({base_url}/Docs/workspaces) on Dash Enterprise Single Node, then you can simply create & link and Redis database to your app.
 > The same Redis instance will be shared with your app and the workspace and the `dash-snapshots` library will automatically partition the data on Redis separately between workspace and deployed application.
 > If you are using Dash Enterprise on Kubernetes, then you will need to provide an external Redis instance via an environment variable into your workspace.
 > See [deploying `dash-snapshots`]({base_url}/Docs/dash-snapshots/deployment).

3. In separate terminals, run the following commands:
```python
python index.py
```

```python
celery -A index:celery_instance worker --loglevel=INFO --concurrency=2
```

> Note:

> 1. These commands were adapted from the Procfile, which is the list of commands that are used when the application is deployed. The only difference is that `gunicorn` was replaced with `python` for running the application locally with Dash's devtools and reloading features.

> 2. If you get an error message like
> "`REDIS_URL` needs to be available as an environment variable."
> Then prepend the env variable `REDIS_URL=redis://127.0.0.1:6379` on every command:
> REDIS_URL=redis://127.0.0.1:6379 python index.py
> REDIS_URL=redis://127.0.0.1:6379 celery -A index:celery_instance worker --loglevel=INFO --concurrency=2

## References
