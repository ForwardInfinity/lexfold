import os

import psycopg
from fastapi import FastAPI

app = FastAPI(title="LexFold API", version="0.1.0")


@app.get("/healthz")
def healthz():
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        runs = conn.execute("SELECT count(*) FROM replay_run").fetchone()[0]
    return {"status": "ok", "replay_runs": runs}
