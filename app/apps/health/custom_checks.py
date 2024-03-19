import logging

from apps.applicaties.models import Applicatie
from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import HealthCheckException

logger = logging.getLogger(__name__)


class ApplicatieTokenAPIHealthCheck(BaseHealthCheckBackend):
    critical_service = False

    def check_status(self):
        results = []
        result_waardes = (
            "Niet compleet",
            "Ok",
            "Niet ok",
        )
        result_waardes_niet_ok = (
            result_waardes[0],
            result_waardes[2],
        )
        for applicatie in Applicatie.objects.all():
            r = {
                "token": None,
                "naam": applicatie.naam,
                "applicatie_data_exists": (
                    applicatie.applicatie_gebruiker_naam
                    and applicatie.applicatie_gebruiker_wachtwoord
                    and applicatie.basis_url
                ),
                "result": None,
            }
            try:
                r["token"] = applicatie._get_token()
            except Exception as e:
                logger.error(
                    f"Error fetching token for applicatie={applicatie.naam}, e={e}"
                )

            r["result"] = (
                result_waardes[0]
                if not r.get("applicatie_data_exists")
                else result_waardes[1]
                if r.get("token")
                else result_waardes[2]
            )
            results.append(r)

        niet_ok_results = ", ".join(
            [
                f"{r.get('naam')}({r.get('result')})"
                for r in results
                if r.get("result") in result_waardes_niet_ok
            ]
        )
        if niet_ok_results:
            raise HealthCheckException(niet_ok_results)

    def identifier(self):
        return self.__class__.__name__
