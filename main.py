import requests
from fastapi import FastAPI, HTTPException, Response, Request, status, Depends, Cookie, responses
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
    session_token = hashlib.sha256(f"{credentials.username}{credentials.password}secret".encode()).hexdigest()
    response.set_cookie(key="session_token", value=session_token)
    return {"message": "Welcome"}


@app.post("/login_token", status_code=201)
def token_show(credentials: HTTPBasicCredentials = Depends(security)):
    if not (credentials.username == "4dm1n") or not (credentials.password == "NotSoSecurePa$$"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    session_token = hashlib.sha256(f"{credentials.username}{credentials.password}secret".encode()).hexdigest()
    app.access_tokens.append(session_token)
    return {"token": session_token}


@app.get("/welcome_session")
def w_session(request: Request, *args):
    if request.cookies.get("session_token") != hashlib.sha256(f"4dm1nNotSoSecurePa$$secret".encode()).hexdigest():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    else:
        if args == "json":
            return responses.JSONResponse({"message": "Welcome!"})
        if args == "html":
            return HTMLResponse("Welcome!")
#            """
#                <html>
#                    <head>
#                        <title></title>
#                    </head>
#                    <body>
#                        <h1>Welcome!</h1>
#                    </body>
#                </html>
#            """
        else:
            return responses.PlainTextResponse("Welcome!")


@app.get(f"/welcome_token")
def w_token(*, response: Response, session_token: str, format: Optional[str]):
    if session_token not in app.access_tokens:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    else:
        if format == "json":
            return {"message": "Welcome!"}
        if format == "html":
            return """
                <html>
                    <head>
                        <title></title>
                    </head>
                    <body>
                        <h1>Welcome!</h1>
                    </body>
                </html>
            """
        else:
            return "Welcome!"
