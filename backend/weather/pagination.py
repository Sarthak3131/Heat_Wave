from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination


class StandardResultsPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        value = request.query_params.get(self.page_query_param)
        if value is not None:
            try:
                page_number = int(value)
            except (TypeError, ValueError) as exc:
                raise ValidationError(
                    {'page': 'Enter a positive whole page number.'}
                ) from exc
            if page_number < 1:
                raise ValidationError(
                    {'page': 'Enter a positive whole page number.'}
                )
        return super().paginate_queryset(queryset, request, view=view)

    def get_page_size(self, request):
        value = request.query_params.get(self.page_size_query_param)
        if value is None:
            return self.page_size
        try:
            page_size = int(value)
        except (TypeError, ValueError) as exc:
            raise ValidationError(
                {'page_size': 'Enter a whole number between 1 and 100.'}
            ) from exc
        if not 1 <= page_size <= self.max_page_size:
            raise ValidationError(
                {'page_size': 'Enter a whole number between 1 and 100.'}
            )
        return page_size
