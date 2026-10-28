# Vapi voice assistant setup

This workflow is the receiving half of the system. The sending half is a Vapi voice assistant that runs the discovery call and reports it to your n8n webhook when the call ends. This page lists what the Vapi side needs so the workflow receives what it expects.

> The assistant name "Roy" is an example. Use any name; the workflow only uses it to label transcript lines.

## 1. Report delivery

| Setting | Value |
| --- | --- |
| Server URL | Your n8n webhook (see [SETUP.md](SETUP.md)) |
| Server messages | `end-of-call-report` only |
| Structured output | One output named `Discovery Lead Details`, attached to the assistant |

Use the n8n **test** URL (`/webhook-test/`) only while the workflow is listening. For real calls, activate the workflow and use the **production** URL (`/webhook/`).

## 2. Structured output fields

Create a structured output whose result contains these fields. Anything the caller did not say should be `null`, `"Not provided"` or `"Not confirmed"`, never a guess.

| Field | Type | Notes |
| --- | --- | --- |
| `customer_name` | string | |
| `business_name` | string | |
| `customer_role` | string | |
| `customer_email` | string | |
| `customer_phone` | string | |
| `business_need` | string | |
| `desired_outcome` | string | |
| `systems_mentioned` | array of strings | |
| `follow_up_consent` | string | `Confirmed` / `Not confirmed` |
| `current_process` | string | Optional extra context |
| `pain_points` | array of strings | Optional |
| `business_impact` | string | Optional |
| `workflow_details` | object | `trigger`, `current_steps`, `desired_automation`, `human_approval_required` |
| `success_criteria` | array of strings | Optional |
| `constraints` | array of strings | Optional |
| `budget`, `desired_timeframe`, `decision_maker` | string | Optional |

The first nine rows are the fields the workflow reads as named values. The optional fields are passed through in the report and are also available to the AI step through the transcript.

Vapi nests the result under `message.artifact.structuredOutputs`. The workflow's **Normalize Vapi Payload** node unwraps it, so you do not need to flatten anything. See [`examples/sample-end-of-call-report.json`](../examples/sample-end-of-call-report.json) for the exact shape.

## 3. Conversation behaviour that worked well

These instructions fixed the main problems seen in test calls. Add them to your assistant's prompt in your own words.

- Wait for the caller to finish. Allow pauses and self-corrections before replying.
- If an interruption does not answer the question, acknowledge it and ask the unfinished question again, shorter.
- A short "okay" or "got it" is not an answer to an open question.
- Learn what the business does, who it serves and the caller's role before diagnosing the process.
- Ask about each topic once. Treat differently worded questions on the same subject (for example tools) as duplicates.
- Repeat the caller's contact details slowly and ask them to confirm.
- Summarise, ask "anything else you'd like me to note?", and wait for the answer.
- Say a complete goodbye before the call ends. If your platform lets the end-call tool speak its own message, use that as a safeguard so the call can never end silently.

## 4. Test before going live

1. Send a sample report without a phone call:

   ```bash
   export N8N_WEBHOOK_URL="https://<your-n8n-host>/webhook-test/<your-webhook-path>"
   python3 scripts/send_test_payload.py
   ```

   Use `--dry-run` to see the payload without sending it.
2. Make one real call and confirm a delivery with a `2xx` response in Vapi's webhook logs.
3. Test partial calls, missing contact details, a caller who hangs up early and a malformed email or phone number.
4. In n8n, confirm one Data Table row per call and no duplicates on retry.

## 5. Production checklist

- [ ] Workflow active and production webhook URL installed in Vapi
- [ ] Webhook path is a long random value, and you have considered adding authentication
- [ ] First real call shows a `2xx` delivery and a complete Google Doc, proposal and deck
- [ ] Call recordings and transcripts handled in line with your privacy policy and local consent rules
