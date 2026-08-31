from pathlib import Path

from core.models import ChangeKind, ComparisonResult


class HtmlReporter:

    def _lista_html(self, descripciones: list[str]) -> str:
        if not descripciones:
            return "&mdash;"
        items = "".join(f"<li>{d}</li>" for d in descripciones)
        return f'<ul style="margin:0; padding-left:18px;">{items}</ul>'

    def generate_report(
        self,
        result: ComparisonResult,
        output_path: str | Path = "reports/report.html",
    ):

        rows = ""

        for d in result.semantic.discrepancies:

            severity = d.severity.value if d.severity else "SIN CLASIFICAR"
            color = self.get_color(severity)

            cambios_reales = [c.description for c in d.internal_changes if c.kind == ChangeKind.REAL]
            rellenos = [c.description for c in d.internal_changes if c.kind != ChangeKind.REAL]

            rows += f"""
            <tr>
                <td>{d.location}</td>
                <td>{d.change_type.value}</td>
                <td>{d.expected_text}</td>
                <td>{d.actual_text}</td>
                <td>{self._lista_html(cambios_reales)}</td>
                <td>{self._lista_html(rellenos)}</td>
                <td style="
                    color:{color};
                    font-weight:bold;
                ">
                    {severity}
                </td>
            </tr>
            """

        structural_section = f"""

        <div
            style="
                background:#f4f4f4;
                padding:15px;
                border-radius:10px;
                margin-top:20px;
                margin-bottom:20px;
            "
        >

            <h3>Estructura del Documento</h3>

            <ul>
                <li>Método de descubrimiento: <b>{result.structural.discovery_method.value}</b></li>
                <li>Puntuación estructural: <b>{result.structural.score}%</b></li>
                <li>Secciones esperadas: <b>{len(result.structural.expected_sections)}</b></li>
                <li>Secciones faltantes: <b>{result.structural.missing_sections or "Ninguna"}</b></li>
            </ul>

        </div>
        """

        summary_section = f"""

        <h2>
            STATUS:
            <span style="
                color:
                {'red'
                if result.summary.status == 'FAILED'
                else 'green'};

                font-weight:bold;
            ">
                {result.summary.status}
            </span>
        </h2>

        <div
            style="
                background:#f4f4f4;
                padding:15px;
                border-radius:10px;
                margin-top:20px;
                margin-bottom:20px;
            "
        >

            <h3>Resumen Ejecutivo</h3>

            <ul>

                <li>
                    Total Diferencias:
                    <b>
                        {result.summary.total_discrepancies}
                    </b>
                </li>

                <li>
                    Criticos:
                    <b>
                        {result.summary.critical}
                    </b>
                </li>

                <li>
                    Avisos:
                    <b>
                        {result.summary.warning}
                    </b>
                </li>

                <li>
                    Informativos:
                    <b>
                        {result.summary.info}
                    </b>
                </li>

            </ul>

        </div>
        """

        if result.visual is None:
            visual_section = ""
        elif result.visual.available:
            visual_section = f"""

            <div
                style="
                    margin-top:30px;
                    padding:20px;
                    background:#f8f9fa;
                    border-left:6px solid #007bff;
                    border-radius:10px;
                "
            >

                <h2>
                    Análisis Visual (IA)
                </h2>

                <pre
                    style="
                        white-space: pre-wrap;
                        font-family: Arial;
                    "
                >
{result.visual.findings}
                </pre>

            </div>
            """
        else:
            visual_section = f"""

            <div
                style="
                    margin-top:30px;
                    padding:20px;
                    background:#fff3cd;
                    border-left:6px solid #ffc107;
                    border-radius:10px;
                "
            >

                <h2>
                    Análisis Visual (IA)
                </h2>

                <p>
                    No disponible: {result.visual.error}
                </p>

            </div>
            """

        html = f"""
        <html>

        <head>

            <title>PDF Comparison Report</title>

            <style>

                body {{
                    font-family: Arial;
                    padding: 20px;
                    background-color: #ffffff;
                }}

                h1 {{
                    color: #333;
                }}

                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }}

                th, td {{
                    border: 1px solid #ccc;
                    padding: 10px;
                    text-align: left;
                }}

                th {{
                    background-color: #f4f4f4;
                }}

            </style>

        </head>

        <body>

            <h1>
                Reporte Validación de Documento
            </h1>

            <p>
                Generado durante:
                {result.summary.generated_at.strftime("%Y-%m-%d %H:%M:%S")}
            </p>

            <p>
                {result.expected_path} (esperado) vs. {result.actual_path} (actual)
            </p>

            {summary_section}

            {structural_section}

            <table>

                <thead>

                    <tr>
                        <th>Ubicación</th>
                        <th>Tipo</th>
                        <th>Esperado</th>
                        <th>Actual</th>
                        <th>Cambios Reales</th>
                        <th>Datos/Montos Rellenados</th>
                        <th>Severidad</th>
                    </tr>

                </thead>

                <tbody>

                    {rows}

                </tbody>

            </table>

            {visual_section}

        </body>

        </html>
        """

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as file:
            file.write(html)

    def get_color(self, severity):

        if severity == "CRITICO":
            return "red"

        if severity == "AVISO":
            return "orange"

        return "black"
