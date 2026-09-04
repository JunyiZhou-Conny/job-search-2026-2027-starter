# Computer-use token sinks (2026-08-24 retrospective)

Moved out of `knowledge/form_strategy.yaml` on 2026-09-03 because it is a retrospective, not a form rule. Kept verbatim as YAML.

```yaml
computer_use_token_sinks:
  decided: "2026-08-24"
  documented_with_a_rule:
    leftover_verify_loops:
      what: "Parent resumes computer-use to Ctrl+F / scroll / prove a paste"
      solution: "leftover_typing_one_pass + docs/automation/COMPUTER_USE_PROMPT.md"
    autofill_again:
      what: "Run Autofill Again after corrections"
      solution: "do_not_run_autofill_again"
    nested_task_cloud_child:
      what: "Task environment=cloud child has no computerUse"
      solution: "Dashboard Cloud Agent. First isolation child was not_run."
    generate_with_ai:
      what: "Simplify Generate with AI on leftover essays"
      solution: "Never click. written_responses.never_click"
  documented_no_helper_yet:
    vision_full_apply:
      what: >
        Even a clean Autofill+Submit pass is expensive. The clicker
        screenshots after almost every move (20–30 stills per short
        Ashby form). There is no DOM / Playwright fill this week.
      see: "docs/automation/COMPUTER_USE_PROMPT.md Later (not this week)"
    parent_screenshot_audit:
      what: >
        Parent re-reads many /tmp/computer-use/*.webp after the clicker
        already reported Success. Needed for Submit-truth experiments.
        Waste for leftover paste. leftover_typing_one_pass already
        says do not re-read many screenshots as a UI test.
    screen_record_plus_review:
      what: >
        Cloud walkthrough rules want a demo video. leftover rule says
        do not record unless Junyi asked. videoReview also failed on a
        15MB recording. Do not start RecordScreen for leftover paste.
        For Submit experiments, one short recording is enough; do not
        also spawn videoReview on a huge file.
```
