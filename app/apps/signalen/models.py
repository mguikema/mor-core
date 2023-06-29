from apps.applicaties.models import Applicatie
from django.contrib.gis.db import models
from utils.models import BasisModel


class Signaal(BasisModel):
    """
    Een signaal een individuele signaal vanuit de buiten ruimte.
    Er kunnen meerdere signalen aan een melding gekoppeld zijn, bijvoorbeeld dubbele signalen.
    Maar er altijd minimaal een signaal gerelateerd aan een Melding.
    Er mag binnen deze applicatie geen extra info over een signaal

    Het verwijzing veld, moet nog nader bepaald worden. Vermoedelijk wordt dit een url
    """

    signaal_url = models.URLField()
    signaal_data = models.JSONField(default=dict)
    melder = models.OneToOneField(
        to="melders.Melder", on_delete=models.SET_NULL, null=True, blank=True
    )
    melding = models.ForeignKey(
        to="meldingen.Melding",
        related_name="signalen_voor_melding",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    def notificatie_melding_afgesloten(self):
        applicatie = Applicatie.vind_applicatie_obv_uri(self.signaal_url)
        applicatie.notificatie_melding_afgesloten(self.signaal_url)

    class Meta:
        verbose_name = "Signaal"
        verbose_name_plural = "Signalen"
