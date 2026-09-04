from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from datetime import date
from typing import Literal

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from api.jobs import get_job, list_jobs, rerun_job, submit_comparison_job
from api.schemas import ComparisonResultOut
from core import AIProvider, GeminiProvider
from core.exceptions import AIProviderError

logger = logging.getLogger(__name__)

PAGE_SIZE = 20

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

app.add_middleware(
    CORSMiddleware,
    # El puerto del dev server de Vite cambia seguido (5173 casi siempre está
    # ocupado), así que se permite cualquier puerto en localhost/127.0.0.1
    # en vez de fijar uno solo.
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_methods=["*"],
    allow_headers=["*"],
)


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)


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


@app.get("/comparisons")
def list_comparisons(
    status: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    filename: str | None = None,
    page: int = 1,
) -> dict:
    jobs, total = list_jobs(
        status=status,
        date_from=_parse_date(date_from),
        date_to=_parse_date(date_to),
        filename=filename,
        page=page,
        page_size=PAGE_SIZE,
    )
    return {
        "items": [
            {
                "job_id": job.id,
                "created_at": job.created_at.isoformat(),
                "expected_filename": job.expected_filename,
                "actual_filename": job.actual_filename,
                "status": job.result.summary.status if job.result else "",
            }
            for job in jobs
        ],
        "total": total,
        "page": page,
        "page_size": PAGE_SIZE,
    }


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


@app.get("/comparisons/{job_id}/files/{kind}")
def download_comparison_file(job_id: str, kind: Literal["actual", "expected"]) -> FileResponse:
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job no encontrado")

    path = job.actual_stored_path if kind == "actual" else job.expected_stored_path
    if not path.exists():
        raise HTTPException(status_code=404, detail="archivo no encontrado")

    filename = job.actual_filename if kind == "actual" else job.expected_filename
    return FileResponse(path, filename=filename)


@app.post("/comparisons/{job_id}/rerun")
def rerun_comparison(job_id: str) -> dict:
    new_job_id = rerun_job(job_id, ai_provider=_ai_provider)
    if new_job_id is None:
        raise HTTPException(status_code=404, detail="job o archivos originales no encontrados")
    return {"job_id": new_job_id, "status": "pending"}
