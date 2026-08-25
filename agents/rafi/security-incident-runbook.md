> **Imported 2026-06-11** from the prior "YourCo LLC" Desktop archive (v2). Part of Rafi’s compliance suite; implements the DPA’s 72-hour breach-notification duty. **Counsel-review-required; reconcile to the current stack** before relying on it.

---

INTERNAL · SECURITY INCIDENT RUNBOOK · v2
When something goes wrong.
This runbook covers what to do when there is — or might be — a Security Incident affecting Personal Information that YourCo processes on behalf of clients. It satisfies YourCo's commitments under DPA Section 10 (72-hour notification) and gives a single human (you) a clear sequence of steps to follow under stress.
Read this BEFORE you need it
The whole point of a runbook is that it works at 11pm on a Tuesday when you're alone, tired, and worried. Read it cold once now, so the structure is familiar. Print the wall card on the last page and put it somewhere you'll see it. When something goes wrong, you'll have approximately zero capacity for novel problem-solving — you need a script.
How to use this document
	•	If you're reading this because something just happened: skip to the wall card on the last page first. Come back here once you've taken the first 4 actions on the card.
	•	If you're reading this for training: read cover to cover, then walk through the sample scenarios at the end.
	•	If you're reading this for compliance review (DPA audit, client security questionnaire): the structure mirrors DPA Section 10. The notification template at the back is what gets sent to clients.
The bias is toward over-reaction, not under-reaction. If you're not sure whether something is a Security Incident, treat it like one until investigation proves otherwise. The cost of a false alarm is a few hours of your time. The cost of a missed real incident is regulatory exposure, contractual breach, and customer trust.
What counts as a Security Incident
The DPA Section 1.5 definition: "any unauthorized access to, acquisition, use, disclosure, alteration, or destruction of Personal Information Processed by YourCo in connection with the Services."
In plain English: anything that means a person who shouldn't have client data either saw it, copied it, changed it, or deleted it (or anything that suggests they might have).
Triggers — declare a Security Incident if any of these happen
Account compromise
	•	YourCo's Anthropic API console, OpenAI API console, Google Workspace, GoHighLevel, Notion, Slack, AWS, or any other administrative account shows unauthorized login activity (login from unfamiliar location, login at unusual time, MFA challenge you didn't initiate).
	•	Suspicious password reset email arrives that you didn't request, OR your password no longer works on a system you used recently.
	•	You realize you clicked a phishing link and entered credentials, even if no follow-on activity is yet visible.
Device compromise
	•	Laptop, phone, or tablet with active sessions to client systems is lost, stolen, or left unattended in an untrusted location.
	•	Malware detection alert from any endpoint YourCo uses to access client data.
	•	Family member, friend, contractor, or anyone else gained access to an unlocked device with active client sessions.
Subprocessor incident
	•	Anthropic, OpenAI, Google (Workspace), AWS, Stripe, GoHighLevel, Notion, Slack, or any other listed Subprocessor notifies YourCo of a security incident affecting their platform.
	•	News reports a breach at any Subprocessor that processes Personal Information for YourCo's clients (verify with the Subprocessor before declaring, but don't wait too long — the clock starts at awareness, not confirmation).
Data exposure
	•	Client data inadvertently sent to the wrong client (e.g., reply-all, attachment going to wrong recipient, Slack message to wrong channel, agent output routed to wrong destination).
	•	Client data found in a publicly accessible location (Google Drive folder set to "anyone with link," S3 bucket misconfigured, Notion page accidentally made public, etc.).
	•	AI agent output that includes confidential or personal information when it shouldn't (e.g., agent leaks one client's data into another client's session).
	•	Prompt-injection attack causes an agent to disclose confidential information or take unauthorized action on Client's behalf.
Loss or destruction
	•	Discovery that a meaningful amount of client data was deleted unintentionally (regardless of cause — human error, automation bug, infrastructure failure).
	•	Backup or recovery system fails when needed AND data cannot be restored.
What does NOT count (but document anyway)
	•	A failed login attempt by an attacker that did not succeed (record in incident log, no DPA notification needed).
	•	A spam phishing email that you correctly identified and did not act on (record in incident log).
	•	A subprocessor service outage (operational issue, not security; document under reliability incidents instead).
	•	A client asking you to delete their data (this is a Data Subject Request under DPA Section 9, separate process).
	•	An AI agent producing a low-quality output that is corrected by Client review (this is a quality issue, not a security incident, unless it caused exposure of confidential information).
