from core.models import ChangeKind, ComparisonResult


class ConsoleReporter:

    def print_report(self, result: ComparisonResult):

        print("\n")
        print("=" * 50)
        print("ESTRUCTURA DEL DOCUMENTO")
        print("=" * 50)
        print(f"Método de descubrimiento: {result.structural.discovery_method.value}")
        print(f"Puntuación estructural: {result.structural.score}%")
        if result.structural.missing_sections:
            print(f"Secciones faltantes: {result.structural.missing_sections}")

        print("\n")
        print("=" * 50)
        print("DIFERENCIAS ENCONTRADAS")
        print("=" * 50)

        if not result.semantic.discrepancies:
            print("\nNo se encontraron diferencias.\n")
        else:
            for d in result.semantic.discrepancies:
                print(f"\nUbicación: {d.location}")
                print(f"Tipo: {d.change_type.value}")
                print(f"Esperado: {d.expected_text}")
                print(f"Actual: {d.actual_text}")
                print(f"Severidad: {d.severity.value if d.severity else 'SIN CLASIFICAR'}")
                if d.severity_reasoning:
                    print(f"Razón: {d.severity_reasoning}")
                cambios_reales = [c for c in d.internal_changes if c.kind == ChangeKind.REAL]
                rellenos = [c for c in d.internal_changes if c.kind != ChangeKind.REAL]

                if cambios_reales:
                    print("Cambios reales:")
                    for cambio in cambios_reales:
                        print(f"  - {cambio.description}")
                if rellenos:
                    print("Datos/montos rellenados:")
                    for relleno in rellenos:
                        print(f"  - {relleno.description}")
                print("-" * 50)

        if result.visual is not None:
            print("\n")
            print("=" * 50)
            print("ANÁLISIS VISUAL")
            print("=" * 50)
            if result.visual.available:
                print(f"Status: {result.visual.status}")
                print(result.visual.findings)
            else:
                print(f"No disponible: {result.visual.error}")

        print("\n")
        print("=" * 50)
        print(f"RESUMEN: {result.summary.status}")
        print("=" * 50)
        print(
            f"Total: {result.summary.total_discrepancies} | "
            f"Críticos: {result.summary.critical} | "
            f"Avisos: {result.summary.warning} | "
            f"Info: {result.summary.info}"
        )
