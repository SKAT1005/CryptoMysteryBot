from django.contrib import admin

from app.models import User, AdminMessage


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass

@admin.register(AdminMessage)
class AdminMessageAdmin(admin.ModelAdmin):
    pass
