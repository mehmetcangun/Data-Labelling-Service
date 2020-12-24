import os
import psycopg2 as dbapi2

DB_URL = os.getenv("DATABASE_URL")

def add_domain(domain):
  with dbapi2.connect(DB_URL) as connection:
    with connection.cursor() as cursor:
      query = 'select * from '