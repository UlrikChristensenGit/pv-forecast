import polars as pl


def collection_to_df(data: dict) -> pl.DataFrame:

    df = pl.DataFrame(data["features"])

    df = df.unnest("properties")

    df = df.with_columns(
        [
            pl.col(["modelRun", "datetime", "created"]).str.to_datetime(),
        ]
    )

    df = df.select(
        [
            pl.col("id").alias("run_id"),
            pl.col("datetime").alias("time_utc"),
            pl.col("modelRun").alias("model_run_time_utc"),
        ]
    )

    return df
