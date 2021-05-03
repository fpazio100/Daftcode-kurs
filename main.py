from fastapi import FastAPI, HTTPException, Response, Request, status, Depends, Cookie
from pydantic import BaseModel
from typing import Optional, Dict
import hashlib
import datetime
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials


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
security = HTTPBasic()
app.access_tokens = []


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


@app.api_route(path="/method", methods=["GET", "POST", "DELETE", "PUT", "OPTIONS"], status_code=200)
def read_request(request: Request, response: Response):
    request_method = request.method

    if request_method == "POST":
        response.status_code = status.HTTP_201_CREATED

    return {"method": request_method}


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
def register_patient(patient: Patient):
    app.pid += 1
    patient.id = app.pid
    patient.register_date = datetime.date.today()
    patient.vaccination_date = datetime.date.today() + \
                               datetime.timedelta(sum(c.isalpha() for c in patient.name) +
                                                  sum(c.isalpha() for c in patient.surname))
    app.storage[app.pid] = patient
    return patient


@app.get("/patient/{patient_id}", status_code=200)
def download_patient(patient_id: int):
    if patient_id < 1:
        raise HTTPException(status_code=400, detail="Invali id")
    elif patient_id not in app.storage:
        raise HTTPException(status_code=404, detail="Patient not found")
    else:
        return app.storage.get(patient_id)


@app.get("/hello", response_class=HTMLResponse)
def greet():
    date = datetime.date.today()
    return f"""
    <html>
        <head>
            <title>content-type</title>
        </head>
        <body>
            <h1>Hello! Today date is {date}</h1>
        </body>
    </html>
    """


@app.post("/login_session", status_code=201)
def login(response: Response, credentials: HTTPBasicCredentials = Depends(security)):
    if not (credentials.username == "4dm1n") or not (credentials.password == "NotSoSecurePa$$"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    token = hashlib.sha256(f"{credentials.username}{credentials.password}secret".encode()).hexdigest()
    app.access_tokens.append(token)
    response.set_cookie(key="session_token", value=token)
    return {"message": "Welcome"}


@app.post("/login_token", status_code=201)
def secured_data(*, response: Response, token: str = Cookie(None), credentials: HTTPBasicCredentials = Depends(security)):
    if not (credentials.username == "4dm1n") or not (credentials.password == "NotSoSecurePa$$"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    else:
        print(token)
        return {"token": response}
