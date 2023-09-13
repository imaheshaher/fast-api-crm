from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Create a function to handle HTTP 422 Unprocessable Entity (validation error)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )

# Create a function to handle other exceptions (HTTP 500 Internal Server Error)
async def generic_exception_handler(request: Request, exc: Exception):

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )
