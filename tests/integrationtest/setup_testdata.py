from pretix.base.models import (
    Event, Item, Order, OrderPosition, Question, QuestionAnswer,
    Team, TeamAPIToken, Organizer, SalesChannel,
)
from django.contrib.auth import get_user_model
from django_scopes import scope
from decimal import Decimal
import datetime
import pytz

User = get_user_model()
u = User.objects.get(email='admin@example.com')


def make_event(org, slug, name):
    with scope(organizer=org):
        return Event.objects.create(
            organizer=org, slug=slug,
            name=name, plugins='',
            date_from=datetime.datetime(2025, 1, 1, tzinfo=pytz.UTC),
            currency='EUR', live=True,
        )


def make_item(event, org, name):
    with scope(organizer=org):
        return Item.objects.create(event=event, name=name, default_price=Decimal('0.00'), admission=True)


def make_question(event, org, text):
    with scope(organizer=org):
        return Question.objects.create(event=event, question=text, type='S', required=False)


_order_counter = 0


def make_order(event, org, item, question=None, answer=None):
    global _order_counter
    _order_counter += 1
    code = 'T{:04d}'.format(_order_counter)
    with scope(organizer=org):
        sc = SalesChannel.objects.get(organizer=org, identifier='web')
        order = Order.objects.create(
            event=event, code=code, email='test@example.com',
            status=Order.STATUS_PAID, locale='en',
            sales_channel=sc,
            datetime=datetime.datetime.now(pytz.UTC),
            expires=datetime.datetime(2030, 1, 1, tzinfo=pytz.UTC),
            total=Decimal('0.00'),
        )
        pos = OrderPosition.objects.create(
            order=order, item=item, price=Decimal('0.00'),
            attendee_name_cached='Test Person', attendee_email='test@example.com',
        )
        if question and answer:
            QuestionAnswer.objects.create(orderposition=pos, question=question, answer=answer)
        return order


# All test data lives under one organizer so a single TeamAPIToken covers everything
org = Organizer.objects.create(slug='dpsg-speyer', name='DPSG Speyer')

# prisma-2025 (used by test_events, test_orders, test_questions)
ev1 = make_event(org, 'prisma-2025', 'Prisma 2025')
it1 = make_item(ev1, org, 'Ticket')
q1 = make_question(ev1, org, 'City')
make_order(ev1, org, it1, q1, 'Berlin')

# source-event (used by test_forwarder as source)
ev2 = make_event(org, 'source-event', 'Source Event')
it2 = make_item(ev2, org, 'Ticket')
make_order(ev2, org, it2)

# dest-event (used by test_forwarder as destination)
ev3 = make_event(org, 'dest-event', 'Dest Event')
make_item(ev3, org, 'Ticket')

# Single team + token covering all events under dpsg-speyer
t = Team.objects.create(
    organizer=org, name='CI', all_events=True,
    all_event_permissions=True, all_organizer_permissions=True,
)
t.members.add(u)
tok = TeamAPIToken.objects.create(team=t, name='ci')
print(tok.token)
