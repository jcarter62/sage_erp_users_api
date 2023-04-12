"""
The main module of the sgma-api system
"""
from fastapi import FastAPI, Request, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, HTMLResponse
from decouple import config, UndefinedValueError
import requests

from wmisdb import WMISDB

app = FastAPI()

templates = Jinja2Templates(directory="templates")

def is_allowed(host_ip) -> bool:
    """
    Check if the host ip is allowed to access the resource based on ALLOWD_IPS environment variable

    :param host_ip: The host ip address
    :return: True if the host ip is allowed, False otherwise
    """
    try:
        ip_addresses = config('ALLOWED_IPS', default='')

        if ip_addresses == '':
            return True

        allowd_ips = ip_addresses.split(',')
        return host_ip in allowd_ips
    except UndefinedValueError as err:
        print(f'Error which checking allowd IPs: {err}')
        return False


@app.get("/")
async def root(request: Request):
    """
    The root path of the API
    """
    rsp = templates.TemplateResponse("home.html", {"request": {}})
    return rsp


@app.get("/showusers")
async def root(request: Request):
    """
    The root path of the API
    """
    user_data = await get_sage_erp_users()
    rsp = templates.TemplateResponse("current_users.html", {"request": user_data})
    return rsp



@app.get("/SageErpUsers")
async def get_sage_erp_users():
    """
    Get the list of Sage ERP users
    """
    try:
        db = WMISDB()
        users = db.get_sage_erp_users()
        appusers = 0
        biusers = 0
        for u in users:
            if u['appuser'] == 'X':
                appusers += 1
            if u['biuser'] == 'X':
                biusers += 1

        data = {"users": users, "message": "Success",
                "appusers": appusers, "biusers": biusers}
    except Exception as err:
        print(f'Unexpected error: {err}')
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            content={"message": f"Unexpected Error: {err}"})    
    return data


@app.middleware("http")
async def before_request(request: Request, call_next):
    """
    Middleware to check if the host ip is allowed to access the resource
    """
    try:
        method = request.method
        path = request.url.path
        print(f"method: {method}, path: {path}")
        ip_addr = str(request.client.host)
        if not is_allowed(ip_addr):
            data = {"message": f"IP {ip_addr} is not allowed to access this resource"}
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=data)
        response = await call_next(request)
    finally:
        pass
    return response



