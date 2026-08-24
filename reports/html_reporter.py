from datetime import datetime

class HtmlReporter:

    def generate_report(
        self,
        differences,
        summary,
        analysis
    ):

        current_date = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        rows = ""

        for diff in differences:

            severity = diff["severity"]

            color = self.get_color(severity)

            rows += f"""
            <tr>
                <td>{diff['field']}</td>
                <td>{diff['expected']}</td>
                <td>{diff['actual']}</td>
                <td style="
                    color:{color};
                    font-weight:bold;
                ">
                    {severity}
                </td>
            </tr>
            """

        summary_section = f"""

        <h2>
            STATUS:
            <span style="
                color:
                {'red'
                if summary['status'] == 'FAILED'
                else 'green'};

                font-weight:bold;
            ">
                {summary['status']}
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
                        {summary['total_differences']}
                    </b>
                </li>

                <li>
                    Criticos:
                    <b>
                        {summary['critical']}
                    </b>
                </li>

                <li>
                    Avisos:
                    <b>
                        {summary['warning']}
                    </b>
                </li>

                <li>
                    Informativos:
                    <b>
                        {summary['info']}
                    </b>
                </li>

            </ul>

        </div>
        """

        ai_section = f"""

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
                Analisis IA
            </h2>

            <pre
                style="
                    white-space: pre-wrap;
                    font-family: Arial;
                "
            >
{analysis}
            </pre>

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
                {current_date}
            </p>

            {summary_section}

            

            <table>

                <thead>

                    <tr>
                        <th>Campo/Mencion</th>
                        <th>Esperado</th>
                        <th>Actual</th>
                        <th>Severidad</th>
                    </tr>

                </thead>

                <tbody>

                    {rows}

                </tbody>

            </table>
            
            {ai_section}

        </body>

        </html>
        """

        with open(
            "reports/report.html",
            "w",
            encoding="utf-8"
        ) as file:

            file.write(html)

    def get_color(self, severity):

        if severity == "CRITICO":
            return "red"

        if severity == "AVISO":
            return "orange"

        return "black"