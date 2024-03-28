import json

import celery
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

DEFAULT_RETRY_DELAY = 2
MAX_RETRIES = 6

LOCK_EXPIRE = 5


class BaseTaskWithRetry(celery.Task):
    autoretry_for = (Exception,)
    max_retries = MAX_RETRIES
    default_retry_delay = DEFAULT_RETRY_DELAY


@shared_task(bind=True, base=BaseTaskWithRetry)
def task_notificatie_voor_signaal_melding_afgesloten(self, signaal_id):
    from apps.signalen.models import Signaal

    signaal_instantie = Signaal.objects.get(pk=signaal_id)
    signaal_instantie.notificatie_melding_afgesloten()

    return f"Signaal id: {signaal_instantie.pk}"


@shared_task(bind=True, base=BaseTaskWithRetry)
def task_notificatie_voor_melding_veranderd(
    self, applicatie_id, melding_url, notificatie_type
):
    from apps.applicaties.models import Applicatie

    applicatie = Applicatie.objects.get(pk=applicatie_id)
    notificatie_response = applicatie.melding_veranderd_notificatie_voor_applicatie(
        melding_url,
        notificatie_type,
    )
    return f"Applicatie id: {applicatie_id}, melding_url={melding_url}, notificatie_type={notificatie_type}, status code={notificatie_response.status_code}"


@shared_task(bind=True, base=BaseTaskWithRetry)
def convert_aanvullende_informatie_to_aanvullende_vragen(self, melding_ids):
    from apps.meldingen.models import Melding

    for melding_id in melding_ids:
        melding = Melding.objects.get(pk=melding_id)
        try:
            aanvullende_informatie = melding.aanvullende_informatie
            print(f"Aanvullende informatie: {aanvullende_informatie}")
            if aanvullende_informatie:
                lines = aanvullende_informatie.strip().split("\\n")
                print(f"Lines: {lines}")
                aanvullende_vragen = []
                question = None
                answers = []
                for line in lines:
                    if not line:
                        continue
                    if "?" in line:
                        if question:
                            aanvullende_vragen.append(
                                {"question": f"{question.strip()}?", "answers": answers}
                            )
                            answers = []
                        question, *temp_answers = line.split("?")
                        answers.extend(
                            [
                                ans.strip()
                                for ans in temp_answers
                                if ans and ans != "null"
                            ]
                        )
                    else:
                        answers.append(line)
                if question and answers:
                    print(f"Question: {question}")
                    aanvullende_vragen.append(
                        {"question": f"{question.strip()}?", "answers": answers}
                    )
                melding.aanvullende_vragen = json.dumps(aanvullende_vragen)
                print(f"Aanvullende vragen end: {melding.aanvullende_vragen}")
                melding.save()
        except Exception as e:
            print(
                f"Error converting aanvullende_informatie to aanvullende_vragen for melding {melding.pk}: {e}"
            )
            logger.error(
                f"Error converting aanvullende_informatie to aanvullende_vragen for melding {melding.pk}: {e}"
            )
