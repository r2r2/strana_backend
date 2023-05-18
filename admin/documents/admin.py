from django.contrib import admin
from . models import Document, Escrow


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    pass

@admin.register(Escrow)
class EscrowAdmin(admin.ModelAdmin):
    list_display = ("slug", "file")
