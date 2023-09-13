# main.py

from fastapi import FastAPI
from api.routers import lead_router
from api.lib.error_handler import validation_exception_handler, generic_exception_handler
from fastapi.exceptions import RequestValidationError

app = FastAPI()
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.add_exception_handler(Exception, generic_exception_handler)


app.include_router(lead_router.app)

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
