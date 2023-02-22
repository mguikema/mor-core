from django.contrib.gis.db import models
from PIL import Image, UnidentifiedImageError

# class Orchestrator(models.Model):
#     """
#     Orchestrator manages one or more IncidentHandlers
#     It can darefor follow an Melding
#     """


# class ProccessProposalTemplate(models.Model):
#     """
#     Created by task managers
#     """
#     proccess_proposal_name = models.CharField(
#         max_length=100
#     )
#     default_proccess_proposal = models.BooleanField(
#         default=False
#     )
#     incident_handler = models.ForeignKey(
#         to="mor.TaakApplicatie",
#         related_name="proccess_proposal_templates",
#         on_delete=models.CASCADE,
#     )

#     def __str__(self):
#         return self.proccess_proposal_name


# class ProccessProposalItemTemplate(models.Model):
#     """
#     When a ProccessProposalTemplate instance is created, at least one ProccessProposalItemTemplate item should be added to ProccessProposalTemplate
#     """
#     status_name = models.CharField(max_length=50,)
#     timedelta = models.DurationField()
#     proccess_proposal_template = models.ForeignKey(
#         to="mor.ProccessProposalTemplate",
#         related_name="items",
#         on_delete=models.CASCADE,
#     )

#     class Meta:
#         ordering = ("timedelta",)

#     def __str__(self):
#         return f"{self.status_name}: {self.timedelta}"


# class ProccessProposal(models.Model):
#     """
#     A ProccessProposal is a concrete represention of a ProccessProposalTemplate
#     When an Melding is assigned to the TaakApplicatie, a ProccessProposal is created based on the default ProccessProposalTemplate of the responsable TaakApplicatie,
#     """
#     proccess_proposal_template = models.ForeignKey(
#         to="mor.ProccessProposalTemplate",
#         related_name="proccess_proposals",
#         on_delete=models.SET_NULL,
#         null=True
#     )
#     melding = models.OneToOneField(
#         to="mor.Melding",
#         related_name="proccess_proposal",
#         on_delete=models.CASCADE,
#         null=True
#     )

#     def __str__(self):
#         return f"Template: {self.proccess_proposal_template}"


# class ProccessProposalItem(models.Model):
#     proccess_proposal = models.ForeignKey(
#         to="mor.ProccessProposal",
#         related_name="items",
#         on_delete=models.CASCADE,
#     )
#     status_name = models.CharField(max_length=50,)
#     expected_completion = models.DateTimeField()

#     def __str__(self):
#         return self.status_name


class Bijlage(models.Model):
    incident_gebeurtenis = models.ForeignKey(
        to="mor.MeldingGebeurtenis",
        related_name="bijlages",
        on_delete=models.CASCADE,
    )
    bestand = models.FileField(
        upload_to="attachments/%Y/%m/%d/", null=False, blank=False, max_length=255
    )
    mimetype = models.CharField(max_length=30, blank=False, null=False)
    is_afbeelding = models.BooleanField(default=False)

    def _is_afbeelding(self):
        try:
            Image.open(self.bestand)
        except UnidentifiedImageError:
            return False
        return True

    def save(self, *args, **kwargs):
        if self.pk is None:
            # Check of het bestand een afbeelding is
            self.is_afbeelding = self._is_afbeelding()

            if not self.mimetype and hasattr(self.bestand.file, "content_type"):
                self.mimetype = self.bestand.file.content_type

        super().save(*args, **kwargs)


class TaakApplicatie(models.Model):
    """
    Representeerd externe applicaite die de afhandling van de melden op zich nemen.
    """

    naam = models.CharField(
        max_length=100,
        default="Taak applicatie",
    )


class MeldingGebeurtenisType(models.Model):
    type_naam = models.CharField(
        max_length=50,
        choices=(
            ("proccess_proposal_item_completion", "proccess_proposal_item_completion"),
            ("incident_handler_change", "incident_handler_change"),
            ("status_change", "status_change"),
            ("meta_data_change", "meta_data_change"),
        ),
    )
    incident_gebeurtenis = models.ForeignKey(
        to="mor.MeldingGebeurtenis",
        related_name="melding_gebeurtenistypes",
        on_delete=models.CASCADE,
    )
    meta = models.JSONField(default=dict)


class MeldingGebeurtenis(models.Model):
    """
    MeldingGebeurtenissen bouwen de history op van van de melding
    """

    aangemaakt = models.DateTimeField(auto_now_add=True)
    melding = models.ForeignKey(
        to="mor.Melding",
        related_name="melding_gebeurtenissen",
        on_delete=models.CASCADE,
    )


class Geometrie(models.Model):
    """
    Basis klasse voor geo info.
    """

    geometrie = models.GeometryField()
    meta = models.JSONField(default=dict)
    melding = models.ForeignKey(
        to="mor.Melding",
        related_name="geometrieen",
        on_delete=models.CASCADE,
        null=True,
    )


class Signaal(models.Model):
    """
    Een signaal een individuele signaal vanuit de buiten ruimte.
    Er kunnen meerdere signalen aan een melding gekoppeld zijn, bijvoorbeeld dubbele signalen.
    Maar er altijd minimaal een signaal gerelateerd aan een Melding.
    Er mag binnen deze applicatie geen extra info over een signaal

    Het verwijzing veld, moet nog nader bepaald worden. Vermoedelijk wordt dit een url
    """

    verwijzing = models.TextField()
    melding = models.ForeignKey(
        to="mor.Melding", related_name="signalen", on_delete=models.CASCADE, null=True
    )


class Melding(models.Model):
    """
    Een melding is de ontdubbelde versie van signalen
    """

    aangemaakt = models.DateTimeField(auto_now_add=True)

    """
    If the incident_handler field is empty, no one is responsable for the melding
    Maybe an orchestrator like  MidOffice can be connected automaticaly


    """
    taak_applicaties = models.ManyToManyField(
        to="mor.TaakApplicatie",
        related_name="meldingen",
    )
