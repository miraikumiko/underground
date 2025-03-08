import databases
import sqlalchemy
from underground.config import TESTING, DATABASE_URL, TEST_DATABASE_URL

metadata = sqlalchemy.MetaData()

if TESTING:
    database = databases.Database(TEST_DATABASE_URL)
else:
    database = databases.Database(DATABASE_URL)
