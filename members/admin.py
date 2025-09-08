from django.contrib import admin
from .models import Member

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'status', 'membership_date', 'joined_date')
    search_fields = ('name', 'email')
    list_filter = ('status',)
    readonly_fields = ('joined_date',)
