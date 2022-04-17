from django.contrib import admin
from api import models


@admin.register(models.Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = (
        'clientname',
        'is_active', 'is_staff',
        'created_at'
    )
    list_filter = ("is_active", "is_staff")
    search_fields = ('clientname', 'user_id')


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'tg_user_id', 'client', 'username', 'balance',
        'created_at', 'updated_at'
    )
    search_fields = ('client', 'user_id')


@admin.register(models.Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = (
        'owner', 'code',
        'created_at',
    )
    search_fields = ('owner', 'code')
    readonly_fields = ('get_uses_amount',)

    @admin.display(description='Uses amount')
    def get_uses_amount(self, obj):
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
    readonly_fields = (
        'available_peers_amount',
        'peers_amount',
        'traffic_peers_amount',
    )

    @admin.display(description='Available peers amount')
    def available_peers_amount(self, obj):
        return f'{obj.get_available_peers_amount()}'

    @admin.display(description='Peers amount')
    def peers_amount(self, obj):
        return f'{obj.get_peers_amount()}'

    @admin.display(description='All traffic (GB)')
    def traffic_peers_amount(self, obj):
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
