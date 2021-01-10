import os
import psycopg2 as dbapi2

DB_URL = os.getenv("DATABASE_URL")
messages = {
  'insert' : 'The data is added.',
  'update' : 'The data is updated.',
  'delete' : 'The data is deleted.',
  'domains_name_key': 'Domain key should be unique, please try again.',
  'subdomains_domain_id_fkey': 'Domain has subdomains so the domain key should not deleted.',
  'labels_subdomain_id_fkey': 'Subdomain has been used in labels so the subdomain could not be deleted.',
  'images_criteria_id_fkey': 'This criteria have images so the criteria could not be deleted.',
  'users_email_key': 'You must check your credentials!',
  'criterias_user_id_fkey':'User have criterias so the user could not be deleted.',
  'error': 'Error has been occured. Please contact administrator.'
}

select_query = {
  'domains': """select d.domain_id, d.domain_name, d.description, d.domain_priority_rate, d.color, count(sd.domain_id) as subdomain_length
        from domains as d left join subdomains as sd on d.domain_id = sd.domain_id
        %s
        group by d.domain_id""",
  'labels' : """
        select label_id, domain_name, subdomain_name, description, color, icon, is_correct, frontcolor, backgroundcolor
        from labels as lb inner join images as img on lb.image_id = img.image_id
        inner join subdomains as sd on sd.subdomain_id = lb.subdomain_id
        inner join domains as d on d.domain_id = sd.domain_id
        %s
        """,
  'users': """select u.user_id as user_id, uname, surname, security_answer, email, usertype, points,
         count(cnt.user_id) as contribution_size,
         to_char(last_seen, 'DD Mon YYYY HH24:MI:SS') as last_seen,
         to_char(join_date, 'DD Mon YYYY HH24:MI:SS') as join_date
        from users as u left join contributions as cnt on u.user_id = cnt.user_id
        %s
        group by u.user_id""",
  'images': """select i.image_id as image_id, title, url_path, 
        count(c.contribution_id) as user_contribution, most_contribution, classification_type,
        case
           when is_favourite = false THEN 'No'
           ELSE 'Yes'
        END as is_favourite
        , count(l.label_id) as label_count
        from images as i left join labels as l on i.image_id = l.image_id
                 left join contributions as c on c.label_id = l.label_id
        %s
        group by i.image_id  
  """,
  'subdomains_for_label': """select sd.subdomain_id, domain_name, description, subdomain_name, color, icon, frontcolor, backgroundcolor
      from domains as d inner join subdomains as sd on d.domain_id = sd.domain_id
      %s
  """,
  'subdomains' : 'select sd.subdomain_id, domain_name, description, frontcolor, backgroundcolor, subdomain_name, subdomain_priority_rate, icon, count(lb.image_id) as count_images_used from domains as d inner join subdomains as sd on d.domain_id = sd.domain_id left join labels as lb on lb.subdomain_id = sd.subdomain_id %s group by sd.subdomain_id, d.domain_id',

  'criterias': "select c.criteria_id as criteria_id, for_contribution, correctness, wrongness, uname, surname, count(img.criteria_id) as count_images_used from criterias as c inner join users as u on c.user_id = u.user_id left join images as img on img.criteria_id = c.criteria_id %s group by c.criteria_id, u.user_id"
}

sort_by_tables = {
  'users': {
    'default':' u.user_id DESC',
    'points_asc':' points ASC',
    'points_desc':' points DESC',
    'contribution_size_asc':' contribution_size ASC',
    'contribution_size_desc':' contribution_size DESC',
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
    'default': 'criteria_id DESC',
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
    'default': 'domain_id DESC',
    'domain_name_asc':' domain_name ASC',
    'domain_name_desc':' domain_name DESC',
    'domain_priority_rate_asc':' domain_priority_rate ASC',
    'domain_priority_rate_desc':' domain_priority_rate DESC',
    'subdomain_length_asc':' subdomain_length ASC',
    'subdomain_length_desc':' subdomain_length DESC',
  },
  'images': {
    'default': 'image_id DESC',
    'user_contribution_asc': 'user_contribution ASC',
    'user_contribution_desc': 'user_contribution DESC',
    'most_contribution_asc': 'most_contribution ASC',
    'most_contribution_desc': 'most_contribution DESC',
    'title_asc': 'title ASC',
    'title_desc': 'title DESC',
    'classification_type_asc': 'classification_type ASC',
    'classification_type_desc': 'classification_type DESC',
    'label_count_asc': 'label_count ASC',
    'label_count_desc': 'label_count DESC',
    'is_favourite_asc': 'is_favourite ASC',
    'is_favourite_desc': 'is_favourite DESC',
  },
  'subdomains': {
    'default': 'subdomain_id DESC',
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
    'default': 'label_id DESC',
    'domain_name_asc':' domain_name ASC',
    'domain_name_desc':' domain_name DESC',
    'subdomain_name_asc':' subdomain_name ASC',
    'subdomain_name_desc':' subdomain_name DESC',
    'is_correct_asc':' is_correct ASC',
    'is_correct_desc':' is_correct DESC'
  }
}

