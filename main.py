from fastapi import FastAPI,UploadFile,File,Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import pymysql
import os

app = FastAPI()
app.mount(
    "/audio",
    StaticFiles(directory="recordings"),
    name="audio"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins = [
    "http://localhost:8000",
    "http://192.168.26.128"
    ],
    allow_methods = ["GET", "POST", "DELETE"]
)

@app.post("/upload")
def upload_audio(
        audio : UploadFile = File(),
        duration : float = Form()
    ):
    print (audio.filename)
    print(duration)

    data = audio.file.read()
    connection = None
    cursor = None 
    try:    
        connection = get_connection()
        cursor = connection.cursor()
        with open(f"recordings/{audio.filename}", "wb") as f:
            f.write(data)
        
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
            audio.filename,
            f"recordings/{audio.filename}",
            audio.content_type,
            duration
        )
        cursor.execute(sql, parameters)
        connection.commit()
        new_id = cursor.lastrowid
#如果非none則關閉    
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:    
            connection.close()

#回傳檔案資訊給前端
    return {
        "id" : new_id,
        "filename" : audio.filename,
        "duration" : duration
    }

@app.get("/recordings")
def getrecord():
    connection = None
    cursor = None 
    try:
        connection = get_connection()
        cursor = connection.cursor()  
        cursor.execute("SELECT * FROM recordings")  
        records = cursor.fetchall()
        result = []
        for record in records:
            result.append(
                {
                    "id" : record[0],
                    "filename" : record[1],
                    "filepath" : record[2],
                    "mime_type" : record[3],
                    "created_at" : record[4],
                    "duration" : record[5]
                }
            )
        return result
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:    
            connection.close()

@app.delete("/recordings/{id}")
def delete_recording(id: int):
    connection = get_connection()
    cursor = connection.cursor() 
    cursor.execute("SELECT * FROM recordings WHERE id = %s",
                   (id,)
                   ) 
    record = cursor.fetchone()
    filepath = record[2] 
    if os.path.exists(filepath):
        os.remove(filepath)
    cursor.execute(
        "DELETE FROM recordings WHERE id = %s",
        (id,)
    )
    connection.commit()

def get_connection():
    return pymysql.connect(
        host = "localhost",
        port = 3306,
        user = "voice_app",
        password="mak94041",
        database = "voice_recorder"
        )   
