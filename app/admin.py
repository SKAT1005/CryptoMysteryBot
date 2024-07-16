from django.contrib import admin

from app.models import User, History, Wallet


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['id']

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['chat_id']
    search_fields = ['chat_id']
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term != '':
            queryset |= self.model.objects.filter(chat_id=search_term)
        return queryset.distinct(), use_distinct  # adding distinct()

@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'user']
    search_fields = ['id']

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term != '':
            queryset |= self.model.objects.filter(user__chat_id__icontains=search_term)
        return queryset.distinct(), use_distinct  # adding distinct()
