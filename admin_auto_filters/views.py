from django.http import JsonResponse
from django.contrib.admin.views.autocomplete import AutocompleteJsonView as Base


class AutocompleteJsonView(Base):
    """Overriding django admin's AutocompleteJsonView"""

    @staticmethod
    def display_text(obj):
        """
        Hook to specify means for converting object to string for endpoint.
        """
        return str(obj)

    def get(self, request, *args, **kwargs):
        self.term = request.GET.get('term', '')
        self.paginator_class = self.model_admin.paginator
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return JsonResponse({
            'results': [
                {'id': str(obj.pk), 'text': self.display_text(obj)}
                for obj in context['object_list']
            ],
            'pagination': {'more': context['page_obj'].has_next()},
        })

    def get_queryset(self):
        """Return queryset based on ModelAdmin.get_search_results()."""
        qs = self.model_admin.get_queryset(self.request)
        if hasattr(self.source_field, 'get_limit_choices_to'):
            qs = qs.complex_filter(self.source_field.get_limit_choices_to())
        elif hasattr(self.source_field, 'limit_choices_to'):
            qs = qs.complex_filter(self.source_field.limit_choices_to)
        qs, search_use_distinct = self.model_admin.get_search_results(self.request, qs, self.term)
        if search_use_distinct:
            qs = qs.distinct()
        return qs
