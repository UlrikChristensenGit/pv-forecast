from azure_function.jobs.versioned_nwp.job import VersionedNwpETL

if __name__ == "__main__":
    etl = VersionedNwpETL()

    etl.run()
