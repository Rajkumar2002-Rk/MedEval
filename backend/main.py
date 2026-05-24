from fastapi import FastAPI

from models import TriageRequest


app = FastAPI(title="MedEval API", version="0.1.0")


@app.get("/health")
def health_check():
    return {"status": "ok"} 



@app.post("/triage")
def triage(request: TriageRequest):
    return {"received": request}

