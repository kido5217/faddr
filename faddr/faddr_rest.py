"""REST API entry point."""

import uvicorn

from fastapi import FastAPI


app = FastAPI()


@app.get("/")
async def root():
    """API root."""
    return {"message": "Hello World"}


@app.get("/networks/")
async def get_networks(query):
    """Find network"""
    return {query: "network_data"}


def main():
    """Start gunicorn server."""
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")