When in doubt, declare. An over-declared incident gets de-classified in Phase 2 with no harm done. An under-declared incident becomes an unreported breach.
The 72-hour clock
Per DPA Section 10, YourCo will notify each affected Client of any Security Incident affecting their Personal Information "without undue delay, and in any event within seventy-two (72) hours after becoming aware of the Security Incident."
When does "becoming aware" start?
Awareness starts the moment YourCo has more than fleeting suspicion that an incident occurred. Specifically:
	•	If a tool fires an alert (suspicious login, malware detection, etc.), awareness = the timestamp of the alert.
	•	If a Subprocessor notifies YourCo, awareness = the timestamp of their notification.
	•	If you discover an incident yourself (lost device, misdirected email, agent producing unexpected output), awareness = the moment you realized.
	•	If a client reports something to YourCo that turns out to be an incident, awareness = the timestamp of their report.
What you must do within 72 hours
Send each affected client a notification that contains, to the extent known at the time:
	•	The nature of the Security Incident.
	•	The categories and approximate number of Data Subjects and records affected.
	•	The likely consequences of the Security Incident.
	•	The measures taken or proposed to address it and mitigate effects.
These four points are required by DPA Section 10. The notification template at the back of this runbook is structured around them.
"To the extent known" is doing real work
You are NOT required to have a complete picture before notifying. You ARE required to notify with what you know, and follow up as you learn more. Most regulators and contracts treat partial-but-prompt notification favorably. Late notification with a complete picture is treated badly.
If at hour 60 you still don't know the full scope, send the notification anyway with what you know. Mark sections "under investigation" and commit to a follow-up notification within X days. This is the right move.
PHASE 1 — Detect and contain
First 0–4 hours · Goal: stop the bleeding without destroying evidence.
DO NOT panic-fix. The instinct to immediately delete suspicious files, force-logout sessions, or reset passwords can destroy evidence needed later. Containment is good. Eradication-before-investigation is bad. Take the actions below in order, no skipping ahead.
Step 1 — Stop and write down the time
☐  Open a notes app or grab a notebook. Write today's date and the current time. This is your awareness timestamp — it starts the 72-hour clock.
☐  Write a one-paragraph plain-English description of what made you suspect something is wrong. Don't edit. Don't analyze. Just record.
Step 2 — Decide if this is real (5 minutes max)
☐  Is there any chance this is a false alarm? (e.g., the "unusual login" was from your own laptop on a VPN.) Verify quickly — but do NOT spend more than 5 minutes ruling it out.
☐  If you can't conclusively rule it out in 5 minutes: declare. Move to Step 3. The cost of false declaration is small.
Step 3 — Contain (do not eradicate)
Containment depends on what kind of incident it is. Pick the relevant block and execute.
If it's an account compromise (Anthropic, Google, GHL, Notion, Slack, etc.):
☐  Sign out all sessions on the affected account from the account's security settings (do NOT change the password yet — changing it now may destroy evidence of how the attacker got in).
☐  Enable MFA if it wasn't already enabled. Force-rotate any API keys associated with the account.
☐  Note exactly what you changed and at what time. Take screenshots of any visible session/login history before any further changes.
☐  DO NOT delete any suspicious emails, files, or activity yet — they're evidence.
If it's a device compromise (laptop, phone):
☐  If the device is lost or stolen: remote-wipe via Google Workspace admin / Apple Find My / equivalent. Disable any active session keys. Take a screenshot of the wipe confirmation.
☐  If you suspect malware on a device you still have: disconnect from the network (turn off WiFi, unplug ethernet) but DO NOT power off — running memory has evidence. Take it to a quiet corner.
☐  Do not log into any client systems from any other device until Phase 2 starts.
If it's a Subprocessor incident:
☐  Acknowledge the Subprocessor's notification in writing. Note the timestamp of their notice (this is your awareness timestamp).
☐  Ask the Subprocessor for: which client data is potentially affected, what they know about scope, what they're doing about it, what their notification timeline is.
☐  Do NOT cancel the Subprocessor relationship in panic. Don't make changes that would prevent forensic cooperation.
If it's a data exposure (misdirected email, public link, wrong agent recipient, etc.):
☐  Recall the message if possible (Gmail "undo send," Outlook recall — only works in narrow windows). Don't assume recall succeeded.
☐  Revoke link sharing on any publicly exposed file/folder. Verify the new sharing setting actually took effect.
☐  If an AI agent caused the exposure, pause the agent immediately to prevent recurrence. See the Lights-On Documentation for the affected agent's pause procedure.
☐  Take screenshots of the exposure as it stood (Drive sharing dialog, the misdirected email, agent output, etc.) — evidence.
If it's a prompt-injection or AI-specific incident:
☐  Pause the affected agent immediately. Note the time.
☐  Preserve the input that triggered the issue (the user prompt, the data the agent ingested, etc.) — evidence.
☐  Preserve the agent's output, even if you'd rather not look at it. The output is the evidence of what was disclosed.
☐  Identify which Client(s) are affected. With multi-tenant agents, an injection affecting one Client may have affected only one Client's data — don't assume "all clients" until you've checked.
Step 4 — Notify yourself in writing
☐  Send yourself an email to founder@yourco.example.com summarizing what happened, when you became aware, what you've contained so far. This becomes the start of your incident log and is timestamped by Gmail.
PHASE 2 — Investigate
Hours 4–24 · Goal: understand scope before notifying.
By now containment is in place and the immediate panic has passed. Use this window to figure out what actually happened, what data was actually affected, and what to tell clients. Keep notes the entire time — your notes are the foundation of the eventual notification email and any post-incident review.
What to gather
	•	Audit logs from any system involved (Google Workspace login history, Anthropic API console activity, GHL admin activity log, Notion access logs, AWS CloudTrail, etc.).
	•	List of clients whose data is or might be affected. Be specific — name them. "All clients" is rarely accurate; usually it's a subset.
	•	List of data categories potentially exposed (business contact info, project documents, agent outputs, communication content).
	•	Approximate number of Data Subjects affected (the actual people whose info was in the data, not the clients). Round generously — "approximately 500" is fine; "exactly 487" is suspicious if you can't actually count them.
	•	Best guess at root cause (phishing, weak password, Subprocessor breach, your own mistake, agent prompt-injection, misconfiguration).
