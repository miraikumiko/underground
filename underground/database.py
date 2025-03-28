import databases
import sqlalchemy
from underground.config import TESTING, DATABASE_URL, DATABASE_TEST_URL

metadata = sqlalchemy.MetaData()

if TESTING:
    database = databases.Database(DATABASE_TEST_URL)
else:
    database = databases.Database(DATABASE_URL)
