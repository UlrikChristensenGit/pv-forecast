import dotenv
dotenv.load_dotenv()

from logs import get_logger
logger = get_logger(__name__)


from jobs.latest_nwp.job import LatestNwpETL


if __name__ == "__main__":
    try:
        etl = LatestNwpETL()

        etl.run()
    except Exception:
        logger.exception("Error occurred during ETL run")
