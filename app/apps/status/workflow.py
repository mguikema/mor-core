"""
Model the workflow of responding to a Signal (melding) as state machine.
"""
# Note on historical states: to leave the historical data intact, old states are
# retained below (but made unreachable if at all possible).

# Internal statusses
LEEG = ""
GEMELD = "gemeld"
AFWACHTING = "afwachting"
IN_BEHANDELING = "in_behandeling"
ON_HOLD = "on_hold"
AFGEHANDELD = "afgehandeld"
GEANNULEERD = "geannuleerd"
GESPLITST = "gesplitst"
HEROPEND = "heropend"
VERZOEK_TOT_AFHANDELING = "verzoek_tot_afhandeling"
INGEPLAND = "ingepland"
VERZOEK_TOT_HEROPENEN = "verzoek_tot_heropenen"
REACTIE_GEVRAAGD = "Reactie gevraagd"
REACTIE_ONTVANGEN = "Reactie ontvangen"

# Statusses to track progress in external systems
TE_VERZENDEN = "te_verzenden"
VERZONDEN = "verzonden"
VERZENDEN_MISLUKT = "verzenden_mislukt"
AFGEHANDELD_EXTERN = "afgehandeld_extern"

# Choices for the API/Serializer layer. Users that can change the state via the API are only allowed
# to use one of the following choices.
STATUS_CHOICES_API = (
    (GEMELD, "Nieuw"),
    (AFWACHTING, "In afwachting van behandeling"),
    (IN_BEHANDELING, "In behandeling"),
    (ON_HOLD, "On hold"),
    (INGEPLAND, "Ingepland"),
    (TE_VERZENDEN, "Extern: te verzenden"),
    (AFGEHANDELD, "Afgehandeld"),
    (GEANNULEERD, "Geannuleerd"),
    (HEROPEND, "Heropend"),
    (GESPLITST, "Gesplitst"),
    (VERZOEK_TOT_AFHANDELING, "Extern: verzoek tot afhandeling"),
    (REACTIE_GEVRAAGD, "Reactie gevraagd"),
    (REACTIE_ONTVANGEN, "Reactie ontvangen"),
)

# Choices used by the application. These choices can be set from within the application, not via the
# API/Serializer layer.
STATUS_CHOICES_APP = (
    (VERZONDEN, "Extern: verzonden"),
    (VERZENDEN_MISLUKT, "Extern: mislukt"),
    (AFGEHANDELD_EXTERN, "Extern: afgehandeld"),
    (VERZOEK_TOT_HEROPENEN, "Verzoek tot heropenen"),
)

# All allowed choices, used for the model `Status`.
STATUS_CHOICES = STATUS_CHOICES_API + STATUS_CHOICES_APP

ALLOWED_STATUS_CHANGES = {
    LEEG: [GEMELD],
    GEMELD: [
        # IN_BEHANDELING,
        AFGEHANDELD,
        GEANNULEERD,
    ],
    AFWACHTING: [
        GEMELD,
        AFWACHTING,
        INGEPLAND,
        VERZOEK_TOT_AFHANDELING,
        AFGEHANDELD,
        TE_VERZENDEN,
        IN_BEHANDELING,
        GEANNULEERD,
        REACTIE_GEVRAAGD,
    ],
    IN_BEHANDELING: [
        AFGEHANDELD,
        GEANNULEERD,
    ],
    INGEPLAND: [
        GEMELD,
        INGEPLAND,
        IN_BEHANDELING,
        AFGEHANDELD,
        GEANNULEERD,
        VERZOEK_TOT_AFHANDELING,
        REACTIE_GEVRAAGD,
    ],
    ON_HOLD: [
        INGEPLAND,
        GEANNULEERD,
    ],
    TE_VERZENDEN: [
        VERZONDEN,
        VERZENDEN_MISLUKT,
        GEANNULEERD,
    ],
    VERZONDEN: [
        AFGEHANDELD_EXTERN,
        GEANNULEERD,
    ],
    VERZENDEN_MISLUKT: [
        GEMELD,
        TE_VERZENDEN,
        GEANNULEERD,
    ],
    AFGEHANDELD_EXTERN: [
        AFGEHANDELD,
        GEANNULEERD,
        IN_BEHANDELING,
    ],
    AFGEHANDELD: [
        # HEROPEND,
        # VERZOEK_TOT_HEROPENEN,
    ],
    GEANNULEERD: [
        # GEANNULEERD,
        # HEROPEND,
        # IN_BEHANDELING,
    ],
    HEROPEND: [
        HEROPEND,
        IN_BEHANDELING,
        AFGEHANDELD,
        GEANNULEERD,
        TE_VERZENDEN,
        GEMELD,
        REACTIE_GEVRAAGD,
    ],
    GESPLITST: [],
    VERZOEK_TOT_AFHANDELING: [
        GEMELD,
        VERZOEK_TOT_AFHANDELING,
        AFWACHTING,
        AFGEHANDELD,
        GEANNULEERD,
        IN_BEHANDELING,
    ],
    VERZOEK_TOT_HEROPENEN: [
        GEMELD,
        AFGEHANDELD,
        HEROPEND,
        GEANNULEERD,
    ],
    REACTIE_GEVRAAGD: [
        GEMELD,
        AFWACHTING,
        IN_BEHANDELING,
        INGEPLAND,
        AFGEHANDELD,
        GEANNULEERD,
        REACTIE_GEVRAAGD,
        REACTIE_ONTVANGEN,
        TE_VERZENDEN,
    ],
    REACTIE_ONTVANGEN: [
        GEMELD,
        AFWACHTING,
        IN_BEHANDELING,
        AFGEHANDELD,
        GEANNULEERD,
        INGEPLAND,
        REACTIE_GEVRAAGD,
        TE_VERZENDEN,
    ],
}
