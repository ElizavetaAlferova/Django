from django.contrib import admin

from .models import Category, Comment, Location, Post


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'description',
        'slug'
    )
    list_editable = (
        'description',
        'slug'
    )
    search_fields = ('title',)
    list_filter = ('title',)
    list_display_links = ('title',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location)
admin.site.register(Post)
admin.site.register(Comment)
