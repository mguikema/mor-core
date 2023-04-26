from prometheus_client import Counter


class Metrics:
    morcore_meldingen_aantal = Counter(
        "morcore_meldingen_total",
        "aantal status veranderingen",
        [
            "onderwerp",
            "status",
            "actie",
        ],
    )
