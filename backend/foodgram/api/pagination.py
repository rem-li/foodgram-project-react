from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })

    def paginate_queryset(self, queryset, request, view=None):
        limit = request.query_params.get('limit', None)
        recipes_limit = request.query_params.get(
            'recipes_limit', None
        )

        if limit is not None:
            try:
                self.page_size = int(limit)
            except (TypeError, ValueError):
                pass

        page = super().paginate_queryset(
            queryset, request, view
        )

        if recipes_limit is not None:
            try:
                recipes_limit = int(recipes_limit)
                for obj in page:
                    obj.recipes = obj.recipes[
                        :recipes_limit
                    ]
            except (TypeError, ValueError):
                pass

        return page
