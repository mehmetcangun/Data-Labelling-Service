import os
import psycopg2 as dbapi2

DB_URL = os.getenv("DATABASE_URL")
messages = {
  'insert' : 'The data is added.',
  'update' : 'The data is updated.',
  'delete' : 'The data is deleted.',
  'domains_name_key': 'Domain key should be unique, please try again.',
  'subdomains_domain_id_fkey': 'Domain has subdomains so the domain key should not deleted.',
  'error': 'Error has been occured. Please contact administrator.'
}
class Database():
  
  def select_query(self, name):
    with dbapi2.connect(DB_URL) as connection:
      with connection.cursor() as cursor:
        query = "select * from " + name
        cursor.execute(query)
        result = cursor.fetchall()
        header = list( cursor.description[i][0] for i in range(0, len(cursor.description)) )
        result_with_header = list()
        for i in result:
          result_with_header.append(dict(zip(header, i)))
    return result_with_header
  
  def select_query_by_id(self, idd, name, where):
    with dbapi2.connect(DB_URL) as connection:
      with connection.cursor() as cursor:
        query = "select * from "+name+" where "+where+" = %s"
        cursor.execute(query, (idd, ))
        result = cursor.fetchone()
        header = list( cursor.description[i][0] for i in range(0, len(cursor.description)) )
        result_with_header = None
        if result:
          result_with_header = dict(zip(header, result))
    return result_with_header

  def run_query(self,query, method, data):
    try:
      with dbapi2.connect(DB_URL) as connection:
        with connection.cursor() as cursor:
          cursor.execute(query, tuple(data))
          connection.commit()
          if method == 'insert':
            id_ = cursor.fetchone()[0]
            return messages['insert'], id_
          elif method == 'delete':
            return messages['delete'], 0
          elif method == 'update':
            return messages['update'], 0

    except dbapi2.IntegrityError as e:
      print(e.diag.constraint_name)
      print("dance ", e.diag.message_detail)
      if e.diag.constraint_name in messages:
        return messages[e.diag.constraint_name], -1
      return messages['error'], -1
    except dbapi2.Error as e:
      print(e.pgcode)
      print("mance: ", e.diag.message_detail)
      return messages['error'], -1

  def add(self, class_):
    query = 'insert into ' + class_['table_name'] +'('
    values = 'values ('
    data = []
    for key, value in enumerate(class_['data']):
      query += str(value)+','
      values += '%s,'
      data.append(class_['data'][value])
    query = query[:-1]
    query += ') '
    values = values[:-1]
    query += values + ') RETURNING ' + class_['primary_key']
    return self.run_query(query, 'insert', data)
      
  def update(self, class_):
    query = 'update '+ class_["table_name"] + ' set '
    data = []
    
    for key, value in enumerate(class_['data']):
      query += str(value) + '= %s,'
      data.append(class_["data"][value])
    query = query[:-1]
    query += ' where '

    for key, value in enumerate(class_['where']):
      query += value + '= %s and '
      data.append(class_["where"][value])
    
    query = query[:-4]
    return self.run_query(query,  'update', data)
    
  def delete(self, class_):
    query = 'delete from ' + class_["table_name"]
    data = []
    if len(class_["where"]) != 0:
      for key, value in enumerate(class_["where"]):
        data.append(class_["where"][value])    
        query += ' where ' + value + ' = %s'
    return self.run_query(query, 'delete', data)
