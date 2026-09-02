from __future__ import annotations

import shutil
import tempfile
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from threading import Lock

from core import AIProvider, ComparisonResult, compare_documents
from core.exceptions import CoreError

_executor = ThreadPoolExecutor(max_workers=2)
_jobs: dict[str, "Job"] = {}
_lock = Lock()


@dataclass
class Job:
    id: str
    status: str = "pending"  # pending | done | error
    result: ComparisonResult | None = None
    error: str | None = None


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
    job = Job(id=job_id)
    with _lock:
        _jobs[job_id] = job

    _executor.submit(
        _run_job,
        job,
        actual_bytes,
        actual_filename,
        expected_bytes,
        expected_filename,
        ai_provider,
        enable_visual,
        hide_variable_fills,
    )
    return job_id


def get_job(job_id: str) -> Job | None:
    with _lock:
        return _jobs.get(job_id)


def _run_job(
    job: Job,
    actual_bytes: bytes,
    actual_filename: str,
    expected_bytes: bytes,
    expected_filename: str,
    ai_provider: AIProvider | None,
    enable_visual: bool,
    hide_variable_fills: bool,
) -> None:
    tmp_dir = tempfile.mkdtemp(prefix="api_comparison_")
    try:
        actual_path = Path(tmp_dir) / f"actual_{actual_filename}"
        expected_path = Path(tmp_dir) / f"expected_{expected_filename}"
        actual_path.write_bytes(actual_bytes)
        expected_path.write_bytes(expected_bytes)

        job.result = compare_documents(
            str(actual_path),
            str(expected_path),
            ai_provider=ai_provider,
            enable_visual=enable_visual,
            hide_variable_fills=hide_variable_fills,
        )
        job.status = "done"
    except CoreError as e:
        job.error = str(e)
        job.status = "error"
    except Exception as e:
        job.error = f"Error inesperado: {e}"
        job.status = "error"
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
