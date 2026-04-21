from products.models import Product
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, SearchHeadline
from django.db.models import Value


def search_q(query):
    find_q = SearchQuery(query)
    vector = SearchVector("name", "short_description")
    result = (
        Product.objects.visible().annotate(
            rank=SearchRank(vector, find_q, normalization=Value(1).bitor(Value(4)))
        )
        .order_by("-rank")
        .filter(rank__gt=0)
    )

    result = result.annotate(
        headline = SearchHeadline(
            'name',
            find_q,
            start_sel = '<span style="background-color: red;">',
            stop_sel = '</span>',
        )
    )

    result = result.annotate(
        bodyline = SearchHeadline(
            'short_description',
            find_q,
            start_sel = '<span style="background-color: red;">',
            stop_sel = '</span>',
        )
    )

    return result