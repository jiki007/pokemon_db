from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Avg
from .models import *

admin.site.site_header  = "⚡ PokémonDB Admin"
admin.site.site_title   = "PokémonDB"
admin.site.index_title  = "Database Management"

#Inlines
class AttackInline(admin.TabularInline):
    model = Attack
    extra = 0
    fields = ['name', 'damage', 'converted_cost', 'description']
    readonly_fields = ('converted_cost')

class WeaknessInline(admin.TabularInline):
    model = Weakness
    extra = 0
    fields = ('type', 'value')

class ResistanceInline(admin.TabularInline):
    model = Resistance
    extra = 0
    fields = ('type', 'value')

class PriceLine(admin.TabularInline):
    model = Price
    extra = 0
    fields = ('tcg_low', 'tcg_mid', 'tcg_high', 'tcg_market')

# Register your models here.

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('card_image', 'name', 'card_id', 'supertype', 'rarity', 'hp', 'card_set', 'market_price_display', 'created_at')
    list_filter = ('supertype', 'rarity', 'types', 'card_set__series')
    search_fields = ('name', 'card_id', 'artist')
    readonly_fields = ('card_id', 'created_at', 'updated_at', 'card_image_large')
    list_per_page = 25
    ordering = ('name',)
    inlines = [PriceLine, AttackInline, WeaknessInline, ResistanceInline]

    fieldsets = (
        ('Identity', {
            'fields': ('card_image_large', 'card_id', 'name', 'supertype', 'subtypes', 'rarity', 'card_number')
        }),
        ('Stats', {
            'fields': ('hp', 'evolves_from', 'retreat_cost')
        }),
        ('Media', {
            'fields': ('image_small', 'image_large', 'artist', 'flavor_text')
        }),
        ('Relations', {
            'fields': ('card_set', 'types')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def card_image(self, obj):
        if obj.image_small:
            return format_html('<img src="{}" style="height:48px;border-radius:4px;">', obj.image_small)
        return '🃏'
    card_image.short_description = ''

    def card_image_large(self, obj):
        if obj.image_large:
            return format_html('<img src="{}" style="height:200px;border-radius:8px;">', obj.image_large)
        return '—'
    card_image_large.short_description = 'Preview'

    def market_price_display(self, obj):
        try:
            p = obj.price.tcg_market
            if p:
                return format_html('<span style="color:#22c55e;font-weight:600;">${}</span>', p)
        except Exception:
            pass
        return format_html('<span style="color:#9ca3af;">—</span>')
    market_price_display.short_description = 'Market Price'


@admin.register(Cardset)
class CardsetAdmin(admin.ModelAdmin):
    list_display  = ('set_logo', 'name', 'series', 'release_date', 'card_count_display', 'printed_total')
    list_filter   = ('series',)
    search_fields = ('name', 'series', 'set_id')
    readonly_fields = ('set_id', 'set_logo_large')
    list_per_page = 30
    ordering      = ('-release_date',)

    fieldsets = (
        ('Identity', {
            'fields': ('set_logo_large', 'set_id', 'name', 'series')
        }),
        ('Card Counts', {
            'fields': ('printed_total', 'total')
        }),
        ('Media', {
            'fields': ('logo_url', 'symbol_url')
        }),
        ('Release', {
            'fields': ('release_date',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(card_count=Count('cards'))

    def set_logo(self, obj):
        if obj.logo_url:
            return format_html('<img src="{}" style="height:32px;object-fit:contain;">', obj.logo_url)
        return '🃏'
    set_logo.short_description = ''

    def set_logo_large(self, obj):
        if obj.logo_url:
            return format_html('<img src="{}" style="height:60px;object-fit:contain;">', obj.logo_url)
        return '—'
    set_logo_large.short_description = 'Logo'

    def card_count_display(self, obj):
        return obj.card_count
    card_count_display.short_description = 'Cards in DB'
    card_count_display.admin_order_field = 'card_count'

#Type
@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):
    list_display  = ('type_badge', 'name', 'card_count_display')
    search_fields = ('name',)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(card_count=Count('cards'))

    def type_badge(self, obj):
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;border-radius:12px;font-size:12px;font-weight:600;">{} {}</span>',
            obj.color, obj.icon, obj.name
        )
    type_badge.short_description = 'Type'

    def card_count_display(self, obj):
        return obj.card_count
    card_count_display.short_description = 'Cards'
    card_count_display.admin_order_field = 'card_count'

#Price
@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display  = ('card', 'tcg_market', 'tcg_low', 'tcg_high', 'update_at')
    search_fields = ('card__name',)
    list_filter   = ('update_at',)
    readonly_fields = ('update_at',)
    ordering      = ('-tcg_market',)
    list_per_page = 30

#Attack
@admin.register(Attack)
class AttackAdmin(admin.ModelAdmin):
    list_display  = ('name', 'card', 'damage', 'converted_cost')
    search_fields = ('name', 'card__name')
    list_filter   = ('converted_cost',)
    ordering      = ('-converted_cost',)
    list_per_page = 30

#Favorite