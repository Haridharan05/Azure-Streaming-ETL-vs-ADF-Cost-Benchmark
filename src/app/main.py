# """FastAPI entry‑point for streaming CSV → MySQL + ADLS."""

from fastapi import FastAPI, HTTPException
from azure.storage.blob.aio import BlobServiceClient
from .loader import bulk_insert_rows
from .adls import upload_to_adls
from .metrics import REQUEST_COUNT, LATENCY_HISTO
import csv, gzip, os, logging, asyncio, io

app = FastAPI(title="CSV‑to‑DL Micro‑ETL", version="1.0.0")

# ENV vars
STORAGE_CONN = os.getenv("AZ_BLOB_CONN")     # connection‑string or SAS
CONTAINER    = os.getenv("AZ_BLOB_CONTAINER", "raw-csv")

@app.get("/healthz")
async def health():
    """Liveness probe for Azure."""
    return {"status": "ok"}

@app.get("/load/{blob_name}")
@LATENCY_HISTO.time()
async def load_blob(blob_name: str):
    """Download a gzipped CSV from Blob, insert rows to MySQL, then copy raw file to ADLS."""
    try:
        async with BlobServiceClient.from_connection_string(STORAGE_CONN) as svc:
            bc = svc.get_blob_client(CONTAINER, blob_name)
            stream = await bc.download_blob()
            buf = io.BytesIO()
            await stream.readinto(buf)
            buf.seek(0)
            text = gzip.decompress(buf.getvalue()).decode()
            reader = csv.reader(text.splitlines())
            inserted = await bulk_insert_rows(reader)
            await upload_to_adls(blob_name, buf.getvalue())
            REQUEST_COUNT.inc()
            return {"blob": blob_name, "rows_inserted": inserted}
    except Exception as ex:
        logging.exception("load failed")
        raise HTTPException(status_code=500, detail=str(ex))