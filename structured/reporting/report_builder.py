from datetime import datetime

class ReportBuilder:

    def build_summary(self, differences):

        critical = len([

            d for d in differences

            if d["severity"] == "CRITICO"
        ])

        warning = len([

            d for d in differences

            if d["severity"] == "AVISO"
        ])

        info = len([

            d for d in differences

            if d["severity"] == "INFO"
        ])

        status = "PASSED"

        if critical > 0:
            status = "FAILED"

        summary = {

            "total_differences": len(differences),

            "critical": critical,

            "warning": warning,

            "info": info,

            "status": status,

            "generated_at": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        }

        return summary