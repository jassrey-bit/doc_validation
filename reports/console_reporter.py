class ConsoleReporter:

    def print_report(self, differences):

        print("\n")
        print("=" * 50)
        print("DIFERENCIAS ENCONTRADAS")
        print("=" * 50)

        if not differences:

            print("\nNo se encontraron diferencias.\n")
            return

        for difference in differences:

            print(f"\nCampo: {difference['field']}")

            print(
                f"Esperado: {difference['expected']}"
            )

            print(
                f"Actual: {difference['actual']}"
            )

            print(
                f"Severidad: {difference['severity']}"
            )

            print("-" * 50)