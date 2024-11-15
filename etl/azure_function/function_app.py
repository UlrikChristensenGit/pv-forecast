import azure.functions as func
from jobs.versioned_nwp.job import VersionedNwpETL
from jobs.latest_nwp.job import LatestNwpETL

app = func.FunctionApp()


@app.function_name("etl_versioned_nwp")
@app.timer_trigger(
    schedule="0 0 */6 * * *",
    arg_name="timer",
    use_monitor=False,
    run_on_startup=True,
)
def etl_versioned_nwp_timer_trigger(timer: func.TimerRequest) -> None:
    etl = VersionedNwpETL()

    etl.run()


@app.function_name("etl_latest_nwp")
@app.timer_trigger(
    schedule="0 0 */6 * * *",
    arg_name="timer",
    use_monitor=False,
    run_on_startup=True,
)
def etl_latest_nwp_timer_trigger(timer: func.TimerRequest) -> None:
    etl = LatestNwpETL()

    etl.run()