Who to involve
	•	If there's any possibility of legal exposure or regulatory question: contact your Florida business attorney before sending the client notification. Even a 30-minute call before notification is worth it.
	•	If there's any possibility of criminal activity (theft, attack with malicious intent): consider whether to file a police report. Generally yes, but consult counsel first.
PHASE 3 — Notify
Hours 24–72 · Goal: notify each affected client in writing within DPA-required timing.
Send the notification
	•	Use the notification template at the end of this runbook. Customize per client (name, what data of theirs was affected, etc.).
	•	Send via direct email to the Client's primary contact. CC any escalation contact identified during onboarding.
	•	Post the notification (or a summary) to any client-shared workspace where you regularly communicate with the client.
	•	Confirm delivery — Gmail read receipt, response from client, or follow-up phone call within 24 hours of sending.
After sending — be available
Clients often have follow-up questions in the hours and days after receiving an incident notification. Make yourself available. Avoid leaving questions unanswered for more than a few hours.
PHASE 4 — Remediate and Learn
Days 3–30 · Goal: close the incident and prevent recurrence.
Eradication
☐  Now you can change passwords, delete malicious files, revoke compromised credentials. Evidence is preserved (or has been collected) and forensic work is done.
☐  Verify the root cause is actually addressed. "We rotated the password" is not a fix if the credential leaked because of a phishing pattern that will repeat.
Documentation
☐  Write a post-mortem within 14 days. What happened, what we did, what we'll change. File in the Incident Log.
☐  Send a closing notification to affected clients confirming the incident is closed and summarizing remediation.
Pattern analysis
	•	Add the incident to the Incident Log (see template at end of runbook).
	•	Review the log quarterly. Look for repeat patterns — same Subprocessor, same control gap, same human error mode. That's the real signal.
Incident log fields
Maintain this log for every incident — including ones that turn out to be false alarms. Pattern analysis across the log over time is the single best signal of whether YourCo's security posture is improving or drifting.

