# """Async MySQL bulk‑insert helper."""

import aiomysql, itertools, os, logging, asyncio

_POOL = None
BATCH = int(os.getenv("BATCH_SIZE", 10_000))

async def _get_pool():
    global _POOL
    if _POOL is None:
        _POOL = await aiomysql.create_pool(
            host=os.getenv("MYSQL_HOST"),
            port=int(os.getenv("MYSQL_PORT", 3306)),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PWD"),
            db=os.getenv("MYSQL_DB"),
            autocommit=True,
            minsize=1,
            maxsize=10,
        )
    return _POOL

async def bulk_insert_rows(rows):
    """Insert iterable of rows into `raw_data` table. Ignores duplicates."""
    pool = await _get_pool()
    inserted = 0
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            for chunk in iter(lambda: list(itertools.islice(rows, BATCH)), []):
                if not chunk:
                    break
                values = ",".join(str(tuple(r)) for r in chunk)
                try:
                    await cur.execute(f"INSERT IGNORE INTO raw_data VALUES {values}")
                    inserted += len(chunk)
                except Exception as exc:
                    logging.warning("batch failed: %s", exc)
    return inserted