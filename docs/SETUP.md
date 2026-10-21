# Setup Guide

## 1. Prerequisites
- n8n (cloud or self-hosted) with **Data Tables**, the AI Agent node, OpenAI and Brave Search nodes
- Google account with Docs, Slides and Drive
- OpenAI API key and Brave Search API key (or n8n gateway credits)
- Vapi account and assistant

## 2. Import the workflow
n8n > Workflows > **Import from file** > `workflows/vapi-discovery-to-proposal.json`.
The workflow imports **inactive**.

## 3. Create credentials in n8n
| Nodes | Credential type |
|---|---|
| Google Docs - Create / Write / Get Client Inquiry | Google Docs OAuth2 |
| Google Slides - Create / Populate Proposal | Google Slides OAuth2 |
| Google Drive - Move Inquiry / Move Proposal | Google Drive OAuth2 |
| OpenAI Chat Model | OpenAI API |
| Brave Web Search | Brave Search API |

Open each node and re-select the credential (placeholders show `REPLACE_ME`).

## 4. Replace placeholders
| Placeholder | Location | Value |
|---|---|---|
| `YOUR_INQUIRIES_FOLDER_ID` | Google Docs - Create Client Inquiry; Google Drive - Move Inquiry to Folder | ID of the Drive folder for inquiry docs |
| `YOUR_PROPOSALS_FOLDER_ID` | Google Drive - Move Proposal to Folder | ID of the Drive folder for decks |
| `YOUR_DATA_TABLE_ID` | Upsert Discovery Call Log | Select your data table |
| `REPLACE_WITH_LONG_RANDOM_SECRET` | Vapi Discovery Webhook `path` | Long random string; treat as a secret |

A Drive folder ID is the last part of the folder URL: `drive.google.com/drive/folders/<ID>`.

## 4b. Add your branding
The workflow is brand-neutral. Search the workflow for `Your Agency` / `YOUR AGENCY` and replace it with your own name in:
- the AI agent system prompt (Analyze Discovery Call and Draft Proposal)
- the document and deck title expressions (`Your Agency - ...`)
- the inquiry doc header and the slide header/footer text (Build Slides Batch Requests, Google Docs - Write Client Inquiry)

## 5. Create the data table
Name: `Discovery Call Log` (any name works; you select it by ID). All columns are strings except `received_at` (date/time):

`call_id, received_at, event_type, transcript, proposal_title, proposal_text, google_doc_url, approval_status, canva_status, processing_status, error_message, customer_name, business_name, customer_email, customer_phone, customer_role, business_need, desired_outcome, systems_mentioned, follow_up_consent, structured_data, canva_design_url`

Open **Upsert Discovery Call Log** and set matching to `call_id` so retries update the row instead of duplicating it.

## 6. Connect Vapi
1. Copy the webhook **Production URL** (not `webhook-test`).
2. Vapi > Assistant > **Server URL** = that URL. Server messages: `end-of-call-report` only.
3. Add **Header Auth** on the webhook node and send the same secret from Vapi.
4. Attach a structured output (name it *Discovery Lead Details*) with these fields: `customer_name`, `business_name`, `customer_email`, `customer_phone`, `customer_role`, `business_need`, `desired_outcome`, `systems_mentioned`, `follow_up_consent`. Optional: `pain_points`, `current_process`, `success_criteria`, `constraints`.

## 7. Test
1. Click **Execute workflow** (listening for a test event) and place a Vapi test call.
2. Confirm: an inquiry doc in the inquiries folder, a deck in the proposals folder, and a new data table row with status `PROPOSAL_DRAFT_CREATED_IN_GOOGLE_SLIDES`.
3. Review the deck. It must read as a draft for human review.

## 8. Go live
Publish the workflow, then point Vapi at the production URL. Monitor **Executions** for the first few calls.

## Recommended hardening
- Webhook authentication (step 6.3) so only Vapi can trigger runs.
- Add an Error Workflow to alert you on failures after the AI step (Slides and Drive nodes).
- Rotate the webhook secret periodically.
