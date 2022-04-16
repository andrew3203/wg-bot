from django.contrib import admin
from api import models


@admin.register(models.BaseUser)
class BaseUserAdmin(admin.ModelAdmin):
    list_display = (
        'user_id', 'username',
        'is_active', 'is_staff',
        'created_at'
    )
    list_filter = ("is_active", "is_staff")
    search_fields = ('username', 'user_id')


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'user_id', 'username', 'balance',
        'is_active', 'created_at', 'updated_at'
    )
    list_filter = ("is_active", "is_staff")
    search_fields = ('username', 'user_id')


@admin.register(models.Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = (
        'owner', 'code',
        'created_at',
    )
    search_fields = ('owner', 'code')

    @admin.display(description='Uses amount')
    def get_uses_amount(obj):
        return f'{obj.get_uses_amount()}'


@admin.register(models.Order)
class OrderTrafficAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'tariff', 'is_paid',
        'paid_at', 'finish_at',
    )
    list_filter = ("is_paid", 'tariff')
    search_fields = ('user', 'tariff')


@admin.register(models.Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = (
        'price', 'traffic_amount',
        'connections_amount',
    )
    search_fields = ('price',)


@admin.register(models.VpnServer)
class VpnServerAdmin(admin.ModelAdmin):
    list_display = (
        'ip', 'location', 'peers_amount',
    )
    list_filter = ("location", )
    search_fields = ('ip', 'user_id')

    @admin.display(description='Available peers amount')
    def get_available_peers_amount(obj):
        return f'{obj.get_available_peers_amount()}'

    @admin.display(description='Peers amount')
    def get_peers_amount(obj):
        return f'{obj.get_peers_amount()}'

    @admin.display(description='All traffic')
    def getget_traffic_peers_amount(obj):
        return f'{obj.get_traffic()}'


@admin.register(models.Peer)
class PeerAdmin(admin.ModelAdmin):
    list_display = (
        'server', 'is_busy',
    )
    list_filter = ("is_busy",)
    search_fields = ('server',)


@admin.register(models.PeerTraffic)
class PeerTrafficAdmin(admin.ModelAdmin):
    list_display = (
        'recived_gb', 'trancmitted_gb', 'time', 'peer',
    )
    search_fields = ('peer',)


@admin.register(models.ServerTraffic)
class ServerTrafficAdmin(admin.ModelAdmin):
    list_display = (
        'recived_gb', 'trancmitted_gb', 'time', 'server',
    )
    search_fields = ('server',)
