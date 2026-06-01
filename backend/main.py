from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import upload, invoice, analytics, chat

app = FastAPI(title="InvoSense API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(invoice.router)
app.include_router(analytics.router)
app.include_router(chat.router)

@app.get("/")
def root():
    return {"message": "InvoSense API is running", "version": "1.0.0"}