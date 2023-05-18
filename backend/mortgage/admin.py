from django.contrib import admin
from .models import (
    Bank,
    MortgageAdvantage,
    MortgageInstrument,
    MortgagePage,
    Offer,
    OfferFAQ,
    OfferTypeStep,
    OfferPanel,
    Program,
    MortgagePageForm,
    MortgagePageFormEmployee,
)
from .tasks import calculate_mortgage_page_fields_task


class PurchaseTypeStepInline(admin.TabularInline):
    model = OfferTypeStep
    extra = 0


class MortgageAdvantageInline(admin.TabularInline):
    model = MortgageAdvantage
    extra = 0


class MortgageInstrumentInline(admin.TabularInline):
    model = MortgageInstrument
    extra = 0


@admin.register(MortgagePageForm)
class MortgagePageFormAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name")


@admin.register(MortgagePageFormEmployee)
class MortgagePageFormEmployeeAdmin(admin.ModelAdmin):
    pass


@admin.register(MortgagePage)
class MortgagePageAdmin(admin.ModelAdmin):
    inlines = (MortgageAdvantageInline, MortgageInstrumentInline)
    actions = ("calculate_fields",)

    def calculate_fields(self, request, queryset):
        calculate_mortgage_page_fields_task()

    calculate_fields.short_description = "Просчитать поля"


@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    pass


@admin.register(OfferFAQ)
class OfferFAQAdmin(admin.ModelAdmin):
    pass


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = (
        "program",
        "deposit_display",
        "rate_display",
        "term_display",
        "amount_display",
        "get_projects",
        "is_active",
        "city",
        "is_site"
    )
    inlines = (PurchaseTypeStepInline,)
    list_filter = ("projects", "type", "program", "is_active", "city", "is_site")

    @staticmethod
    def range_display(value, unit="%"):
        if not value:
            return "не задана"
        elif value.lower == value.upper:
            return f"{value.lower} {unit}"
        elif not value.lower:
            return f"до {value.upper} {unit}"
        elif not value.upper:
            return f"от {value.lower} {unit}"
        else:
            return f"от {value.lower} {unit} до {value.upper} {unit}"

    def rate_display(self, obj):
        return self.range_display(obj.rate)

    rate_display.short_description = "Процентная ставка"
    rate_display.admin_order_field = "rate"

    def term_display(self, obj):
        return self.range_display(obj.term, unit="")

    term_display.short_description = "Срок кредита"
    term_display.admin_order_field = "term"

    def deposit_display(self, obj):
        return self.range_display(obj.deposit)

    deposit_display.short_description = "Первоначальный взнос"
    deposit_display.admin_order_field = "deposit"

    def amount_display(self, obj):
        return self.range_display(obj.amount, unit="руб.")

    amount_display.short_description = "Сумма кредита"
    amount_display.admin_order_field = "amount"

    def get_projects(self, obj):
        return ", ".join([str(project) for project in obj.projects.all()])

    get_projects.short_description = "Проекты"
    get_projects.admin_order_field = "projects"


@admin.register(OfferPanel)
class OfferPanelAdmin(admin.ModelAdmin):
    list_display = (
        "bank",
        "is_active",
        "program",
        "deposit_display",
        "rate_display",
        "term_display",
        "amount_display",
        "get_projects",
    )
    list_filter = ("projects", "bank", "type", "program", "deposit", "rate", "term", "is_active", "city")
    list_editable = ("is_active",)
    actions = ["update_task"]

    @staticmethod
    def range_display(value, unit="%"):
        if not value:
            return "не задана"
        elif value.lower == value.upper:
            return f"{value.lower} {unit}"
        elif not value.lower:
            return f"до {value.upper} {unit}"
        elif not value.upper:
            return f"от {value.lower} {unit}"
        else:
            return f"от {value.lower} {unit} до {value.upper} {unit}"

    def rate_display(self, obj):
        return self.range_display(obj.rate)

    rate_display.short_description = "Процентная ставка"
    rate_display.admin_order_field = "rate"

    def term_display(self, obj):
        return self.range_display(obj.term, unit="")

    term_display.short_description = "Срок кредита"
    term_display.admin_order_field = "term"

    def deposit_display(self, obj):
        return self.range_display(obj.deposit)

    deposit_display.short_description = "Первоначальный взнос"
    deposit_display.admin_order_field = "deposit"

    def amount_display(self, obj):
        return self.range_display(obj.amount, unit="руб.")

    amount_display.short_description = "Сумма кредита"
    amount_display.admin_order_field = "amount"

    def from_dvizh_display(self, obj):
        return bool(obj.dvizh_ids)

    from_dvizh_display.short_description = "Предложение от Движ."
    from_dvizh_display.admin_order_field = "dvizh_ids"
    from_dvizh_display.boolean = True

    def get_projects(self, obj):
        return ", ".join([str(project) for project in obj.projects.all()])

    get_projects.short_description = "Проекты"
    get_projects.admin_order_field = "projects"

    def update_task(self, request, queryset):
        from dvizh_api.tasks import update_offers_data_task

        update_offers_data_task.delay()

    update_task.short_description = "Запустить обновление"


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    pass
