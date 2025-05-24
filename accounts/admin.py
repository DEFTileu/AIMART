from django.contrib import admin

from accounts.models import CustomUser, Card

admin.site.register(CustomUser)


@admin.register(Card)
class PaymentCardAdmin(admin.ModelAdmin):
    list_display = ('user', 'card_number', 'get_expiry_date', 'created_at')
    search_fields = ('user__email', 'card_number')
    readonly_fields = ('created_at',)

    def get_card_number(self, obj):
        return f"**** **** **** {obj.card_number[-4:]}"

    def get_expiry_date(self, obj):
        return f"{obj.expiry_month:02d}/{obj.expiry_year}"

    get_expiry_date.short_description = 'Expiry Date'

    get_card_number.short_description = 'Card Number'