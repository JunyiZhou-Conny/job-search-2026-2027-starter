# Computer-use leftover prompt (copy this)

**Audience:** the parent Cloud Agent about to spawn `computerUse`.
**Decided:** 2026-08-24 after Charta. Junyi: fire-and-forget. Do not verify.

The clicker only sees pixels and fake mouse/keyboard. It cannot read the
DOM value of a textarea. If you ask it to prove the paste, it will
Ctrl+F, fight autosuggest, and scroll. That is the token burn.

You cannot inject a custom system prompt into the Computer Use built-in.
You **can** send this user prompt and nothing else.

## Parent steps

1. One `Task` with `subagent_type=computerUse`.
2. Prompt = the template below, with tab / URL / text filled in.
3. Do not add "verify", "confirm", "search for", or "scroll to the end".
4. Do not resume the same agent unless Junyi asks, or the first call
   never reached the tab.
5. Do not start a screen recording unless Junyi asked for a demo.

## Template (copy)

```text
Same Chrome. Do not Submit. Do not Run Autofill Again. Do not click
Generate with AI. Do not change any other field.

1. Open the tab: <COMPANY> — <ROLE>
   URL contains: <URL_SUBSTRING>
2. Click the box: <FIELD LABEL>
3. Ctrl+A. Paste the text between the markers once. Do not type it
   key by key. If an autosuggest dropdown opens, click the textarea
   once and paste anyway. Do not press Escape in a loop. Do not
   click away to "clean" the dropdown.
4. Click once outside the box.
5. One screenshot of the page. Stop.

Do not Ctrl+F. Do not Ctrl+End. Do not press Down to read the
textarea. Do not hunt for phrases. A cropped textarea is normal.
Do not start a second pass.

-----BEGIN TEXT-----
<ACCEPTED DRAFT, EXACT>
-----END TEXT-----
```

## If the first pass fails

- Tab not found, or paste never happened → one retry with the same
  template. Still no verify steps.
- Textarea looks empty later → tell Junyi. He pastes, or he asks for
  one more paste. Do not Autofill Again.
- Dropdown / "thegoal" / 0/0 find-in-page → ignore. Not a retry reason.

## Later (not this week)

A DOM or Playwright fill would skip vision entirely. That is a
separate helper. Do not build it in a leftover-typing pass.
