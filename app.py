import requests
import json
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from vietinbank import VTB


app = FastAPI()
@app.get("/")
def read_root():
    return {"Hello": "World"}
class LoginDetails(BaseModel):
    username: str
    password: str
    account_number: str
@app.post('/login', tags=["login"])
def login_api(input: LoginDetails):
        vtb = VTB(input.username, input.password, input.account_number)
        response = vtb.do_login()
        return response

@app.post('/get_balance', tags=["get_balance"])
def get_balance_api(input: LoginDetails):
        vtb = VTB(input.username, input.password, input.account_number)
        response = vtb.do_login()
        if response['success']:
            balance = vtb.get_balance(input.account_number)
            return balance
        else:
            return response
    
class Transactions(BaseModel):
    username: str
    password: str
    account_number: str
    from_date: str
    to_date: str
    limit: int
    
@app.post('/get_transactions', tags=["get_transactions"])
def get_transactions_api(input: Transactions):
        vtb = VTB(input.username, input.password, input.account_number)
        response = vtb.do_login()
        if response['success']:
            transaction = vtb.get_transaction(input.limit,input.from_date, input.to_date)
            return transaction
        else:
            return response


if __name__ == "__main__":
    uvicorn.run(app ,host='0.0.0.0', port=3000)