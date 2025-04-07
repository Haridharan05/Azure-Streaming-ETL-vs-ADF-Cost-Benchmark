import pytest, anyio
from src.app.loader import bulk_insert_rows, _get_pool

@pytest.mark.anyio
async def test_bulk_insert():
    pool = await _get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("CREATE TABLE IF NOT EXISTS raw_data (id INT PRIMARY KEY, a VARCHAR(20), b INT, c VARCHAR(10))")
    rows = ((i, "x", 1, "y") for i in range(1, 101))
    inserted = await bulk_insert_rows(rows)
    assert inserted == 100