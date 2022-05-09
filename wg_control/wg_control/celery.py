import os
from celery import Celery
from celery import shared_task
from celery.utils.log import get_task_logger


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wg_control.settings')

app = Celery('wg_control')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

logger = get_task_logger(__name__)


@shared_task
def send_notify(user_id, keyword, *args, **kwagrs):
    # send_notify.delay(user.id, 'has_no_avallible_traffic', order_id=self.id)
    # send_notify.delay(user.id, 'has_no_avallible_time', order_id=self.id)
    # send_notify.delay(user.id, 'order_auto_renewaled', order_id=self.id)
    # send_notify.delay(user.id, 'has_no_balance_to_auto_renewale', order_id=self.id)
    # send_notify.delay(user.id, 'order_closed', order_id=self.id)


    # send_notify.delay(referral.owner.id, 'user_get_from_referral', user=user.id)

    # send_notify.delay(self.user.id, 'time_is_running_out', order_id=self.id, delta_time=delta_time)
    # send_notify.delay(self.user.id, 'traffic_is_running_out', order_id=self.id, delta_traffic=delta_traffic)



    logger.info(
        f' - - - User: {user_id} notified! {keyword}, {args}, {kwagrs} - - -')
    return True