Incident ID
INC-YYYY-NNN sequential (e.g., INC-2026-001)
Awareness date/time
When YourCo became aware. Starts the 72-hour clock.
Reporter
Who first noticed (you, a tool alert, a Subprocessor, a client)
Initial classification
Suspected incident / confirmed incident / false alarm
Final classification
Updated after Phase 2 — true incident / false alarm / inconclusive
Affected systems
List the specific systems involved
Affected clients
Named list — "all clients" should be rare and verified
Affected data categories
What kinds of data were potentially exposed
Approximate Data Subjects
Number of end-users (your clients' partners/employees/customers) potentially affected
Root cause
The actual underlying cause, not the proximate trigger
Containment timeline
When each major containment step was taken
Notification sent? When?
Date/time client notification went out, OR reason notification was not required
Subprocessor involved?
Name + their incident reference if applicable
Counsel consulted?
Yes/No, who, when
Law enforcement involved?
Yes/No
Remediation actions taken
Specific control updates, training, process changes
Post-mortem doc location
Link to the post-mortem document in Drive or Notion
Status
Open / In remediation / Closed
Closed date
When the incident was officially closed

Where the log lives
	•	Internal Notion or Google Drive folder named "Security Incident Log," access restricted to YourCo personnel only.
	•	One row per incident in a master spreadsheet for quick scanning. One detailed document per incident for full record.
	•	Retain incident records for at least 7 years per YourCo's data retention practice. Some regulators may require longer.
	•	Never include this log in marketing materials, sales decks, or anything client-facing without explicit redaction.
Client notification email template
Customize the {placeholders}. Send within 72 hours of awareness. Do not wait for a complete investigation if it would cause you to miss the window. Have your Florida business attorney review the customized version before sending if there is any chance of regulatory or contractual exposure beyond the DPA. The 72-hour clock allows time for legal review — use it.

Subject: Important: Security Incident Notification — {Client Company}

Hi {first_name},

I'm writing to notify you of a security incident that has affected — or may have affected — Personal Information that YourCo Processes on your behalf. Per Section 10 of our Data Processing Addendum, I am required to notify you within 72 hours of becoming aware. I'm writing within {X} hours of awareness.

1. NATURE OF THE INCIDENT
{Plain-English description of what happened. Examples: "On {date} at {time}, an attacker gained access to my Anthropic API console through a phishing email. The unauthorized access lasted approximately {duration} before I identified and revoked it." or "On {date}, our Subprocessor {name} notified us of a security incident affecting their platform; YourCo's data was identified as among the potentially affected scope."}

2. AFFECTED DATA AND DATA SUBJECTS
Based on our investigation to date:
	•	Categories of Personal Information potentially affected: {list — e.g., business contact information, project documents, agent inputs/outputs}
	•	Approximate number of records: {number, with "under investigation" if not yet known}
	•	Estimated number of Data Subjects (your partners, employees, customers, or others whose information appears in your data): {number}

We estimate that approximately {number} of your end-users (Data Subjects) may have data within the affected set. We are continuing to refine this number; we will update you if it changes materially.

3. LIKELY CONSEQUENCES
{Honest assessment of what the affected data could be used for. Examples: "The data does not include payment information or government identifiers, so direct financial fraud risk is limited. The primary risk is that contact information could be used in subsequent phishing attempts targeting your team."}

{If applicable: "At this time, we have no evidence that the data has been viewed or copied by an unauthorized party — only that the unauthorized access occurred. We will inform you immediately if that changes."}

4. MEASURES TAKEN AND PROPOSED
Within {X} hours of becoming aware, YourCo:
	•	{Containment action 1 — e.g., "forced log-out of all sessions on the compromised account and rotated credentials"}
	•	{Containment action 2 — e.g., "enabled multi-factor authentication on all administrative accounts that did not already have it"}
	•	{Containment action 3 — e.g., "preserved audit logs and engaged in forensic review of the activity timeline"}

Over the next {X} days, we will:
	•	Complete the forensic investigation and provide you with a final scoping report.
	•	{Specific remediation step relevant to the incident type}
	•	Conduct an internal post-mortem and update our security controls accordingly.

WHAT YOU MAY WANT TO CONSIDER
Depending on your business and your jurisdiction, you may have your own notification obligations under applicable privacy laws. We are not in a position to advise on those obligations, but we will provide whatever technical information you need to fulfill them. If it would help, I can join a call with your counsel.

I recognize this is not the email anyone wants to receive. I am committed to keeping you fully informed as we learn more and as remediation progresses. Expect an update from me by {commit_date} at the latest, even if it is just to confirm there is nothing new.

If you have any questions, reach me directly: founder@yourco.example.com.

the Founder
Founder, YourCo LLC
Sample scenarios — training appendix
Three worked scenarios illustrating how the runbook applies in practice. Read these cold once now. They will make the structure stick better than reading the runbook alone.
Scenario 1: Phishing email gives attacker Anthropic API console access
What happens
Tuesday 9:47 AM ET. You click a link in an email that looks like a legitimate Anthropic security alert. You enter your password and approve the MFA push notification (assuming it's the legitimate Anthropic login flow you initiated). At 10:03 AM you notice an unfamiliar device in your Anthropic account's security activity. The device's IP geolocates to Eastern Europe.
How you handle it
Phase 1 (10:03–10:30 AM):
	•	Awareness timestamp: 10:03 AM Tuesday. 72-hour deadline = Friday 10:03 AM.
	•	Sign out all sessions from the Anthropic account security page. Take screenshot of the unfamiliar device entry first.
	•	Check Anthropic billing / usage logs: any unusual activity? Any unexpected API calls? Take screenshots.
	•	Check related accounts (Google Workspace, GHL, AWS) for cross-contamination — was the same password reused anywhere? Take screenshots.
	•	Force-rotate Anthropic API keys. Force-rotate any related keys that share a password. Enable hardware-key MFA if not already on.
	•	Email yourself a one-paragraph description of what happened, which becomes the start of your incident log.
Phase 2 (10:30 AM–6 PM Tuesday):
	•	Pull Anthropic console audit log for the past 48 hours. Identify which API keys were viewed/exported, by whom (the unfamiliar device's session ID).
	•	Determine: 2 of 3 active client API keys were exfiltrated. The attacker has the keys but Anthropic's logs show no actual usage of them. YourCo immediately rotates both.
	•	List the affected clients by name. Determine whether any Personal Information was accessible via those keys.
	•	Call your Florida business attorney for a 30-minute review.
Phase 3 (Wednesday morning):
	•	Send notification email to each of the 2 affected clients using the template. Customize per client.
	•	Do NOT send anything to the unaffected client.
	•	Notification sent 24 hours after awareness — well within the 72-hour DPA window.
Phase 4 (Wednesday onward):
	•	Hardware-key MFA now mandatory on all YourCo accounts. Audit complete.
	•	Phishing training: review the specific email pattern, document for future reference.
	•	Post-mortem written within 14 days. Final scope confirmed: keys exfiltrated but no usage detected, 2 clients affected, no Data Subject impact.
	•	Closing notification sent to the 2 affected clients with final scope.
Scenario 2: Laptop stolen at airport with active sessions
What happens
Friday 4:30 PM. You realize at the gate that your MacBook is no longer in your bag. Last seen at the security checkpoint. The laptop was logged into Google Workspace, Anthropic console, GHL, Notion, and Slack, all with active session tokens. Notion had several Client documentation packages open in tabs.
How you handle it
Phase 1 (immediately):
	•	Awareness timestamp: 4:30 PM Friday. 72-hour deadline = Monday 4:30 PM.
	•	From your phone, log into Apple Find My and trigger remote-wipe. Take screenshot of the wipe command timestamp.
	•	Sign out all sessions on Google Workspace from another device. Same for Anthropic, GHL, Notion, Slack.
	•	File a police report at the airport — required for insurance, useful for evidence trail.
	•	Email yourself the incident description from your phone.
Phase 2 (Friday evening through Saturday):
	•	Verify remote-wipe completed (Apple confirmation email).
	•	Determine: did the device have client data cached locally? Yes — Notion offline files, Slack history, Google Drive offline files. So even with sessions invalidated, data on the device pre-wipe was at risk.
	•	Review what was on the device: client lights-on documentation, agent prompts and configurations, recent project notes.
	•	All YourCo clients potentially affected — though scope of cached data varies.
Phase 3 (Saturday afternoon):
	•	Send notification to all clients (this is one of the rare cases where "all clients" is genuinely accurate).
	•	Notification specifically calls out: device wiped within minutes of awareness; sessions invalidated; cached data was limited to recent operational documents and agent configurations.
	•	Notification sent ~24 hours after awareness.
Phase 4 (next 30 days):
	•	New laptop policy: no offline-cached client data on travel devices. Use a separate "travel" Google account with no admin access.
	•	FileVault / disk encryption verified on all devices. Auto-lock timeout shortened.
	•	Post-mortem written. Closing notification confirms no evidence of data access (police never recovered the device, but no signs of exfiltration in any account).
Scenario 3: AI agent prompt-injection causes data leak between clients
What happens
Wednesday 2:15 PM. While reviewing logs of a Working Pilot Agent operated for Client A, you notice an unusual output: in response to a user query, the agent included a brief summary that mentions a Client B project name. You realize a recent prompt-injection attack via a document Client A uploaded caused the agent to retrieve data from a shared knowledge store that should have been segmented by client.
How you handle it
Phase 1 (2:15–3:00 PM Wednesday):
	•	Awareness timestamp: 2:15 PM Wednesday. 72-hour deadline = Saturday 2:15 PM.
	•	Pause the agent immediately (per Lights-On Documentation Section 10.1).
	•	Preserve the agent's input (Client A's uploaded document) and output (the response that mentioned Client B). Do not delete.
	•	Identify exactly which Client B information was disclosed. In this case: a project name and one sentence of context. No personal information of Client B's Data Subjects was disclosed.
	•	Email yourself the incident description.
Phase 2 (Wednesday afternoon through Thursday):
	•	Investigate the segmentation failure. Determine that the knowledge store was insufficiently scoped between clients.
	•	Pull all of Client A's recent agent interactions. Confirm this is the only instance of cross-client leakage.
	•	Pull Client B's recent agent interactions. Confirm no Client A data leaked into Client B's outputs.
	•	Determine: only Client B is affected (their data was disclosed to Client A). Client A is the one who saw it but is not "affected" in the privacy sense.
Phase 3 (Thursday afternoon):
	•	Send notification to Client B. Be specific about what was disclosed and to whom (Client A).
	•	Send a separate, lower-stakes communication to Client A — they're not the affected party but they did see something they shouldn't have, and their cooperation is needed (e.g., asking them to delete the leaked output).
	•	Both communications sent within 48 hours of awareness.
Phase 4 (Thursday onward):
	•	Re-architect the agent's data retrieval so that segmentation is enforced at the storage layer, not just the prompt layer (more robust against future injection).
	•	Add prompt-injection test cases to your standard agent QA process.
	•	Post-mortem documents the architectural lesson for future agent design.

WALL CARD · PRINT THIS · TAPE IT WHERE YOU'LL SEE IT
Security Incident — first 30 minutes
Something went wrong. Read this before doing anything else.

AWARENESS TIMESTAMP: __________________________   (Date + Time + Time zone)

1.
STOP. Don't delete files. Don't change passwords yet. Don't email clients. Take a breath.
2.
Note the time. Write down today's date and the current time (down to the minute). This is your awareness timestamp. The 72-hour clock starts NOW.
3.
Write what you saw. One paragraph, plain English, no analysis. "At 10:03 AM I noticed an unfamiliar device in my Anthropic console."
4.
Contain. Sign out all sessions on the affected account. Rotate API keys. Pause any AI agent involved. Take screenshots before any further changes.
5.
Email yourself. Send the description from step 3 to founder@yourco.example.com. This timestamps your record.
6.
Stop here. Don't notify clients yet. Don't post anywhere. Open the runbook ("YourCo Security Incident Runbook v2") and follow Phase 2.

WHEN IN DOUBT, DECLARE.  Better an over-reaction. Treat as incident until proven false.
DO NOT email clients yet.  Phase 3 is for client notification. You're still in Phase 1. Follow the order.
DEADLINES TO REMEMBER:  Hour 4: containment complete · Hour 24: scope known · Hour 72: client notification sent (DPA Section 10).

YourCo LLC  ·  Security Incident Wall Card  ·  v2  ·  April 2026
Full runbook: "YourCo Security Incident Runbook v2" in Drive  ·  Counsel + DPA contacts: in operations binder
