"""
The main module of the sgma-api system
"""
from fastapi import FastAPI, Request, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from decouple import config, UndefinedValueError
from datetime import datetime
import pathlib

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


@app.get("/favicon.ico")
async def favicon():
    """
    Return the favicon.ico file
    """
    file_name = 'favicon.ico'
    file_path = pathlib.Path(__file__).parent.resolve() / file_name
    return FileResponse(path=file_path, headers={"Content-Type": "image/x-icon"})


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

    def remove_domain(user):
        """
        Remove the domain from the user name
        """
        if user.find('\\') > 0:
            return user.split('\\')[1]
        return user

    def reformat_datetime(dt: str):
        """
        Reformat the datetime string from YYYY-MM-DD HH:MM:SS.Z to MM/DD/YYYY HH:MM AM/PM
        """
        if dt is None:
            return ''
        datetime_tmp = dt.replace('T', ' ').replace('Z', '')

        # check to see if .%f is in the string, and add it if not
        if not('.' in datetime_tmp):
            datetime_tmp = f'{datetime_tmp}.000000'

        dtmp = None
        for fmt in ('%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S'):
            try:
                dtmp = datetime.strptime(datetime_tmp, fmt)
                break
            except Exception as err:
                print(f'Error in reformat_datetime: {err}')
                pass

        if dtmp is None:
            result = ''
        else:
            result = dtmp.strftime('%m/%d/%Y %I:%M %p')

        return result

    def sort_users(users):
        """
        Sort the users by sort_key
        """
        return sorted(users, key=lambda k: k['sort_key'])


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
            u['username'] = remove_domain(u['username'])

            u['login_time'] = reformat_datetime(u['login_time'].__str__())
            u['last_activty'] = reformat_datetime(u['last_activty'].__str__())
            u['sort_key'] = datetime.strptime(u['last_activty'], '%m/%d/%Y %I:%M %p')

        users = sort_users(users)

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
        # print(f"method: {method}, path: {path}")
        ip_addr = str(request.client.host)
        if not is_allowed(ip_addr):
            data = {"message": f"IP {ip_addr} is not allowed to access this resource"}
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=data)
        response = await call_next(request)
    finally:
        pass
    return response



