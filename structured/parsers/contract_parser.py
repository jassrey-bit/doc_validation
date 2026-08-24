import re

class ContractParser:

    def parse(self, text):

        data = {}

        monto = re.search(
            r"Monto solicitado:\s*\$([\d,]+)",
            text
        )

        cliente = re.search(
            r"Cliente:\s*(.*)",
            text
        )

        tasa = re.search(
            r"Tasa:\s*([\d.]+)",
            text
        )

        if monto:
            data["monto"] = monto.group(1)

        if cliente:
            data["cliente"] = cliente.group(1)

        if tasa:
            data["tasa"] = tasa.group(1)

        return data