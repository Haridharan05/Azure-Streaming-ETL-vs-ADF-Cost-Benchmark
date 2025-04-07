# """Upload raw blob bytes to ADLS Gen2 for archival."""

from azure.storage.filedatalake.aio import DataLakeFileClient
import os, asyncio, logging

ADLS_URL = os.getenv("ADLS_URL")          # dfs.core.windows.net URL with SAS or MSI
FILESYSTEM = os.getenv("ADLS_FS", "raw-archive")

async def upload_to_adls(blob_name: str, data: bytes):
    path = f"{blob_name}"
    try:
        client = DataLakeFileClient.from_connection_string(ADLS_URL, FILESYSTEM, path)
        await client.upload_data(data, overwrite=True)
    except Exception as exc:
        logging.error("adls upload failed: %s", exc)