from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dbms import Database

app = FastAPI()
db = Database(data_dir='data')

class SQLCommand(BaseModel):
    command: str

@app.post("/execute")
async def execute_command(sql_command: SQLCommand):
    command = sql_command.command.strip()
    try:
        result = db.execute(command)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
