import dotenv
from logs import get_logger
logger = get_logger(__name__)

dotenv.load_dotenv()

from jobs.versioned_nwp.job import VersionedNwpETL


if __name__ == "__main__":
    try:
        etl = VersionedNwpETL()

        etl.run()
    except Exception:
        logger.exception("Error occurred during ETL run")
