from __future__ import annotations

import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from threading import Lock

from core import AIProvider, ComparisonResult, compare_documents
from core.exceptions import CoreError

_executor = ThreadPoolExecutor(max_workers=2)
_jobs: dict[str, "Job"] = {}
_lock = Lock()

STORAGE_DIR = Path(__file__).resolve().parent.parent / "storage" / "comparisons"


@dataclass
class Job:
    id: str
    actual_filename: str
    expected_filename: str
    enable_visual: bool
    hide_variable_fills: bool
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "pending"  # pending | done | error
    result: ComparisonResult | None = None
    error: str | None = None

    @property
    def dir(self) -> Path:
        return STORAGE_DIR / self.id

    @property
    def actual_stored_path(self) -> Path:
        return self.dir / f"actual_{self.actual_filename}"

    @property
    def expected_stored_path(self) -> Path:
        return self.dir / f"expected_{self.expected_filename}"


def submit_comparison_job(
    actual_bytes: bytes,
    actual_filename: str,
    expected_bytes: bytes,
    expected_filename: str,
    *,
    ai_provider: AIProvider | None,
    enable_visual: bool,
    hide_variable_fills: bool,
) -> str:
    job_id = uuid.uuid4().hex
    job = Job(
        id=job_id,
        actual_filename=actual_filename or "actual",
        expected_filename=expected_filename or "expected",
        enable_visual=enable_visual,
        hide_variable_fills=hide_variable_fills,
    )
    with _lock:
        _jobs[job_id] = job

    job.dir.mkdir(parents=True, exist_ok=True)
    job.actual_stored_path.write_bytes(actual_bytes)
    job.expected_stored_path.write_bytes(expected_bytes)

    _executor.submit(_run_job, job, ai_provider)
    return job_id


def get_job(job_id: str) -> Job | None:
    with _lock:
        return _jobs.get(job_id)


def list_jobs(
    *,
    status: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    filename: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Job], int]:
    with _lock:
        jobs = list(_jobs.values())

    completed = [j for j in jobs if j.status == "done" and j.result is not None]

    if status:
        completed = [j for j in completed if j.result.summary.status.upper() == status.upper()]
    if date_from:
        completed = [j for j in completed if j.created_at.date() >= date_from]
    if date_to:
        completed = [j for j in completed if j.created_at.date() <= date_to]
    if filename:
        needle = filename.lower()
        completed = [
            j
            for j in completed
            if needle in j.actual_filename.lower() or needle in j.expected_filename.lower()
        ]

    completed.sort(key=lambda j: j.created_at, reverse=True)

    total = len(completed)
    start = max(page - 1, 0) * page_size
    page_items = completed[start : start + page_size]
    return page_items, total


def rerun_job(job_id: str, *, ai_provider: AIProvider | None) -> str | None:
    original = get_job(job_id)
    if original is None:
        return None
    if not original.actual_stored_path.exists() or not original.expected_stored_path.exists():
        return None

    return submit_comparison_job(
        original.actual_stored_path.read_bytes(),
        original.actual_filename,
        original.expected_stored_path.read_bytes(),
        original.expected_filename,
        ai_provider=ai_provider,
        enable_visual=original.enable_visual,
        hide_variable_fills=original.hide_variable_fills,
    )


def _run_job(job: Job, ai_provider: AIProvider | None) -> None:
    try:
        job.result = compare_documents(
            str(job.actual_stored_path),
            str(job.expected_stored_path),
            ai_provider=ai_provider,
            enable_visual=job.enable_visual,
            hide_variable_fills=job.hide_variable_fills,
        )
        job.status = "done"
    except CoreError as e:
        job.error = str(e)
        job.status = "error"
    except Exception as e:
        job.error = f"Error inesperado: {e}"
        job.status = "error"
