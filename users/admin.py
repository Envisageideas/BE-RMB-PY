from django.contrib import admin
from .models import UserProfile, EditablePage

from .models import Event
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "first_name", "last_name", "email", "mobile", "blood_group", "birthdate", "educational_qualification")
    search_fields = ("first_name", "last_name", "email", "mobile")
    list_filter = ("blood_group", "user_type", "is_rmb_member")


@admin.register(EditablePage)
class EditablePageAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "updated_at", "updated_by")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "created_at")
    search_fields = ("title",)
    ordering = ("-date",)


from .models import KnowledgeItem

@admin.register(KnowledgeItem)
class KnowledgeItemAdmin(admin.ModelAdmin):
    list_display = ("name", "item_type", "parent", "created_by", "created_at")
    search_fields = ("name",)
    list_filter = ("item_type",)



from django.contrib import admin
from .models import D2DConnect, BusinessGiven, BusinessReceived, ReferralGiven

admin.site.register(D2DConnect)
admin.site.register(BusinessGiven)
admin.site.register(BusinessReceived)
admin.site.register(ReferralGiven)
