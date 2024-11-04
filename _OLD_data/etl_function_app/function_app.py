import logging
import azure.functions as func

app = func.FunctionApp()


@app.schedule(
    schedule="0 * * * * *",
    arg_name="myTimer",
    run_on_startup=True,
    use_monitor=False,
)
def timer_trigger(myTimer: func.TimerRequest) -> None:
    pass
