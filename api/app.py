from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from api.jobs import get_job, submit_comparison_job
from api.schemas import ComparisonResultOut
from core import AIProvider, GeminiProvider
from core.exceptions import AIProviderError

logger = logging.getLogger(__name__)

_ai_provider: AIProvider | None = None


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global _ai_provider
    try:
        _ai_provider = GeminiProvider()
    except AIProviderError as e:
        logger.warning("IA deshabilitada, API arranca sin clasificación/veredicto visual: %s", e)
        _ai_provider = None
    yield


app = FastAPI(title="Document Review API", lifespan=lifespan)


@app.post("/comparisons")
async def create_comparison(
    actual: UploadFile = File(...),
    expected: UploadFile = File(...),
    enable_visual: bool = Form(False),
    hide_variable_fills: bool = Form(False),
) -> dict:
    actual_bytes = await actual.read()
    expected_bytes = await expected.read()

    job_id = submit_comparison_job(
        actual_bytes,
        actual.filename or "actual",
        expected_bytes,
        expected.filename or "expected",
        ai_provider=_ai_provider,
        enable_visual=enable_visual,
        hide_variable_fills=hide_variable_fills,
    )
    return {"job_id": job_id, "status": "pending"}


@app.get("/comparisons/{job_id}")
def get_comparison(job_id: str) -> dict:
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job no encontrado")

    if job.status == "pending":
        return {"job_id": job.id, "status": "pending"}
    if job.status == "error":
        return {"job_id": job.id, "status": "error", "error": job.error}

    return {
        "job_id": job.id,
        "status": "done",
        "result": ComparisonResultOut.model_validate(job.result).model_dump(mode="json"),
    }
