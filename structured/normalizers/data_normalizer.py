class DataNormalizer:

    def normalize(self, data):

        normalized = {}

        for key, value in data.items():

            if key == "monto":

                normalized[key] = self.normalize_currency(value)

            elif key == "tasa":

                normalized[key] = self.normalize_decimal(value)

            else:

                normalized[key] = value.strip()

        return normalized

    def normalize_currency(self, value):

        value = value.replace(",", "")
        value = value.replace("$", "")

        return float(value)

    def normalize_decimal(self, value):

        return round(float(value), 2)