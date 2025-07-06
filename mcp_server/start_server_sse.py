import contextlib
from fastapi import FastAPI, Depends
from sports_news_server import sports_news_server
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

# Create a lifespan to manage session manager
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    async with contextlib.AsyncExitStack() as stack:
        await stack.enter_async_context(sports_news_server.session_manager.run())
        #await stack.enter_async_context(another_server.session_manager.run())  # Here we can run another server
        yield

app = FastAPI(docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specify ["http://localhost:3000"] if you want to be strict
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/", sports_news_server.sse_app())
#app.mount("/another", another_server.streamable_http_app())
#@app.api_route("/mcp", methods=["GET", "POST"])
#async def handle(req, res):
#    await transport.handle_request(req, res)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)