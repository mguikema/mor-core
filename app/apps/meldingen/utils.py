from urllib import parse

from django.db.models import Q


def get_q_objects_from_qs(query):
    d = parse.parse_qs(query)
    dll = [[(k, vv) for vv in v] for k, v in d.items()]
    q_objects = Q()
    for q in dll:
        inner = Q()
        for iq in q:
            inner |= Q(iq)
        q_objects &= inner
    return q_objects
