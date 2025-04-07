# """Generate synthetic CSV chunks totalling ~N rows (~200 B/row)."""

import csv, gzip, pathlib, random, string, click

ROWS_PER_CHUNK = 1_000_000  # ≈200 MB gz

@click.command()
@click.option("--rows", default=250_000_000, show_default=True, help="Total rows to generate")
@click.option("--out", default="data/out", show_default=True, help="Output directory")
def main(rows, out):
    out_dir = pathlib.Path(out)
    out_dir.mkdir(parents=True, exist_ok=True)

    def rand_str(n=12):
        return "".join(random.choices(string.ascii_letters, k=n))

    def one_row(i):
        return [i, rand_str(), random.randint(0, 10_000), rand_str(5)]

    for part, start in enumerate(range(0, rows, ROWS_PER_CHUNK), 1):
        fn = out_dir / f"part_{part:04}.csv.gz"
        with gzip.open(fn, "wt", newline="") as fh:
            w = csv.writer(fh)
            for i in range(start, min(start + ROWS_PER_CHUNK, rows)):
                w.writerow(one_row(i))
        click.echo(f"wrote {fn}")

if __name__ == "__main__":
    main()