from fastapi import FastAPI



API_VERSION = "v1"
app = FastAPI(
    version=API_VERSION,
)

