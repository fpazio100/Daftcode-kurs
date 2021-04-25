import requests
from fastapi import FastAPI, HTTPException, Response, Request, Depends, status
from pydantic import BaseModel
from typing import Optional, Dict
import hashlib
import datetime



class Message(BaseModel):
    message: str


class Patient(BaseModel):
    id: Optional[int] = None
    name: str
    surname: str
    register_date: Optional[str]
    vaccination_date: Optional[str]


app = FastAPI()
app.counter = 0
app.pid = 0
app.storage: Dict[int, Patient] = {}


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


@app.get("/auth")
def auth_request(password: str = "", password_hash: str = ""):
    authorized = False
    if password and password_hash:
        phash = hashlib.sha512(bytes(password, "utf-8")).hexdigest()
        authorized = phash == password_hash

    if authorized:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.post("/register", status_code=201)
def register_pac(patient: Patient):
    app.pid += 1
    patient.id = app.pid
    patient.register_date = datetime.date.today()
    patient.vaccination_date = datetime.date.today() + \
                               datetime.timedelta(sum(c.isalpha() for c in patient.name) +
                                                  sum(c.isalpha() for c in patient.surname))
    app.storage[app.pid] = patient
    return patient


@app.get("/patient/{patient_id}", status_code=200)
def download_pac(patient_id: int):
    if patient_id < 1:
        raise HTTPException(status_code=400, detail="Invali id")
    elif patient_id not in app.storage:
        raise HTTPException(status_code=404, detail="Patient not found")
    else:
        return app.storage.get(patient_id)



