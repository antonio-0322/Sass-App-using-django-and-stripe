import datetime

from apps.payment.models import Plan, Subscription
from apps.setup.enums import FieldSlugs
from apps.user.models import User

def user_subscribes_to_plan(user: User, plan: Plan) -> None:
    """
      Subscribe a user to a specified plan.
      This function creates a new subscription for the user with the specified plan.
      It deactivates any existing subscriptions for the user and sets the end date
      of the new subscription to today's date plus 30 days.
      Parameters:
      - user: The user object to subscribe.
      - plan: The plan object to subscribe the user to.
      Returns:
      - None
      Raises:
      - N/A
      """
    deactivate_user_subscriptions(user)
    end_date = datetime.date.today() + datetime.timedelta(days=2) if not plan.is_chargeable else None
    Subscription.objects.create(
        user=user,
        plan=plan,
        end_date=end_date
    )


def deactivate_user_subscriptions(user: User) -> None:
    Subscription.objects.filter(user=user).update(active=False)


def user_subscribes_to_free_plan(user: User):
    plan = Plan.objects.get(amount=0)
    user_subscribes_to_plan(user=user, plan=plan)


def set_subscription_expired(subscription: Subscription):
    subscription.active = False
    subscription.save()


def sync_user_data_with_plan_limits(user: User):
    """
        After changing subscription, we need sync user data
        which is connected to subscription plan options
        ex. Job_search_filters->job_titles
    """
    # delete additional job titles if user has

    job_titles = user.job_search_filters.filter(job_search_filter__slug=FieldSlugs.JOB_TITLE).first()
    if not job_titles:
        return

    plan_limit = user.active_subscription.total_job_titles
    job_titles.values = job_titles.values[:plan_limit] if job_titles.values else []
    job_titles.save()


def create_pending_subscription(user: User, plan: Plan) -> Subscription:
    """
    @param user: User
    @param plan: Plan
    @return: Subscription
    """
    subscription = Subscription.objects.create(
        user=user,
        plan=plan,
        end_date=None,
        active=False
    )

    subscription.save()

    return subscription


def activate_user_subscription(subscription: Subscription, stripe_webhook_id: str, created_at: datetime):
    """
    @param subscription: Subscription
    @param stripe_webhook_id: str
    @param created_at: datetime
    """
    subscription.active = True
    subscription.stripe_webhook_id = stripe_webhook_id
    subscription.stripe_webhook_created_at = created_at
    subscription.save()
