import ast
import importlib
import json

from apps.taken.models import Taakgebeurtenis, Taakopdracht
from apps.taken.tasks import task_fix_taakopdracht_issues
from django.contrib import admin, messages
from django.utils.safestring import mark_safe
from django_celery_results.admin import TaskResultAdmin
from django_celery_results.models import TaskResult

from .admin_filters import (
    AfgeslotenOpFilter,
    ResolutieFilter,
    StatusFilter,
    TitelFilter,
)


class TaakgebeurtenisAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "uuid",
        "taakstatus",
        "aangemaakt_op",
        "aangepast_op",
        "taakopdracht",
        "gebruiker",
        "meldinggebeurtenissen_aantal",
    )

    def meldinggebeurtenissen_aantal(self, obj):
        return obj.meldinggebeurtenissen_voor_taakgebeurtenis.count()

    meldinggebeurtenissen_aantal.short_description = "Meldinggebeurtenissen aantal"


@admin.action(description="Zet taak afgesloten_op voor afgesloten meldingen")
def action_set_taak_afgesloten_op_for_melding_afgesloten(modeladmin, request, queryset):
    for taakopdracht in queryset.all():
        if taakopdracht.melding.afgesloten_op and not taakopdracht.afgesloten_op:
            taakopdracht.afgesloten_op = taakopdracht.melding.afgesloten_op
            taakopdracht.save()


@admin.action(description="Fix problemen met taakopdrachten")
def action_task_fix_taakopdracht_issues(self, request, queryset):
    for taakopdracht in queryset.all():
        task_fix_taakopdracht_issues.delay(taakopdracht.id)
    self.message_user(
        request, f"Updating fixer taak for {len(queryset.all())} taakopdrachten!"
    )


class TaakopdrachtAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "taaktype",
        "taak_url",
        "uuid",
        "titel",
        "aangepast_op",
        "afgesloten_op",
        "pretty_afhandeltijd",
        "melding",
        "melding__afgesloten_op",
        "pretty_status",
        "resolutie",
    )
    actions = (
        action_set_taak_afgesloten_op_for_melding_afgesloten,
        action_task_fix_taakopdracht_issues,
    )
    list_filter = (
        StatusFilter,
        ResolutieFilter,
        AfgeslotenOpFilter,
        TitelFilter,
    )
    search_fields = [
        "melding__id",
    ]
    readonly_fields = (
        "uuid",
        "afhandeltijd",
        "pretty_afhandeltijd",
        "aangemaakt_op",
        "aangepast_op",
        "afgesloten_op",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "uuid",
                    "titel",
                    "melding",
                    "applicatie",
                    "taaktype",
                    "status",
                    "resolutie",
                    "bericht",
                    "additionele_informatie",
                    "taak_url",
                )
            },
        ),
        (
            "Tijden",
            {
                "fields": (
                    "aangemaakt_op",
                    "aangepast_op",
                    "afgesloten_op",
                    "pretty_afhandeltijd",
                )
            },
        ),
    )

    def melding__afgesloten_op(self, obj):
        if obj.melding.afgesloten_op:
            return obj.melding.afgesloten_op
        else:
            return "-"

    def pretty_status(self, obj):
        if obj.status:
            return obj.status.naam
        else:
            return "-"

    pretty_status.short_description = "Status"
    pretty_status.admin_order_field = "status__naam"

    def pretty_afhandeltijd(self, obj):
        if obj.afhandeltijd:
            days = obj.afhandeltijd.days
            total_seconds = obj.afhandeltijd.total_seconds()
            hours, remainder = divmod(total_seconds, 3600)
            remaining_hours = int(hours) % 24  # Remaining hours in the current day
            minutes, _ = divmod(remainder, 60)
            return f"{days} dagen, {remaining_hours} uur, {int(minutes)} minuten"
        else:
            return "-"

    pretty_afhandeltijd.short_description = "Afhandeltijd"


def retry_celery_task_admin_action(modeladmin, request, queryset):
    msg = ""
    for task_res in queryset:
        if task_res.status != "FAILURE":
            msg += f'{task_res.task_id} => Skipped. Not in "FAILURE" State<br>'
            continue
        try:
            task_actual_name = task_res.task_name.split(".")[-1]
            module_name = ".".join(task_res.task_name.split(".")[:-1])
            kwargs = json.loads(task_res.task_kwargs)
            if isinstance(kwargs, str):
                kwargs = kwargs.replace("'", '"')
                kwargs = json.loads(kwargs)
                if kwargs:
                    getattr(
                        importlib.import_module(module_name), task_actual_name
                    ).apply_async(kwargs=kwargs, task_id=task_res.task_id)
            if not kwargs:
                args = ast.literal_eval(ast.literal_eval(task_res.task_args))
                getattr(
                    importlib.import_module(module_name), task_actual_name
                ).apply_async(args, task_id=task_res.task_id)
            msg += f"{task_res.task_id} => Successfully sent to queue for retry.<br>"
        except Exception as ex:
            msg += f"{task_res.task_id} => Unable to process. Error: {ex}<br>"
    messages.info(request, mark_safe(msg))


retry_celery_task_admin_action.short_description = "Retry Task"


class CustomTaskResultAdmin(TaskResultAdmin):
    actions = [
        retry_celery_task_admin_action,
    ]


admin.site.unregister(TaskResult)
admin.site.register(TaskResult, CustomTaskResultAdmin)


admin.site.register(Taakopdracht, TaakopdrachtAdmin)
admin.site.register(Taakgebeurtenis, TaakgebeurtenisAdmin)
