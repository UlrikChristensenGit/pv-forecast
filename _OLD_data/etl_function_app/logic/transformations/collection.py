import polars as pl


def filter_to_latest_run_per_time(df: pl.DataFrame) -> pl.Series:
    df = (
        df.sort(by="model_run_time_utc")
        .group_by(by="time_utc", maintain_order=True)
        .last()
    )

    return df
