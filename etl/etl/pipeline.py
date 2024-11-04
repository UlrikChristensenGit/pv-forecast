import logging


def retry_policy(max_retries: int, errors: list[Exception]):
    def decorator(func):
        def new_func(*args, **kwargs):
            for i in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except errors as exc:
                    logging.warning(
                        f"Encountered error {exc}. Attempt {i}/{max_retries}."
                    )

        return new_func

    return decorator
