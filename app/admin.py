from django.contrib import admin

from app.models import User, AdminMessage

class Chat_ID_Filter(admin.SimpleListFilter):
    title = 'Фильтрация по ID телеграмма'
    parameter_name = 'ID телеграмма'

    def lookups(self, request, model_admin):
        return (
            ('Дмитрий', 'Дмитрий'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        return queryset.filter(chat_id='394151925')
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_filter = (Chat_ID_Filter,)

@admin.register(AdminMessage)
class AdminMessageAdmin(admin.ModelAdmin):
    pass