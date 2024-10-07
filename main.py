# api_gateway.py

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# Configure CORS as needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the URLs for each microservice
AUTH_SERVICE_URL = "http://localhost:8001"
QUEST_CATALOG_SERVICE_URL = "http://localhost:8002"
QUEST_PROCESSING_SERVICE_URL = "http://localhost:8003"

# Create a single HTTP client to reuse connections
client = httpx.AsyncClient()


@app.middleware("http")
async def proxy_requests(request: Request, call_next):
    path = request.url.path

    # Exclude /docs and related paths to prevent proxying internal FastAPI routes
    if (
        path.startswith("/docs")
        or path.startswith("/openapi.json")
        or path.startswith("/favicon.ico")
    ):
        return await call_next(request)

    # Routing logic based on the request path
    if (
        path.startswith("/register/")
        or path.startswith("/token")
        or path.startswith("/users/me/")
    ):
        target_url = AUTH_SERVICE_URL + path
    elif path.startswith("/quests/"):
        target_url = QUEST_CATALOG_SERVICE_URL + path
    elif (
        path.startswith("/assign-quest/")
        or path.startswith("/update-status/")
        or path.startswith("/claim-reward/")
        or path.startswith("/user-quests/")
        or path.startswith("/user-quest-rewards/")
        or path.startswith("/users-with-quests/")
    ):
        target_url = QUEST_PROCESSING_SERVICE_URL + path
    else:
        return Response(status_code=404, content="Not Found")

    # Prepare the request
    try:
        # Forward the incoming request to the target service
        response = await client.request(
            method=request.method,
            url=target_url,
            headers=request.headers.raw,
            content=await request.body(),
            params=request.query_params,
        )
    except httpx.RequestError as e:
        return Response(status_code=502, content="Bad Gateway: " + str(e))

    # Build the response to send back to the client
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
    )


# Run the API Gateway
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
