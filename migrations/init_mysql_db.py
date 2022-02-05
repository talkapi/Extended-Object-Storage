import MySQLdb

host = '127.0.0.1'
user = 'admin'
password = 'pass!23'
port = 3306
db = 'db'

#establishing the connection
conn = MySQLdb.Connection(
    host=host,
    user=user,
    passwd=password,
    port=port,
    db=db
)

#Creating table as per requirement
sqlObjects ='''CREATE TABLE Objects(
   id VARCHAR(1000) NOT NULL,
   directory_id CHAR(20),
   object_key VARCHAR(1000) NOT NULL,
   PRIMARY KEY (id)
)'''
conn.query(sqlObjects)

#Creating table as per requirement
sqlObjects ='''CREATE TABLE Directories(
   id VARCHAR(1000) NOT NULL,
   directory VARCHAR(1000),
   PRIMARY KEY (id)
)'''
conn.query(sqlObjects)

conn.commit()