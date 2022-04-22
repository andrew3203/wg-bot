from django.contrib import admin
from api import models
from .tasks import update_peers, update_traffic, check_users



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
        'tg_user_id', 'client', 'balance',
        'created_at', 'updated_at'
    )
    search_fields = ('client', 'user_id')

    actions = ['check_users_cmd', 'update_info']

    def check_users_cmd(self, request, queryset):
        user_ids = queryset.values_list('id', flat=True).distinct().iterator()
        print(list(user_ids))
        check_users.delay(user_ids=list(user_ids))
    
    def update_info(self, request, queryset):
        user_ids = queryset.values_list('id', flat=True).distinct().iterator()
        print(list(user_ids))


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
class OrderAdmin(admin.ModelAdmin):
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
    actions = ['update_peers_cmd']

    def update_peers_cmd(self, request, queryset):
        vpn_server_ids = queryset.values_list('id', flat=True).distinct().iterator()
        print(list(vpn_server_ids))
        update_peers.delay(vpn_server_ids=list(vpn_server_ids))
                      

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
        'server', 'peer_id',
        'is_booked', 'enabled', 'connected'

    )
    list_filter = ('is_booked', 'enabled', 'connected')
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
