# Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Vapi call finishes but nothing runs | Vapi points at the `webhook-test` URL, or workflow not published | Use the **Production URL** and publish the workflow |
| 404 from webhook | Path changed after setting Vapi URL | Re-copy the URL from the webhook node |
| Webhook returns 401/403 | Header Auth secret mismatch | Use the same secret in Vapi and the node |
| Empty customer fields | Structured output not attached or field names differ | Check the Vapi structured output names (Setup step 6.4) |
| `AI_ANALYSIS_FAILED` in log | Agent error or a required heading is missing | Open the execution, inspect the agent output; re-run |
| Google 403 / "file not found" on move | Wrong folder ID or credential has no access | Check folder IDs and that the OAuth account owns or can edit the folders |
| Slides populate returns 400 | Unexpected section structure | Inspect `proposal_text` in the data table; verify headings and bullets |
| Duplicate rows in the log | Upsert matching not set | Set matching on `call_id` |
| Phone number read back wrongly by the voice agent | Speech-to-text and read-back issue | Fix in the Vapi assistant prompt, not in n8n |
