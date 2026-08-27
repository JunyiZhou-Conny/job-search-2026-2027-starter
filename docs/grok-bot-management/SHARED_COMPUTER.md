# Shared computer (knowledge point)

Junyi 2026-08-25. Confirm against xAI docs, not against this Cloud Agent
looking at your live Grok Bot VM.

This is a fact about the product. It is not a runbook to spawn Bots or
to Submit.

## What is true

All Grok Bots on **one user account** share **one** persistent cloud
computer.

- Same filesystem (`/workspace` and other durable files).
- Same browser cookies and signed-in sessions. A login completed for
  Bot A is available to Bot B.
- Same command-line credentials.
- One Bot can continue from files another Bot saved.

The computer is assigned **per user**, not per Bot. Separate named
roles (Researcher, Writer, Ops, later autofill) are teammates on one
desktop. They are not separate vaults.

Official:

- [Do my Bots share one computer?](https://docs.x.ai/grok-bot/faq)
- [One computer, shared by all your Bots](https://docs.x.ai/grok-bot/computer-and-apps)
- [Understand the shared-computer boundary](https://docs.x.ai/grok-bot/approvals-security-and-privacy)

## Parallel work

Each Bot gets its **own screen** on that shared computer. Several Bots
can click and use the browser at the same time. One Bot can run only
one computer-use task on its screen at a time.

Those screens are work surfaces, not security boundaries.

## What is not shared

- Conversation and learned role stay per Bot unless they hand off or
  sit in a group thread.
- Your Mac/Windows laptop is a different machine.
- A public Bot share link copies config, not your computer or logins.

## Implication for later team design

Do not treat “one Bot per role” as isolation for Simplify, ATS, or
other logins. Sign out, remove files, or do not put a login on the
shared computer if another Bot should not see it.

Deleting a Bot does not wipe shared files or browser sessions.
