# loops/crm-autolog — dated run notes from David's Gmail/Calendar auto-log loop

Weekdays 08:15 ET (`yourco-crm-autolog.timer`). Each run scans the last 2 weekdays of Gmail
(+Calendar if the connector is live) for threads involving CRM contacts and drafts pending
activities into `crm/_pending-activities.json` — the human confirms each one in the CRM UI
("Pending — confirm to save"). The loop NEVER writes `crm/data.json`.
One dated note per run: scanned / proposed / skipped. Quiet day → says so honestly.