group_search_correspond = {
  'criterias': {
    'count_images_used': 'count(img.criteria_id)'
  },
  'subdomains': {
    'count_images_used': 'count(lb.image_id)'
  },
  'domains': {
    'subdomain_length': 'count(sd.domain_id)'
  },
  'users': {
    'contribution_size': 'count(cnt.user_id)'
  },
  'images': {
    'user_contribution': 'count(c.contribution_id)',
    'label_count': 'count(l.label_id)'
  }
}

class Database():
  def select_query(self, name, data=[], sort_by=None, search=None):
    query = select_query[name]
    #search.
    where = ""
    
    search_between = dict()
    search_group_between = dict()
    
    for key in search:
      if search[key] != '':
        if key.startswith('search_to_'):
          if key[10:] not in search_between:
            search_between[key[10:]] = dict()
          search_between[key[10:]]['to'] = search[key]
        elif key.startswith('search_from_'):
          if key[12:] not in search_between:
            search_between[key[12:]] = dict()
          search_between[str(key[12:])]['from'] = search[key]
        elif key.startswith('search_gto_'):
          if key[11:] not in search_group_between:
            search_group_between[key[11:]] = dict()
          search_group_between[key[11:]]['to'] = search[key]
        elif key.startswith('search_gfrom_'):
          if key[13:] not in search_group_between:
            search_group_between[key[13:]] = dict()
          search_group_between[str(key[13:])]['from'] = search[key]
        else:
          # Like usage in Queries https://stackoverflow.com/a/37273764
          
          if key.startswith('search_like_'):
            where += '{} like %s and '.format(key[12:])
            pattern_wise = '%{}%'.format(search[key])
            data.append(pattern_wise)
          else:
            where += '{} = %s and '.format(key[7:])
            data.append(search[key])
    
    if where != '' and name not in ('labels', 'subdomains_for_label'):
      where = ' where '+where
    
    if name == 'labels':
      where = ' where lb.image_id = %s and '+where
    elif name == 'subdomains_for_label':
      where = ' where sd.subdomain_id not in (select subdomain_id from labels where image_id = %s) and '+where

    for key in search_between:
      if 'from' in search_between[key] and 'to' in search_between[key]:
        where += ' {} between %s and %s and '.format(key)
        data.append(search_between[key]['from'])
        data.append(search_between[key]['to'])
      elif 'from' in search_between[key]:
        where += ' {} >= %s '.format(key)
        data.append(search_between[key]['from'])
      elif 'to' in search_between[key]:
        where += ' {} <= %s '.format(key)
        data.append(search_between[key]['to'])
    
    where = where[:-4]
    query = query % where
    having = " having "
    for key in search_group_between:
      if 'from' in search_group_between[key] and 'to' in search_group_between[key]:
        having += ' {} between %s and %s and '.format(group_search_correspond[name][key])
        data.append(search_group_between[key]['from'])
        data.append(search_group_between[key]['to'])
      elif 'from' in search_group_between[key]:
        having += ' {} >= %s and '.format(group_search_correspond[name][key])
        data.append(search_group_between[key]['from'])
      elif 'to' in search_group_between[key]:
        having += ' {} <= %s and '.format(group_search_correspond[name][key])
        data.append(search_group_between[key]['to'])
    
    having = having[:-4]
    if len(search_group_between)>0:
      query += having
    
    #sort.        
    if sort_by is not None:
      query = query + ' order by ' + sort_by_tables[name][sort_by]
    print('KELLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL')
    print(query)
    print(data)
    
    with dbapi2.connect(DB_URL) as connection:
      with connection.cursor() as cursor:
        cursor.execute(query, tuple(data))
        data.clear()
        result = cursor.fetchall()
        header = list( cursor.description[i][0] for i in range(0, len(cursor.description)) )
        result_with_header = list()
        for i in result:
          result_with_header.append(dict(zip(header, i)))
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
          print(query)
          print(data)
          print(method)
          
          cursor.execute(query, tuple(data))
          connection.commit()
          message = messages[method]
          
          if method == 'insert':
            id_ = cursor.fetchone()[0]
            return message, id_
          elif method == 'delete' or method == 'update':
            if cursor.rowcount <= 0:
              message = "Check your credentials."
            return message, cursor.rowcount

    except dbapi2.IntegrityError as e:
      print(e.diag.constraint_name)
      print("dance ", e.diag.message_detail)
      if e.diag.constraint_name in messages:
        return messages[e.diag.constraint_name], -1
      return messages['error'], -1
    except dbapi2.Error as e:
      print(e.pgcode)
      print(e.message_primary)
      print(e.column_name)
      print(e.constraint_name)
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
