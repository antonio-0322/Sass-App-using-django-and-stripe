from rest_framework import pagination


class DynamicPageSizePagination(pagination.PageNumberPagination):
    page_size_query_param = 'page_size'
