import shutil
import subprocess
import tempfile
from pathlib import Path

import fitz  # PyMuPDF

from core.exceptions import VisualUnavailableError

_COMMON_WINDOWS_PATHS = [
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
]


def find_soffice() -> str | None:
    """Localiza el ejecutable de LibreOffice: PATH primero, rutas comunes de Windows después."""
    found = shutil.which("soffice")
    if found:
        return found
    for candidate in _COMMON_WINDOWS_PATHS:
        if Path(candidate).exists():
            return candidate
    return None


def convert_docx_to_pdf(docx_path: str | Path, output_dir: str | Path, timeout: int = 60) -> Path:
    """Convierte un DOCX a PDF vía LibreOffice headless (sin depender de MS Word)."""
    soffice = find_soffice()
    if soffice is None:
        raise VisualUnavailableError(
            "LibreOffice (soffice) no está instalado o no está en PATH; "
            "no se puede generar la vista visual de archivos DOCX."
        )

    # Cada conversión usa su propio perfil de usuario temporal: LibreOffice no
    # admite dos instancias simultáneas sobre el mismo perfil (la segunda
    # termina sin convertir y sin mensaje de error), y un job convierte hasta
    # cuatro DOCX a la vez (render de páginas + análisis visual, actual y expected).
    profile_dir = tempfile.mkdtemp(prefix="lo_profile_")
    try:
        result = subprocess.run(
            [
                soffice,
                f"-env:UserInstallation={Path(profile_dir).as_uri()}",
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                str(output_dir),
                str(Path(docx_path).resolve()),
            ],
            capture_output=True,
            timeout=timeout,
            text=True,
        )
    except subprocess.TimeoutExpired as e:
        raise VisualUnavailableError(f"LibreOffice tardó demasiado en convertir '{docx_path}'") from e
    except Exception as e:
        raise VisualUnavailableError(f"Fallo al invocar LibreOffice: {e}") from e
    finally:
        shutil.rmtree(profile_dir, ignore_errors=True)

    expected_pdf = Path(output_dir) / (Path(docx_path).stem + ".pdf")
    if result.returncode != 0 or not expected_pdf.exists():
        detalle = result.stderr.strip() or result.stdout.strip() or f"código de salida {result.returncode}"
        raise VisualUnavailableError(f"LibreOffice no pudo convertir '{docx_path}' a PDF: {detalle}")

    return expected_pdf


def render_pdf_to_images(pdf_path: str | Path, output_dir: str | Path, zoom: float = 2.0) -> list[Path]:
    """Renderiza cada página de un PDF a una imagen PNG de alta resolución para IA."""
    rutas_imagenes: list[Path] = []
    nombre_base = Path(pdf_path).stem
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        raise VisualUnavailableError(f"No se pudo abrir '{pdf_path}' para renderizar imágenes: {e}") from e

    try:
        for num_pagina in range(len(doc)):
            pagina = doc.load_page(num_pagina)
            pix = pagina.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
            ruta_img = output_dir / f"{nombre_base}_pag_{num_pagina + 1}.png"
            pix.save(ruta_img)
            rutas_imagenes.append(ruta_img)
    finally:
        doc.close()

    return rutas_imagenes


def convert_document_to_images(file_path: str | Path, output_dir: str | Path) -> list[Path]:
    """
    Convierte un documento (PDF o DOCX) a una lista de imágenes PNG, una por
    página. Para DOCX pasa primero por LibreOffice headless.
    """
    ext = Path(file_path).suffix.lower()

    if ext == ".docx":
        pdf_path = convert_docx_to_pdf(file_path, output_dir)
    elif ext == ".pdf":
        pdf_path = Path(file_path)
    else:
        raise VisualUnavailableError(f"Formato de archivo no soportado para render visual: '{ext}'")

    return render_pdf_to_images(pdf_path, output_dir)
