from __future__ import annotations

import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from threading import Lock

from core import AIProvider, ComparisonResult, compare_documents
from core.exceptions import CoreError, VisualUnavailableError
from core.visual import convert_docx_to_pdf, render_pdf_to_images

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
    actual_page_count: int = 0
    expected_page_count: int = 0
    pages_error: str | None = None

    @property
    def dir(self) -> Path:
        return STORAGE_DIR / self.id

    @property
    def actual_stored_path(self) -> Path:
        return self.dir / f"actual_{self.actual_filename}"

    @property
    def expected_stored_path(self) -> Path:
        return self.dir / f"expected_{self.expected_filename}"

    @property
    def actual_pages_dir(self) -> Path:
        return self.dir / "pages" / "actual"

    @property
    def expected_pages_dir(self) -> Path:
        return self.dir / "pages" / "expected"

    @property
    def actual_render_pdf_path(self) -> Path:
        """PDF que un visor (pdf.js) puede cargar para este lado: el archivo
        original si ya es PDF, o el PDF convertido y persistido si era DOCX."""
        if self.actual_stored_path.suffix.lower() == ".pdf":
            return self.actual_stored_path
        return self.actual_pages_dir / "document.pdf"

    @property
    def expected_render_pdf_path(self) -> Path:
        if self.expected_stored_path.suffix.lower() == ".pdf":
            return self.expected_stored_path
        return self.expected_pages_dir / "document.pdf"


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


def _persist_pages(document_path: Path, output_dir: Path) -> int:
    """Renderiza cada página del documento a PNG y las deja en `output_dir`
    como `page_1.png`, `page_2.png`, ... (nombres estables para servirlas por
    número de página, sin importar el nombre original del archivo).

    Si el documento es DOCX, además persiste el PDF intermedio (generado por
    LibreOffice) como `document.pdf` en vez de descartarlo, para que un
    visor en el navegador (pdf.js) pueda cargarlo directamente — con texto
    seleccionable y posiciones reales, no solo la imagen rasterizada."""
    output_dir.mkdir(parents=True, exist_ok=True)
    ext = document_path.suffix.lower()

    if ext == ".docx":
        converted = Path(convert_docx_to_pdf(str(document_path), str(output_dir)))
        source_pdf = output_dir / "document.pdf"
        if converted != source_pdf:
            converted.replace(source_pdf)
    elif ext == ".pdf":
        source_pdf = document_path
    else:
        raise VisualUnavailableError(f"Formato de archivo no soportado para render visual: '{ext}'")

    images = render_pdf_to_images(source_pdf, output_dir)
    page_names = set()
    for i, img_path in enumerate(images, start=1):
        target = output_dir / f"page_{i}.png"
        if img_path != target:
            img_path.replace(target)
        page_names.add(target.name)

    # limpia cualquier otro subproducto, conservando solo las páginas y (si
    # aplica) el PDF convertido que acabamos de persistir a propósito.
    keep = page_names | ({"document.pdf"} if ext == ".docx" else set())
    for leftover in output_dir.iterdir():
        if leftover.name not in keep:
            leftover.unlink(missing_ok=True)

    return len(images)


def _run_job(job: Job, ai_provider: AIProvider | None) -> None:
    # `compare_documents` (que incluye las llamadas a IA cuando aplica —
    # de lejos lo más lento del pipeline, decenas de segundos) y el render
    # de páginas para el visor no dependen entre sí: ambos solo necesitan
    # los archivos que ya se guardaron en disco. Antes corrían en secuencia,
    # sumando la conversión de LibreOffice del render de páginas (que
    # incluye su propia llamada a soffice) al tiempo total de espera; ahora
    # corren en paralelo para que ese trabajo quede oculto dentro de la
    # espera, ya de por sí larga, de la IA.
    with ThreadPoolExecutor(max_workers=3) as pool:
        compare_future = pool.submit(
            compare_documents,
            str(job.actual_stored_path),
            str(job.expected_stored_path),
            ai_provider=ai_provider,
            enable_visual=job.enable_visual,
            hide_variable_fills=job.hide_variable_fills,
        )
        actual_pages_future = pool.submit(_persist_pages, job.actual_stored_path, job.actual_pages_dir)
        expected_pages_future = pool.submit(_persist_pages, job.expected_stored_path, job.expected_pages_dir)

        try:
            job.result = compare_future.result()
        except CoreError as e:
            job.error = str(e)
            job.status = "error"
        except Exception as e:
            job.error = f"Error inesperado: {e}"
            job.status = "error"

        # El render de páginas se espera antes de marcar el job como "done"
        # (aunque la comparación haya fallado): si el estado cambiara a
        # "done" primero, un cliente que consulte el job justo en ese
        # instante vería un resultado completo pero con `pages` a medio
        # llenar (p.ej. expected_count en 0 aunque sí exista, solo que aún
        # no terminó).
        try:
            job.actual_page_count = actual_pages_future.result()
            job.expected_page_count = expected_pages_future.result()
        except Exception as e:
            job.pages_error = str(e)

    if job.status != "error":
        job.status = "done"
