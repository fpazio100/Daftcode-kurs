import requests
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
    return {"method": "GET"}


@app.put("/method", status_code=200)
def method_p():
    return {"method": "PUT"}


@app.options("/method", status_code=200)
def method_o():
    return {"method": "OPTIONS"}


@app.delete("/method", status_code=200)
def method_d():
    return {"method": "DELETE"}


@app.post("/method", status_code=201)
def method_po():
    return {"method": "POST"}


@app.get("/auth", status_code=204)
def haslo_hash_no(password: str, password_hash: str):
    p = hashlib.sha512(password.encode('utf-8')).hexdigest()
    r = ''
    r = hashlib.sha512(r.encode('utf-8')).hexdigest()
    if password_hash == "" or password == "" or password_hash != p or password_hash == r or password_hash is None\
            or password is None:
        raise HTTPException(status_code=401)


@app.post("/register", status_code=201)
def register_pac(patient: Patient):
    app.pid += 1
    patient.id = app.pid
    patient.register_date = datetime.date.today()
    patient.vaccination_date = datetime.date.today() + datetime.timedelta(len(patient.name) + len(patient.surname))
    return patient


@app.get("/patient/{id}", status_code=200, response_model=Patient)
def download_pac(id: int, name: str, surname: str, register_date: str, vaccination_date: str):
    patient = {"id": id, "name": name, "surname": surname, "register_date": register_date, "vaccination_date": vaccination_date}
    return patient



