from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination for most views
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class SmallResultsSetPagination(PageNumberPagination):
    """
    Smaller pagination for data-intensive views
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

