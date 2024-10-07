from logic.etl import ETL
import time


if __name__ == "__main__":

    etl = ETL()

    while True:
        try:
            etl.run()
        except Exception as e:
            print("Error in ETL run. Trying again in 5 minutes!", e)
            time.sleep(5*60)