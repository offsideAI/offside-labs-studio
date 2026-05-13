"""Seed the Agents Marketplace with 4 demo-ready agents (M9.S4 / FR-26).

Run from the backend container:

    docker compose -f backend/docker-compose.yml exec web \
        python -m tools.seeds.marketplace

Idempotent: re-running upserts by `slug` so the catalog stays clean.
Only uses currently-shipped trigger types (manual, record) and action
types (noop, log, crm.*) so every agent runs out-of-the-box after
install.
"""

from __future__ import annotations

import os
import sys
from typing import Any

# Make `apps.*` importable when this script is invoked directly via
# `python -m tools.seeds.marketplace` from the repo root.
_BACKEND = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "backend")
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)

import django  # noqa: E402

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "offside_crm.settings.dev")
django.setup()

from apps.marketplace.models import MarketplaceAgent, MarketplaceAgentCategory  # noqa: E402


SEED_AGENTS: list[dict[str, Any]] = [
    # 0. ★★★ HERO AGENT — Ecommerce Conversion Funnel Optimizer.
    #
    # The demo opener. A single agent that *choreographs* the entire
    # AEO → ads → landing → email → cart-recovery → payments funnel.
    # 9 nodes; every node is inspectable + costed; every CRM record
    # the agent creates is visible to the audience by switching to
    # /companies and /tasks during the demo.
    #
    # Trigger is manual so the presenter can fire it live with one
    # click of the Run button. trigger_payload is empty — the agent
    # doesn't depend on any external data; the value is the
    # choreography itself.
    {
        "slug": "ecommerce-conversion-funnel-optimizer",
        "name": "Ecommerce Conversion Funnel Optimizer",
        "icon_emoji": "🚀",
        "category": MarketplaceAgentCategory.LEAD_MANAGEMENT,
        "description": (
            "One agent. Whole funnel. Marketing campaign launch → AEO content "
            "seed → ad-platform sync → landing-page generation → email "
            "welcome → cart recovery → payments confirmation. Every lead "
            "pulled in becomes a converted paying customer."
        ),
        "long_description": (
            "Install + run this agent to deploy a full ecommerce conversion "
            "funnel in one go. The 10-node graph orchestrates: (1) marketing "
            "campaign launch across email + social + search + display, (2) "
            "AEO content seed via your answer-engine partner, (3) ad-platform "
            "campaign sync, (4) landing-page generation, (5) a placeholder "
            "Demo Funnel company record, (6) email welcome series task, "
            "(7) abandoned-cart recovery task, (8) post-purchase confirm "
            "task, (9) deployment-summary note. Each node's output feeds "
            "the next via {{ n<N>.<field> }} templating, so the audience "
            "can watch one click create the scaffolding of an entire "
            "funnel. After install, the same 10-node graph is editable in "
            "the Agent Design Studio — swap any node for a real integration "
            "(your real campaign orchestrator, your real AEO endpoint, your "
            "real ad platform, your real ESP)."
        ),
        "trigger": {"type": "manual"},
        "graph": {
            "start_node_id": "n1",
            "nodes": {
                "n1": {
                    "type": "action",
                    "label": "Initialize funnel",
                    "config": {
                        "action": "log",
                        "input": {
                            "message": "🚀 ecommerce funnel optimization starting",
                            "phase": "init",
                        },
                    },
                    "next": "n2",
                    "position": {"x": 40, "y": 80},
                },
                "n2": {
                    "type": "action",
                    "label": "Launch marketing campaign",
                    "config": {
                        "action": "crm.http.request",
                        "input": {
                            "url": "https://httpbin.org/post",
                            "method": "POST",
                            "body": {
                                "kind": "marketing_campaign_launch",
                                "campaign_name": "Acme Q3 conversion funnel",
                                "channels": ["email", "social", "search", "display"],
                                "budget_cents": 1_000_000,
                                "target_audience": "ecommerce_shoppers_us_dach",
                                "launch_window_days": 90,
                            },
                        },
                    },
                    "next": "n3",
                    "position": {"x": 320, "y": 80},
                },
                "n3": {
                    "type": "action",
                    "label": "Seed AEO answer content",
                    "config": {
                        "action": "crm.http.request",
                        "input": {
                            "url": "https://httpbin.org/post",
                            "method": "POST",
                            "body": {
                                "kind": "aeo_content_seed",
                                "linked_to_campaign_status": "{{ n2.status_code }}",
                                "topics": [
                                    "best ecommerce platform",
                                    "fastest checkout flow",
                                    "abandoned-cart recovery best practices",
                                ],
                                "target_engines": ["chatgpt", "perplexity", "claude"],
                            },
                        },
                    },
                    "next": "n4",
                    "position": {"x": 600, "y": 80},
                },
                "n4": {
                    "type": "action",
                    "label": "Sync ad campaigns",
                    "config": {
                        "action": "crm.http.request",
                        "input": {
                            "url": "https://httpbin.org/post",
                            "method": "POST",
                            "body": {
                                "kind": "ad_campaign_sync",
                                "platforms": ["google_ads", "meta_ads", "tiktok_ads"],
                                "linked_to_aeo_status": "{{ n3.status_code }}",
                            },
                        },
                    },
                    "next": "n5",
                    "position": {"x": 880, "y": 80},
                },
                "n5": {
                    "type": "action",
                    "label": "Generate landing pages",
                    "config": {
                        "action": "crm.http.request",
                        "input": {
                            "url": "https://httpbin.org/post",
                            "method": "POST",
                            "body": {
                                "kind": "landing_page_generation",
                                "variants": 3,
                                "split_test_traffic": [40, 40, 20],
                            },
                        },
                    },
                    "next": "n6",
                    "position": {"x": 880, "y": 280},
                },
                "n6": {
                    "type": "action",
                    "label": "Create funnel company record",
                    "config": {
                        "action": "crm.create_company",
                        "input": {
                            "name": "Acme Demo Funnel · {{ n2.status_code }}",
                            "domain": "demo-funnel.example",
                            "industry": "Ecommerce",
                            "size_band": "11-50",
                            "created_by_id": "__INSTALLER__",
                        },
                    },
                    "next": "n7",
                    "position": {"x": 600, "y": 280},
                },
                "n7": {
                    "type": "action",
                    "label": "Queue email welcome series",
                    "config": {
                        "action": "crm.create_task",
                        "input": {
                            "title": "📧 Send welcome email (Day 0)",
                            "description": "Auto-deployed by Funnel Optimizer. Personalize subject line per AEO topic.",
                            "related_type": "company",
                            "related_id": "{{ n6.company_id }}",
                            "priority": "high",
                            "created_by_id": "__INSTALLER__",
                        },
                    },
                    "next": "n8",
                    "position": {"x": 320, "y": 280},
                },
                "n8": {
                    "type": "action",
                    "label": "Queue cart-recovery sequence",
                    "config": {
                        "action": "crm.create_task",
                        "input": {
                            "title": "🛒 Configure abandoned-cart recovery",
                            "description": "Auto-deployed by Funnel Optimizer. Trigger at 30 min + 2 hr + 24 hr cart-idle.",
                            "related_type": "company",
                            "related_id": "{{ n6.company_id }}",
                            "priority": "high",
                            "created_by_id": "__INSTALLER__",
                        },
                    },
                    "next": "n9",
                    "position": {"x": 40, "y": 280},
                },
                "n9": {
                    "type": "action",
                    "label": "Queue payment confirmation",
                    "config": {
                        "action": "crm.create_task",
                        "input": {
                            "title": "💳 Wire payment-success confirmations",
                            "description": "Auto-deployed by Funnel Optimizer. Point Stripe webhook at the Payment success agent's URL.",
                            "related_type": "company",
                            "related_id": "{{ n6.company_id }}",
                            "priority": "medium",
                            "created_by_id": "__INSTALLER__",
                        },
                    },
                    "next": "n10",
                    "position": {"x": 40, "y": 480},
                },
                "n10": {
                    "type": "action",
                    "label": "Log deployment summary",
                    "config": {
                        "action": "crm.create_note",
                        "input": {
                            "body_md": (
                                "## 🚀 Funnel deployed\n\n"
                                "**Auto-orchestrated by the Ecommerce Conversion Funnel Optimizer agent.**\n\n"
                                "Deployed in this run:\n"
                                "- ✅ Marketing campaign launched → email · social · search · display\n"
                                "- ✅ AEO content seed → ChatGPT / Perplexity / Claude\n"
                                "- ✅ Ad campaign sync → Google / Meta / TikTok\n"
                                "- ✅ Landing pages → 3-variant split test\n"
                                "- ✅ Email welcome series queued\n"
                                "- ✅ Cart-recovery sequence queued\n"
                                "- ✅ Payment confirmations queued\n\n"
                                "Every lead pulled into this funnel becomes a tracked conversion."
                            ),
                            "related_type": "company",
                            "related_id": "{{ n6.company_id }}",
                            "author_id": "__INSTALLER__",
                        },
                    },
                    "next": "end",
                    "position": {"x": 320, "y": 480},
                },
                "end": {"type": "end", "position": {"x": 600, "y": 480}},
            },
        },
    },

    # 1. Lead qualification — fires on new contact, branches on lifecycle
    # stage, creates a high-priority task.
    {
        "slug": "lead-qualification",
        "name": "Lead qualification",
        "icon_emoji": "🎯",
        "category": MarketplaceAgentCategory.LEAD_MANAGEMENT,
        "description": "Auto-creates a follow-up task whenever a new contact lands in lead stage.",
        "long_description": (
            "Triggered when a contact is created. If the contact's lifecycle "
            "stage is 'lead', creates a high-priority follow-up task for the "
            "contact's owner. Edit the task title + priority to match your "
            "team's playbook."
        ),
        "trigger": {"type": "record", "entity_type": "contact", "event": "created"},
        "graph": {
            "start_node_id": "n1",
            "nodes": {
                "n1": {
                    "type": "action",
                    "label": "Log new contact",
                    "config": {"action": "log", "input": {"message": "new contact arrived"}},
                    "next": "n2",
                    "position": {"x": 80, "y": 80},
                },
                "n2": {
                    "type": "branch",
                    "label": "Is a lead?",
                    "config": {"field": "trigger.event", "op": "eq", "value": "created"},
                    "true_next": "n3",
                    "false_next": "end",
                    "position": {"x": 320, "y": 80},
                },
                "n3": {
                    "type": "action",
                    "label": "Create qualify-this-lead task",
                    "config": {
                        "action": "crm.create_task",
                        "input": {
                            "title": "Qualify this lead",
                            "related_type": "contact",
                            "related_id": "{{ trigger.record_id }}",
                            "priority": "high",
                            "created_by_id": "__INSTALLER__",
                        },
                    },
                    "next": "end",
                    "position": {"x": 600, "y": 30},
                },
                "end": {"type": "end", "position": {"x": 900, "y": 80}},
            },
        },
    },
    # 2. Welcome new contact — fires on new contact, drops a welcome note.
    {
        "slug": "welcome-new-contact",
        "name": "Welcome new contact",
        "icon_emoji": "👋",
        "category": MarketplaceAgentCategory.COMMS,
        "description": "Adds a welcome note to every new contact so the next rep has context.",
        "long_description": (
            "Triggered when a contact is created. Attaches a markdown welcome "
            "note to the contact record. Customize the note body to match your "
            "brand voice."
        ),
        "trigger": {"type": "record", "entity_type": "contact", "event": "created"},
        "graph": {
            "start_node_id": "n1",
            "nodes": {
                "n1": {
                    "type": "action",
                    "label": "Drop welcome note",
                    "config": {
                        "action": "crm.create_note",
                        "input": {
                            "body_md": (
                                "## Welcome\n\n"
                                "_Auto-generated by Welcome agent._\n\n"
                                "- Source: {{ trigger.entity_type }}\n"
                                "- Record id: {{ trigger.record_id }}\n"
                            ),
                            "related_type": "contact",
                            "related_id": "{{ trigger.record_id }}",
                            "author_id": "__INSTALLER__",
                        },
                    },
                    "next": "end",
                    "position": {"x": 120, "y": 80},
                },
                "end": {"type": "end", "position": {"x": 480, "y": 80}},
            },
        },
    },
    # 3. Deal stage tracker — record(deal.stage_changed) → log step. The
    # interesting bit is the run history, not the side effect.
    {
        "slug": "deal-pulse",
        "name": "Deal pulse",
        "icon_emoji": "🔔",
        "category": MarketplaceAgentCategory.DEAL_HYGIENE,
        "description": "Logs every deal stage change so you can see who moved what when.",
        "long_description": (
            "Triggered on any deal stage change. Currently writes a "
            "structured log entry; extend with crm.http.request to forward "
            "to Slack/Looker or with crm.create_task for stage-specific "
            "follow-ups."
        ),
        "trigger": {"type": "record", "entity_type": "deal", "event": "stage_changed"},
        "graph": {
            "start_node_id": "n1",
            "nodes": {
                "n1": {
                    "type": "action",
                    "label": "Log stage change",
                    "config": {
                        "action": "log",
                        "input": {
                            "message": "deal stage changed",
                            "deal_id": "{{ trigger.record_id }}",
                            "stage_id": "{{ trigger.stage_id }}",
                        },
                    },
                    "next": "end",
                    "position": {"x": 120, "y": 80},
                },
                "end": {"type": "end", "position": {"x": 480, "y": 80}},
            },
        },
    },
    # 4. Outbound HTTP ping — manual trigger; great way to demo
    # crm.http.request without setting up a webhook URL ahead of time.
    {
        "slug": "outbound-http-ping",
        "name": "Outbound HTTP ping",
        "icon_emoji": "🔌",
        "category": MarketplaceAgentCategory.INTEGRATIONS,
        "description": "Manual workflow that pings a placeholder HTTP endpoint with a deal payload.",
        "long_description": (
            "Manual trigger. Sends a POST to https://httpbin.org/post with a "
            "small JSON body. Demonstrates the crm.http.request action's auth "
            "presets — swap the URL for your own Slack / Looker / Zapier hook."
        ),
        "trigger": {"type": "manual"},
        "graph": {
            "start_node_id": "n1",
            "nodes": {
                "n1": {
                    "type": "action",
                    "label": "POST to httpbin",
                    "config": {
                        "action": "crm.http.request",
                        "input": {
                            "url": "https://httpbin.org/post",
                            "method": "POST",
                            "body": {
                                "source": "offside-marketplace",
                                "agent": "outbound-http-ping",
                            },
                        },
                    },
                    "next": "n2",
                    "position": {"x": 100, "y": 80},
                },
                "n2": {
                    "type": "action",
                    "label": "Log response",
                    "config": {
                        "action": "log",
                        "input": {"status": "{{ n1.status_code }}"},
                    },
                    "next": "end",
                    "position": {"x": 420, "y": 80},
                },
                "end": {"type": "end", "position": {"x": 720, "y": 80}},
            },
        },
    },

    # =============================================================
    # E-commerce lifecycle agents (added 2026-05).
    # Stages covered: lead capture → follow-up → conversion →
    # fulfillment → payments → customer service.
    # =============================================================

    # 5. Lead from form — captures a contact from a public form-trigger
    # endpoint (web signup, lead magnet, demo request). Pairs with the
    # M9.S1 FormEndpoint surface; install + then create a FormEndpoint
    # in admin pointing at the installed automation.
    {
        "slug": "lead-from-form",
        "name": "Lead from form",
        "icon_emoji": "📋",
        "category": MarketplaceAgentCategory.LEAD_MANAGEMENT,
        "description": "Turns a public form submission into a contact + welcome note + qualify-lead task.",
        "long_description": (
            "Form trigger. The submitted form payload is expected to carry "
            "first_name / last_name / primary_email / company keys. Creates "
            "the contact, drops a welcome note, and queues a qualify-this-lead "
            "task. Wire the trigger by creating a FormEndpoint in Django admin "
            "pointing at the installed automation."
        ),
        "trigger": {"type": "form"},
        "graph": {
            "start_node_id": "n1",
            "nodes": {
                "n1": {
                    "type": "action",
                    "label": "Create contact from form",
                    "config": {
                        "action": "crm.create_contact",
                        "input": {
                            "first_name": "{{ trigger.first_name }}",
                            "last_name": "{{ trigger.last_name }}",
                            "primary_email": "{{ trigger.primary_email }}",
                            "lifecycle_stage": "lead",
                            "source": "form",
                            "created_by_id": "__INSTALLER__",
                        },
                    },
                    "next": "n2",
                    "position": {"x": 80, "y": 80},
                },
                "n2": {
                    "type": "action",
                    "label": "Drop welcome note",
                    "config": {
                        "action": "crm.create_note",
                        "input": {
                            "body_md": "## Welcome from form\n\nAuto-captured via the public form endpoint.",
                            "related_type": "contact",
                            "related_id": "{{ n1.contact_id }}",
                            "author_id": "__INSTALLER__",
                        },
                    },
                    "next": "n3",
                    "position": {"x": 360, "y": 80},
                },
                "n3": {
                    "type": "action",
                    "label": "Queue qualify task",
                    "config": {
                        "action": "crm.create_task",
                        "input": {
                            "title": "Qualify this form lead",
                            "related_type": "contact",
                            "related_id": "{{ n1.contact_id }}",
                            "priority": "high",
                            "created_by_id": "__INSTALLER__",
                        },
                    },
                    "next": "end",
                    "position": {"x": 660, "y": 80},
                },
                "end": {"type": "end", "position": {"x": 960, "y": 80}},
            },
        },
    },

    # 6. Welcome series — day 0 — new-contact onboarding. Drops a
    # welcome note + queues a follow-up task. For multi-day series, the
    # next-day task ships in the M11 sub-graph + delay-node combo.
    {
        "slug": "welcome-series-day-0",
        "name": "Welcome series — day 0",
        "icon_emoji": "📧",
        "category": MarketplaceAgentCategory.COMMS,
        "description": "On contact create, drop a welcome note + queue a 3-day follow-up task.",
        "long_description": (
            "Triggered when a contact lands. Adds a markdown welcome note and "
            "queues a task to follow up in ~3 days. Customize the note body to "
            "match your brand voice; swap the follow-up cadence by editing the "
            "task title + priority."
        ),
        "trigger": {"type": "record", "entity_type": "contact", "event": "created"},
        "graph": {
            "start_node_id": "n1",
            "nodes": {
                "n1": {
                    "type": "action",
                    "label": "Drop welcome note",
                    "config": {
                        "action": "crm.create_note",
                        "input": {
                            "body_md": "## Welcome 🌱\n\nThanks for joining. We'll be in touch within 3 days with next steps.",
                            "related_type": "contact",
                            "related_id": "{{ trigger.record_id }}",
                            "author_id": "__INSTALLER__",
                        },
                    },
                    "next": "n2",
                    "position": {"x": 80, "y": 80},
                },
                "n2": {
                    "type": "action",
                    "label": "Queue day-3 follow-up",
                    "config": {
                        "action": "crm.create_task",
                        "input": {
                            "title": "Day-3 welcome follow-up",
                            "related_type": "contact",
                            "related_id": "{{ trigger.record_id }}",
                            "priority": "medium",
                            "created_by_id": "__INSTALLER__",
                        },
                    },
                    "next": "end",
                    "position": {"x": 420, "y": 80},
                },
                "end": {"type": "end", "position": {"x": 760, "y": 80}},
            },
        },
    },

    # 7. Abandoned cart recovery — fires when a webhook from your
    # storefront announces an abandoned cart. Creates contact + queues
    # urgent recover-this-cart task + drops cart-detail note.
    {
        "slug": "abandoned-cart-recovery",
        "name": "Abandoned cart recovery",
        "icon_emoji": "🛒",
        "category": MarketplaceAgentCategory.CART_RECOVERY,
        "description": "Webhook from your storefront → contact + high-priority recover-cart task.",
        "long_description": (
            "Webhook trigger. The payload should carry first_name / primary_email / "
            "cart_total / cart_url. The agent upserts the contact, drops a note with "
            "the cart total, and queues an urgent recover-this-cart task. Wire your "
            "Shopify / WooCommerce / Bigcommerce 'cart abandoned' webhook at the "
            "WebhookEndpoint URL you create after install."
        ),
        "trigger": {"type": "webhook"},
        "graph": {
            "start_node_id": "n1",
            "nodes": {
                "n1": {
                    "type": "action",
                    "label": "Upsert abandoned-cart contact",
                    "config": {
                        "action": "crm.create_contact",
                        "input": {
                            "first_name": "{{ trigger.first_name }}",
                            "last_name": "{{ trigger.last_name }}",
                            "primary_email": "{{ trigger.primary_email }}",
                            "lifecycle_stage": "lead",
                            "source": "abandoned_cart",
                            "created_by_id": "__INSTALLER__",
                        },
                    },
                    "next": "n2",
                    "position": {"x": 80, "y": 80},
                },
                "n2": {
                    "type": "action",
                    "label": "Note cart details",
                    "config": {
                        "action": "crm.create_note",
                        "input": {
                            "body_md": "## 🛒 Abandoned cart\n\n- Cart total: {{ trigger.cart_total }}\n- Cart URL: {{ trigger.cart_url }}\n\n_Auto-logged by Abandoned cart recovery agent._",
                            "related_type": "contact",
                            "related_id": "{{ n1.contact_id }}",
                            "author_id": "__INSTALLER__",
                        },
                    },
                    "next": "n3",
                    "position": {"x": 380, "y": 80},
                },
                "n3": {
                    "type": "action",
                    "label": "Queue recover-cart task",
                    "config": {
                        "action": "crm.create_task",
                        "input": {
                            "title": "Recover abandoned cart — {{ trigger.cart_total }}",
                            "description": "Reach out within 24h with a recovery offer.",
                            "related_type": "contact",
                            "related_id": "{{ n1.contact_id }}",
                            "priority": "high",
                            "created_by_id": "__INSTALLER__",
                        },
                    },
                    "next": "end",
                    "position": {"x": 700, "y": 80},
                },
                "end": {"type": "end", "position": {"x": 1020, "y": 80}},
            },
        },
    },

    # 8. Order received — webhook from Shopify-style storefront. Adds
    # an order-received note to the contact + queues a fulfillment task.
    {
        "slug": "order-received",
        "name": "Order received",
        "icon_emoji": "📦",
        "category": MarketplaceAgentCategory.FULFILLMENT,
        "description": "Storefront webhook → order note + fulfillment task on the buyer's contact record.",
        "long_description": (
            "Webhook trigger. The payload should carry contact_id / order_id / "
            "order_total / line_items. Drops a structured order note on the "
            "contact and queues a fulfillment task. Combine with the Shipping "
            "dispatched agent to close the fulfillment loop."
        ),
        "trigger": {"type": "webhook"},
        "graph": {
            "start_node_id": "n1",
            "nodes": {
                "n1": {
                    "type": "action",
                    "label": "Log order receipt",
                    "config": {
                        "action": "crm.create_note",
                        "input": {
                            "body_md": "## 📦 Order received\n\n- Order #{{ trigger.order_id }}\n- Total: {{ trigger.order_total }}\n\nFulfillment task queued.",
                            "related_type": "contact",
                            "related_id": "{{ trigger.contact_id }}",
                            "author_id": "__INSTALLER__",
                        },
                    },
                    "next": "n2",
                    "position": {"x": 80, "y": 80},
                },
                "n2": {
                    "type": "action",
                    "label": "Queue fulfillment",
                    "config": {
                        "action": "crm.create_task",
                        "input": {
                            "title": "Fulfill order #{{ trigger.order_id }}",
                            "description": "Pick, pack, and dispatch.",
                            "related_type": "contact",
                            "related_id": "{{ trigger.contact_id }}",
                            "priority": "high",
                            "created_by_id": "__INSTALLER__",
                        },
                    },
                    "next": "end",
                    "position": {"x": 420, "y": 80},
                },
                "end": {"type": "end", "position": {"x": 760, "y": 80}},
            },
        },
    },

    # 9. Shipping dispatched — webhook from carrier. Logs the tracking
    # event + creates a delivery-confirmation task + optionally hits a
    # customer-notification endpoint.
    {
        "slug": "shipping-dispatched",
        "name": "Shipping dispatched",
        "icon_emoji": "🚚",
        "category": MarketplaceAgentCategory.FULFILLMENT,
        "description": "Carrier webhook → shipping note on contact + delivery-confirm task + customer ping.",
        "long_description": (
            "Webhook trigger. The payload should carry contact_id / order_id / "
            "tracking_number / carrier. Drops a shipping note, queues a "
            "confirm-delivery task, and (optionally) hits a placeholder "
            "customer-notification endpoint via crm.http.request. Replace the "
            "endpoint with your transactional-email provider's API."
        ),
        "trigger": {"type": "webhook"},
        "graph": {
            "start_node_id": "n1",
            "nodes": {
                "n1": {
                    "type": "action",
                    "label": "Log shipping",
                    "config": {
                        "action": "crm.create_note",
                        "input": {
                            "body_md": "## 🚚 Shipped\n\n- Carrier: {{ trigger.carrier }}\n- Tracking #: {{ trigger.tracking_number }}\n- Order #: {{ trigger.order_id }}",
                            "related_type": "contact",
                            "related_id": "{{ trigger.contact_id }}",
                            "author_id": "__INSTALLER__",
                        },
                    },
                    "next": "n2",
                    "position": {"x": 80, "y": 80},
                },
                "n2": {
                    "type": "action",
                    "label": "Confirm-delivery task",
                    "config": {
                        "action": "crm.create_task",
                        "input": {
                            "title": "Confirm delivery for order #{{ trigger.order_id }}",
                            "related_type": "contact",
                            "related_id": "{{ trigger.contact_id }}",
                            "priority": "medium",
                            "created_by_id": "__INSTALLER__",
                        },
                    },
                    "next": "n3",
                    "position": {"x": 420, "y": 80},
                },
                "n3": {
                    "type": "action",
                    "label": "Notify customer (placeholder)",
                    "config": {
                        "action": "crm.http.request",
                        "input": {
                            "url": "https://httpbin.org/post",
                            "method": "POST",
                            "body": {
                                "kind": "shipping_notification",
                                "tracking_number": "{{ trigger.tracking_number }}",
                                "order_id": "{{ trigger.order_id }}",
                            },
                        },
                    },
                    "next": "end",
                    "position": {"x": 760, "y": 80},
                },
                "end": {"type": "end", "position": {"x": 1100, "y": 80}},
            },
        },
    },

    # 10. Payment success — Stripe-style webhook. Updates the deal stage
    # to closed_won + drops a payment-received note on the contact.
    {
        "slug": "payment-success",
        "name": "Payment success",
        "icon_emoji": "💳",
        "category": MarketplaceAgentCategory.PAYMENTS,
        "description": "Payment-provider webhook → move deal to closed_won + thank-you note.",
        "long_description": (
            "Webhook trigger. The payload should carry deal_id / contact_id / "
            "amount / provider_charge_id. Moves the deal to closed_won via "
            "crm.move_deal_stage and drops a thank-you note. Wire your Stripe / "
            "Paddle / LemonSqueezy 'charge.succeeded' webhook here."
        ),
        "trigger": {"type": "webhook"},
        "graph": {
            "start_node_id": "n1",
            "nodes": {
                "n1": {
                    "type": "action",
                    "label": "Move deal → closed_won",
                    "config": {
                        "action": "crm.move_deal_stage",
                        "input": {
                            "deal_id": "{{ trigger.deal_id }}",
                            "stage_id": "closed_won",
                        },
                    },
                    "next": "n2",
                    "position": {"x": 80, "y": 80},
                },
                "n2": {
                    "type": "action",
                    "label": "Thank-you note",
                    "config": {
                        "action": "crm.create_note",
                        "input": {
                            "body_md": "## 💳 Payment received\n\n- Amount: {{ trigger.amount }}\n- Provider charge: {{ trigger.provider_charge_id }}\n\nThanks!",
                            "related_type": "contact",
                            "related_id": "{{ trigger.contact_id }}",
                            "author_id": "__INSTALLER__",
                        },
                    },
                    "next": "end",
                    "position": {"x": 420, "y": 80},
                },
                "end": {"type": "end", "position": {"x": 760, "y": 80}},
            },
        },
    },

    # 11. Failed payment retry — Stripe-style "charge.failed" webhook.
    # High-priority retry task + flag note + outbound ping to ops.
    {
        "slug": "failed-payment-retry",
        "name": "Failed payment retry",
        "icon_emoji": "💸",
        "category": MarketplaceAgentCategory.PAYMENTS,
        "description": "Payment-provider failure webhook → urgent recovery task + ops ping.",
        "long_description": (
            "Webhook trigger. The payload should carry contact_id / deal_id / "
            "amount / failure_reason. Drops a flag note, queues an urgent task, "
            "and pings ops via crm.http.request. Combine with a HITL approval "
            "node when the retry value warrants manual review."
        ),
        "trigger": {"type": "webhook"},
        "graph": {
            "start_node_id": "n1",
            "nodes": {
                "n1": {
                    "type": "action",
                    "label": "Note failure",
                    "config": {
                        "action": "crm.create_note",
                        "input": {
                            "body_md": "## 💸 Payment failed\n\n- Amount: {{ trigger.amount }}\n- Reason: {{ trigger.failure_reason }}\n\n**Action required.**",
                            "related_type": "contact",
                            "related_id": "{{ trigger.contact_id }}",
                            "author_id": "__INSTALLER__",
                        },
                    },
                    "next": "n2",
                    "position": {"x": 80, "y": 80},
                },
                "n2": {
                    "type": "action",
                    "label": "Queue urgent retry",
                    "config": {
                        "action": "crm.create_task",
                        "input": {
                            "title": "Retry failed payment — {{ trigger.amount }}",
                            "description": "Reason: {{ trigger.failure_reason }}",
                            "related_type": "contact",
                            "related_id": "{{ trigger.contact_id }}",
                            "priority": "high",
                            "created_by_id": "__INSTALLER__",
                        },
                    },
                    "next": "n3",
                    "position": {"x": 420, "y": 80},
                },
                "n3": {
                    "type": "action",
                    "label": "Ping ops",
                    "config": {
                        "action": "crm.http.request",
                        "input": {
                            "url": "https://httpbin.org/post",
                            "method": "POST",
                            "body": {
                                "kind": "payment_failed",
                                "contact_id": "{{ trigger.contact_id }}",
                                "amount": "{{ trigger.amount }}",
                            },
                        },
                    },
                    "next": "end",
                    "position": {"x": 760, "y": 80},
                },
                "end": {"type": "end", "position": {"x": 1100, "y": 80}},
            },
        },
    },

    # 12. Refund request handler — public form for refund requests.
    # Creates contact (if new) + urgent task for the support team.
    {
        "slug": "refund-request-handler",
        "name": "Refund request handler",
        "icon_emoji": "↩️",
        "category": MarketplaceAgentCategory.CUSTOMER_SERVICE,
        "description": "Public refund form → contact upsert + urgent CS task with order details.",
        "long_description": (
            "Form trigger. The submitted form should carry first_name / "
            "primary_email / order_id / reason. Upserts the contact, drops a "
            "refund-request note with the full reason, and queues an urgent "
            "CS task. Pair with a HITL approval node before any auto-refund."
        ),
        "trigger": {"type": "form"},
        "graph": {
            "start_node_id": "n1",
            "nodes": {
                "n1": {
                    "type": "action",
                    "label": "Upsert refund-requester",
                    "config": {
                        "action": "crm.create_contact",
                        "input": {
                            "first_name": "{{ trigger.first_name }}",
                            "last_name": "{{ trigger.last_name }}",
                            "primary_email": "{{ trigger.primary_email }}",
                            "source": "refund_form",
                            "created_by_id": "__INSTALLER__",
                        },
                    },
                    "next": "n2",
                    "position": {"x": 80, "y": 80},
                },
                "n2": {
                    "type": "action",
                    "label": "Log refund reason",
                    "config": {
                        "action": "crm.create_note",
                        "input": {
                            "body_md": "## ↩️ Refund request\n\n- Order #: {{ trigger.order_id }}\n- Reason: {{ trigger.reason }}",
                            "related_type": "contact",
                            "related_id": "{{ n1.contact_id }}",
                            "author_id": "__INSTALLER__",
                        },
                    },
                    "next": "n3",
                    "position": {"x": 420, "y": 80},
                },
                "n3": {
                    "type": "action",
                    "label": "Queue urgent CS task",
                    "config": {
                        "action": "crm.create_task",
                        "input": {
                            "title": "Refund request — order #{{ trigger.order_id }}",
                            "description": "Reason: {{ trigger.reason }}. Review eligibility before approving.",
                            "related_type": "contact",
                            "related_id": "{{ n1.contact_id }}",
                            "priority": "high",
                            "created_by_id": "__INSTALLER__",
                        },
                    },
                    "next": "end",
                    "position": {"x": 760, "y": 80},
                },
                "end": {"type": "end", "position": {"x": 1100, "y": 80}},
            },
        },
    },

    # 13. Post-purchase review request — record(deal.stage_changed)
    # when the deal hits closed_won. Drops a "ask for a review" task.
    {
        "slug": "post-purchase-review-request",
        "name": "Post-purchase review request",
        "icon_emoji": "⭐",
        "category": MarketplaceAgentCategory.CUSTOMER_SERVICE,
        "description": "Deal closed_won → queue a task to ask the customer for a review.",
        "long_description": (
            "Triggers when any deal moves to closed_won. Drops a note "
            "acknowledging the win and queues a 'ask for review' task. "
            "Customize the task title to match your review platform "
            "(Trustpilot, G2, Capterra, etc.)."
        ),
        "trigger": {"type": "record", "entity_type": "deal", "event": "stage_changed"},
        "graph": {
            "start_node_id": "n1",
            "nodes": {
                "n1": {
                    "type": "branch",
                    "label": "Won?",
                    "config": {
                        "field": "trigger.stage_id",
                        "op": "eq",
                        "value": "closed_won",
                    },
                    "true_next": "n2",
                    "false_next": "end",
                    "position": {"x": 80, "y": 80},
                },
                "n2": {
                    "type": "action",
                    "label": "Queue review request",
                    "config": {
                        "action": "crm.create_task",
                        "input": {
                            "title": "Ask for a review",
                            "description": "Reach out to the customer 1-2 weeks after purchase to request a public review.",
                            "related_type": "deal",
                            "related_id": "{{ trigger.record_id }}",
                            "priority": "medium",
                            "created_by_id": "__INSTALLER__",
                        },
                    },
                    "next": "end",
                    "position": {"x": 420, "y": 80},
                },
                "end": {"type": "end", "position": {"x": 760, "y": 80}},
            },
        },
    },

    # 14. Repeat-purchase nudge — Weekly schedule (use ScheduleTrigger
    # row pointing at the installed automation). Logs that the sweep
    # fired — extend with crm.loop over your stale-customer list once
    # custom-field queries are available (M11+).
    {
        "slug": "repeat-purchase-nudge",
        "name": "Repeat-purchase nudge",
        "icon_emoji": "🔁",
        "category": MarketplaceAgentCategory.COMMS,
        "description": "Weekly schedule that loops over stale customers and queues re-engagement tasks.",
        "long_description": (
            "Schedule trigger. The agent's body iterates over a list of stale "
            "customer ids (passed in via the schedule's trigger_payload) and "
            "queues a re-engagement task per customer. Wire a ScheduleTrigger "
            "row (cron `0 9 * * MON` for Monday-9am-UTC) after install. "
            "Replace the placeholder items list with a real query in M11."
        ),
        "trigger": {"type": "schedule"},
        "graph": {
            "start_node_id": "n1",
            "nodes": {
                "n1": {
                    "type": "action",
                    "label": "Log sweep start",
                    "config": {
                        "action": "log",
                        "input": {
                            "message": "repeat-purchase-nudge sweep started",
                            "cron": "{{ trigger.cron }}",
                        },
                    },
                    "next": "n2",
                    "position": {"x": 80, "y": 80},
                },
                "n2": {
                    "type": "action",
                    "label": "Loop over stale customers",
                    "config": {
                        "action": "crm.loop",
                        "input": {
                            "items": [],
                            "inner_action": "log",
                            "inner_input": {
                                "message": "re-engage customer",
                                "customer_id": "{{ item.id }}",
                                "index": "{{ index }}",
                            },
                            "on_error": "continue",
                            "max_items": 200,
                        },
                    },
                    "next": "end",
                    "position": {"x": 420, "y": 80},
                },
                "end": {"type": "end", "position": {"x": 760, "y": 80}},
            },
        },
    },
]


def upsert_agents() -> int:
    created = 0
    updated = 0
    for spec in SEED_AGENTS:
        slug = spec["slug"]
        # Don't clobber install_count if the agent already exists.
        existing = MarketplaceAgent.objects.filter(slug=slug).first()
        defaults = {k: v for k, v in spec.items() if k != "slug"}
        defaults.setdefault("is_published", True)
        if existing:
            for field, value in defaults.items():
                setattr(existing, field, value)
            existing.save()
            updated += 1
        else:
            MarketplaceAgent.objects.create(slug=slug, **defaults)
            created += 1
    total = MarketplaceAgent.objects.count()
    print(f"marketplace seed: created={created} updated={updated} total={total}")
    return total


if __name__ == "__main__":
    upsert_agents()
