import os
import psycopg2 as dbapi2

DB_URL = os.getenv("DATABASE_URL")
messages = {
  'insert' : 'The data is added.',
  'update' : 'The data is updated.',
  'delete' : 'The data is deleted.',
  'domains_name_key': 'Domain key should be unique, please try again.',
  'subdomains_domain_id_fkey': 'Domain has subdomains so the domain key should not deleted.',
  'users_email_key': 'You must check your credentials!',
  'error': 'Error has been occured. Please contact administrator.'
}

select_query = {
  'domains': """select d.domain_id, d.domain_name, d.description, d.domain_priority_rate, d.color, count(sd.domain_id) as subdomain_length
        from domains as d left join subdomains as sd on d.domain_id = sd.domain_id
        group by d.domain_id""",
  'labels' : """
        select label_id, domain_name, subdomain_name, description, color, icon, is_correct
        from labels as lb inner join images as img on lb.image_id = img.image_id
        inner join subdomains as sd on sd.subdomain_id = lb.subdomain_id
        inner join domains as d on d.domain_id = sd.domain_id
        where lb.image_id = %s
        """,
  'users': """select u.user_id as user_id, uname, surname, email, usertype, points,
         count(cnt.user_id) as contribution_size,
         to_char(last_seen, 'DD Mon YYYY HH24:MI:SS') as last_seen,
         to_char(join_date, 'DD Mon YYYY HH24:MI:SS') as join_date
        from users as u left join contributions as cnt on u.user_id = cnt.user_id
        group by u.user_id""",
  'images': "select * from images",
  'subdomains_for_label': """select sd.subdomain_id, domain_name, description, subdomain_name, color, icon
      from domains as d inner join subdomains as sd on d.domain_id = sd.domain_id
      where sd.subdomain_id not in (
          select subdomain_id from labels where image_id = %s
      ) 
  """,
  'subdomains' : 'select sd.subdomain_id, domain_name, description, subdomain_name, subdomain_priority_rate, icon, count(lb.image_id) as count_images_used from domains as d inner join subdomains as sd on d.domain_id = sd.domain_id left join labels as lb on lb.subdomain_id = sd.subdomain_id group by sd.subdomain_id, d.domain_id',
  'criterias': "select c.criteria_id, for_contribution, correctness, wrongness, uname, surname, count(img.criteria_id) as count_images_used from criterias as c inner join users as u on c.user_id = u.user_id left join images as img on img.criteria_id = c.criteria_id group by c.criteria_id, u.user_id"
}

sort_by_tables = {
  'users': {
    'default':' u.user_id ASC',
    'points_asc':' points ASC',
    'points_desc':' points DESC',
    'contribution_size_asc':' contribution_size ASC',
    'contribution_size_asc':' contribution_size DESC',
    'join_date_asc':' join_date ASC',
    'join_date_desc':' join_date DESC',
    'last_seen_asc':' last_seen ASC',
    'last_seen_desc':' last_seen DESC',
    'uname_asc':' uname ASC',
    'uname_desc':' uname DESC',
    'surname_asc':' surname ASC',
    'surname_desc':' surname DESC'
  },
  'criterias': {
    'default': 'criteria_id',
    'uname_asc':' uname ASC',
    'uname_desc':' uname DESC',
    'for_contribution_asc':' for_contribution ASC',
    'for_contribution_desc':' for_contribution DESC',
    'correctness_asc':' correctness ASC',
    'correctness_desc':' correctness DESC',
    'wrongness_asc':' wrongness ASC',
    'wrongness_desc':' wrongness DESC',
    'count_images_used_asc':' count_images_used ASC',
    'count_images_used_desc':' count_images_used DESC'
  },
  'domains': {
    'default': 'domain_id',
    'domain_name_asc':' domain_name ASC',
    'domain_name_desc':' domain_name DESC',
    'domain_priority_rate_asc':' domain_priority_rate ASC',
    'domain_priority_rate_desc':' domain_priority_rate DESC',
    'subdomain_length_asc':' subdomain_length ASC',
    'subdomain_length_desc':' subdomain_length DESC',
  },
  'images': {
    'default': 'image_id'
  },
  'subdomains': {
    'default': 'subdomain_id',
    'domain_name_asc':' domain_name ASC',
    'domain_name_desc':' domain_name DESC',
    'subdomain_name_asc':' subdomain_name ASC',
    'subdomain_name_desc':' subdomain_name DESC',
    'subdomain_priority_rate_asc':' subdomain_priority_rate ASC',
    'subdomain_priority_rate_desc':' subdomain_priority_rate DESC',
    'count_images_used_asc':' count_images_used ASC',
    'count_images_used_desc':' count_images_used DESC'
  },
  'labels': {
    'default': 'label_id',
    'domain_name_asc':' domain_name ASC',
    'domain_name_desc':' domain_name DESC',
    'subdomain_name_asc':' subdomain_name ASC',
    'subdomain_name_desc':' subdomain_name DESC',
    'is_correct_asc':' is_correct ASC',
    'is_correct_desc':' is_correct DESC'
  }
}

class Database():
  
  #is_ordered?
  #like queries
  def select_query(self, name, data=[], sort_by=None, search=None):
    with dbapi2.connect(DB_URL) as connection:
      with connection.cursor() as cursor:
        query = select_query[name]
        if sort_by is not None:
          query = query + ' order by ' + sort_by_tables[name][sort_by]
        
        cursor.execute(query, tuple(data))
        
        result = cursor.fetchall()
        header = list( cursor.description[i][0] for i in range(0, len(cursor.description)) )
        result_with_header = list()
        for i in result:
          result_with_header.append(dict(zip(header, i)))
        #print(result_with_header)
    return result_with_header
  
  def select_query_by_id(self, idd, name, where, query=None):
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
