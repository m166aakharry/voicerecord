import pymysql
connection = pymysql.connect(
    host = "localhost",
    port = 3306,
    user = "root",
    database = "voice_recorder"
)
cursor = connection.cursor()
cursor.execute("SHOW TABLES")
result = cursor.fetchall()

sql="""
    INSERT INTO recordings(
        filename,
        filepath,
        mime_type,
        duration
    )
    VALUES (%s, %s, %s, %s)
    """
parameters = (
    "test.webm",
    "recordings/test.webm",
    "audio/webm",
    3.52
)
cursor.execute(sql, parameters)
connection.commit()