from fastapi import FastAPI, HTTPException,Form
import httpx
from pydantic import BaseModel
from typing import List, Optional
from pymongo import MongoClient
import json
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Request
from urllib.parse import urlencode
from .login import login_user
from bson import ObjectId

templates = Jinja2Templates(directory="api/templates")

app = APIRouter()

# Define MongoDB connection

client = MongoClient("mongodb://localhost:27017/")
db = client["crm"]
collection = db["contacts"]

# SuiteCRM API URL
crm_url = "http://192.168.1.116/suitcrm/service/v4_1/rest.php"

class UserAuth(BaseModel):
    user_name: str
    password: str

class Lead(BaseModel):
    phone_work: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    id: Optional[str]

@app.post("/collect_leads",response_model=dict)
async def collect_leads(batch_size: int = 2) -> any:
    try:
        module_name = "Leads"
        fields = ["phone_work", "first_name", "last_name"]

        session_id =  login_user()
        print(session_id)

        offset = 0
        while True:
            lead_request = {
                "method": "get_entry_list",
                "input_type": "JSON",
                "response_type": "JSON",
                "rest_data": json.dumps({
                    "session": session_id,
                    "module_name": module_name,
                    "query": "",
                    "order_by": "",
                    "offset": offset,
                    "select_fields": fields,
                }),
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            query_string = urlencode(lead_request) 

            async with httpx.AsyncClient() as client:
                leads_response = await client.post(
                    crm_url,
                    data=query_string,
                    headers=headers
                )
            leads = leads_response.json().get("entry_list", [])
            if not leads:
                break

            leads_data = [
                {field: lead["name_value_list"][field]["value"] for field in fields}
                for lead in leads
            ]

            # Insert leads data into MongoDB
            collection.insert_many(leads_data)

            offset += batch_size

        return {"message": "Leads collected successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


# Function to fetch data from MongoDB
async def fetch_data_from_mongo(skip: int = 0, limit: int = 10):
    data =  collection.find({}).skip(skip).limit(limit)
    print(data)
    return data


@app.get("/", response_class=HTMLResponse)
async def read_data(request: Request, skip: int = 0, limit: int = 10):
    data = await fetch_data_from_mongo(skip, limit)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "data": data,
        },
    )


@app.post("/edit_item")
async def edit_item(
   lead: Lead
):
    # Update the item in MongoDB
    try:
        print(lead)
        result =  collection.update_one(
            {"_id": ObjectId(lead.id)},
            {"$set": {"phone_work": lead.phone_work, "first_name": lead.first_name, "last_name": lead.last_name}},
        )
        print(result.modified_count,"result")
        if result.modified_count == 1:
            return {"message": "Item updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Item not found")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
