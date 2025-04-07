# """Benchmark script – fires parallel /load requests and records latency."""

import asyncio, csv, pathlib, statistics, time, httpx, click, os

@click.command()
@click.option("--app", envvar="APP_URL", required=True, help="Base URL of FastAPI service")
@click.option("--data", default="data/out", help="Folder of blob names (local reference)")
@click.option("--concurrency", default=4, show_default=True)
@click.option("--limit", default=None, type=int, help="Max blobs to test")
def main(app, data, concurrency, limit):
    blobs = [p.name for p in pathlib.Path(data).glob("*.gz")]
    if limit:
        blobs = blobs[:limit]
    click.echo(f"Benchmarking {len(blobs)} blobs against {app} …")

    async def one(name):
        t0 = time.perf_counter()
        async with httpx.AsyncClient(timeout=None) as c:
            await c.get(f"{app}/load/{name}")
        return time.perf_counter() - t0

    async def run():
        sem = asyncio.Semaphore(concurrency)
        async def bound(n):
            async with sem:
                return await one(n)
        return await asyncio.gather(*[bound(b) for b in blobs])

    durations = asyncio.run(run())
    with open("benchmark_results.csv", "w") as fh:
        csv.writer(fh).writerows(zip(blobs, durations))

    click.echo(f"median latency = {statistics.median(durations):.2f}s")

if __name__ == "__main__":
    main()