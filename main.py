from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import hashlib
import datetime

app = FastAPI()
app.counter = 0
app.pid = 0


class Message(BaseModel):
    message: str


class Patient(BaseModel):
    id: Optional[int] = None
    name: str
    surname: str
    register_date: Optional[str]
    vaccination_date: Optional[str]


@app.get("/", status_code=200)
def root_view():
    return {"message": "Hello world!"}


@app.get("/hello/{name}", response_model=Message)
def hello_name_view(name: str):
    return Message(message=f"Hello {name}")


@app.get("/counter")
def counter():
    app.counter += 1
    return str(app.counter)


@app.get("/method", status_code=200)
def method_g():
    return {"message": "GET"}


@app.put("/method", status_code=200)
def method_p():
    return {"message": "PUT"}


@app.options("/method", status_code=200)
def method_o():
    return {"message": "OPTIONS"}


@app.delete("/method", status_code=200)
def method_d():
    return {"message": "DELETE"}


@app.post("/method", status_code=201)
def method_po():
    return {"message": "POST"}


@app.get("/auth", status_code=204)
def haslo_hash_no(password: str, password_hash: str):
    p = hashlib.sha512(password.encode('utf-8')).hexdigest()
    if password_hash == "" or password == "" or password_hash != p:
        raise HTTPException(status_code=401)


@app.post("/register", status_code=201)
def register_pac(patient: Patient):
    app.pid += 1
    patient.id = app.pid
    patient.register_date = datetime.date.today()
    patient.vaccination_date = datetime.date.today() + datetime.timedelta(len(patient.name) + len(patient.surname))
    return patient


@app.get("/patient/{id}", status_code=200)
def download_pac(id: int):
    if id < 1:
        HTTPException(status_code=400)
