import dotenv
dotenv.load_dotenv()
import os
print(os.environ["APP_INSIGHTS_CONNECTION_STRING"])