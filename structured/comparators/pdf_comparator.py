from structured.validators.business_rules import BusinessRules

class PdfComparator:

    def compare(self, expected_data, actual_data):

        differences = []

        for key in expected_data:
            
            if key in BusinessRules.IGNORED_FIELDS:
                continue

            expected_value = expected_data.get(key)
            actual_value = actual_data.get(key)

            if expected_value != actual_value:

                severity = self.get_severity(key)

                differences.append({
                    "field": key,
                    "expected": expected_value,
                    "actual": actual_value,
                    "severity": severity
                })

        return differences

    def get_severity(self, field):

        if field in BusinessRules.CRITICAL_FIELDS:
            return "CRITICO"

        if field in BusinessRules.WARNING_FIELDS:
            return "AVISO"

        return "INFO"