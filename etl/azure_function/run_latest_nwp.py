from jobs.latest_nwp.job import LatestNwpETL

if __name__ == "__main__":
    etl = LatestNwpETL()

    etl.run()
