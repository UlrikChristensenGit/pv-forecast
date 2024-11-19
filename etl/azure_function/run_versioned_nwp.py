import dotenv
dotenv.load_dotenv()

from jobs.versioned_nwp.job import VersionedNwpETL

if __name__ == "__main__":

    etl = VersionedNwpETL()

    etl.run()
