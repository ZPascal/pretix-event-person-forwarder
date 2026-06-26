#!/usr/bin/env python3
"""Bootstrap test data in a local Pretix instance for integration tests.

Creates:
  - Organizer 'dpsg-speyer' with event 'prisma-2025' and question id=256
    (used by existing tests/integrationtest/test_events.py, test_orders.py, test_questions.py)
  - Organizer 'source-org' with event 'source-event' and a test order
  - Organizer 'dest-org' with event 'dest-event'
"""
import json
import sys

import httpx

BASE_URL = "http://localhost"
ADMIN_TOKEN = sys.argv[1] if len(sys.argv) > 1 else ""

headers = {
    "Authorization": f"Token {ADMIN_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}


def post(path, payload):
    resp = httpx.post(f"{BASE_URL}{path}", headers=headers, content=json.dumps(payload), follow_redirects=True)
    if resp.status_code not in (200, 201):
        print(f"POST {path} failed {resp.status_code}: {resp.text}", file=sys.stderr)
        sys.exit(1)
    return resp.json()


def get(path):
    resp = httpx.get(f"{BASE_URL}{path}", headers=headers, follow_redirects=True)
    if resp.status_code != 200:
        print(f"GET {path} failed {resp.status_code}: {resp.text}", file=sys.stderr)
        sys.exit(1)
    return resp.json()


def create_organizer(slug, name):
    return post("/api/v1/organizers/", {"name": name, "slug": slug})


def create_event(organizer, slug, name):
    return post(f"/api/v1/organizers/{organizer}/events/", {
        "name": {"en": name},
        "slug": slug,
        "live": True,
        "currency": "EUR",
        "date_from": "2025-01-01T00:00:00Z",
        "plugins": [],
    })


def create_question(organizer, event, question_text):
    return post(f"/api/v1/organizers/{organizer}/events/{event}/questions/", {
        "question": {"en": question_text},
        "type": "S",
        "required": False,
        "items": [],
    })


def create_item(organizer, event, name):
    return post(f"/api/v1/organizers/{organizer}/events/{event}/items/", {
        "name": {"en": name},
        "default_price": "0.00",
        "tax_rate": "0.00",
        "admission": True,
    })


def create_order(organizer, event, item_id, question_id=None):
    answers = []
    if question_id:
        answers = [{"question": question_id, "answer": "Berlin", "options": []}]
    return post(f"/api/v1/organizers/{organizer}/events/{event}/orders/", {
        "email": "test@example.com",
        "locale": "en",
        "sales_channel": "web",
        "payment_provider": "manual",
        "status": "p",
        "positions": [
            {
                "item": item_id,
                "attendee_name_parts": {"_legacy": "Test Person"},
                "attendee_email": "test@example.com",
                "answers": answers,
            }
        ],
    })


# --- dpsg-speyer / prisma-2025 (existing tests) ---
print("Creating dpsg-speyer organizer...")
create_organizer("dpsg-speyer", "DPSG Speyer")

print("Creating prisma-2025 event...")
create_event("dpsg-speyer", "prisma-2025", "Prisma 2025")

print("Creating item for prisma-2025...")
item = create_item("dpsg-speyer", "prisma-2025", "Ticket")

print("Creating question (will become id=1, tests reference 256 — adjust if needed)...")
question = create_question("dpsg-speyer", "prisma-2025", "City")
print(f"  Question ID: {question['id']} (tests/integrationtest/test_questions.py references 256)")

print("Creating test order for dpsg-speyer/prisma-2025...")
create_order("dpsg-speyer", "prisma-2025", item["id"], question["id"])

# --- source-org / source-event (forwarder tests) ---
print("Creating source-org organizer...")
create_organizer("source-org", "Source Org")

print("Creating source-event event...")
create_event("source-org", "source-event", "Source Event")

print("Creating item for source-event...")
src_item = create_item("source-org", "source-event", "Ticket")

print("Creating test order for source-org/source-event...")
create_order("source-org", "source-event", src_item["id"])

# --- dest-org / dest-event (forwarder tests) ---
print("Creating dest-org organizer...")
create_organizer("dest-org", "Dest Org")

print("Creating dest-event event...")
create_event("dest-org", "dest-event", "Dest Event")

print("Creating item for dest-event (required for order creation)...")
create_item("dest-org", "dest-event", "Ticket")

print("Bootstrap complete.")
