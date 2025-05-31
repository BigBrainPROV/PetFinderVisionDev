from django_filters.rest_framework import (
    BaseInFilter,
    DjangoFilterBackend,
    NumberFilter,
)


class NumberInFilter(BaseInFilter, NumberFilter):
    pass


class FilterBackend(DjangoFilterBackend):
    def get_filterset_kwargs(self, request, queryset, view):
        kwargs = super().get_filterset_kwargs(request, queryset, view)

        if hasattr(view, "get_filterset_kwargs"):
            kwargs.update(view.get_filterset_kwargs())

        return kwargs
