from django.contrib import admin
from .models import UserProfile
from .models import Election, Candidate

class CandidateInline(admin.TabularInline):
    model = Candidate
    extra = 1

class ElectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_time', 'end_time', 'status']
    inlines = [CandidateInline]

admin.site.register(Election, ElectionAdmin)
admin.site.register(Candidate)
admin.site.register(UserProfile)
