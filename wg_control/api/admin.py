from django.contrib import admin
from api import models
from .tasks import check_users, get_updates, send_order_mails



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

    actions = ['check_users_cmd']

    def check_users_cmd(self, request, queryset):
        user_ids = queryset.values_list('id', flat=True).distinct().iterator()
        user_ids = list(user_ids)
        check_users.delay(user_ids=user_ids)


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
    actions = ['send_mails']

    def send_mails(self, request, queryset):
        orders_ids = queryset.values_list('id', flat=True).distinct().iterator()
        orders_ids = list(orders_ids)
        send_order_mails.delay(orders_ids, request.build_absolute_uri())

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
        'all_traffic',
    )
    actions = ['get_updates_cmd']

    def get_updates_cmd(self, request, queryset):
        vpn_server_ids = queryset.values_list('id', flat=True).distinct().iterator()
        vpn_server_ids = list(vpn_server_ids)
        get_updates.delay(vpn_server_ids=vpn_server_ids)
                      

    @admin.display(description='Available peers amount')
    def available_peers_amount(self, obj):
        return f'{obj.get_available_peers_amount()}'

    @admin.display(description='Peers amount')
    def peers_amount(self, obj):
        return f'{obj.get_peers_amount()}'

    @admin.display(description='All traffic')
    def all_traffic(self, obj):
        return f'{obj.get_traffic_label()}'


@admin.register(models.Peer)
class PeerAdmin(admin.ModelAdmin):
    list_display = (
        'server', 'public_key',
        'is_booked', 'connected'

    )
    list_filter = ('is_booked', 'connected')
    search_fields = ('server', 'public_key')

    readonly_fields = (
        'all_traffic',
        'recived_bytes',
        'trancmitted_bytes',
        'data_time_update'
    )

    @admin.display(description='Traffic')
    def all_traffic(self, obj):
        return f'{obj.get_traffic_label()}'


@admin.register(models.ServerTraffic)
class ServerTrafficAdmin(admin.ModelAdmin):
    list_display = (
        'recived_bytes', 'trancmitted_bytes', 'time', 'server',
    )
    search_fields = ('server',)
