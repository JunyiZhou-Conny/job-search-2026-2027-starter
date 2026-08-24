# LinkedIn draft — S-Seg-RLVR

Junyi 2026-08-24 asked for a LinkedIn experience line he can paste.
**Do not post from this repo.** He updates LinkedIn himself.

Facts from the public repo only. No invented metrics. No paper acceptance.

## Experience card

| Field | Paste |
|---|---|
| Title | Graduate Researcher |
| Company | Harvard T.H. Chan School of Public Health |
| Location | Boston, Massachusetts, United States |
| Type | Research |
| Start | August 2026 |
| End | Present |
| Headline under title | Structure-Verified RLVR for Label-Efficient Pathology Instance Segmentation (S-Seg-RLVR) |

## About / description (paste)

```text
I am building S-Seg-RLVR, my Health Data Science capstone with mentor Alexander Chowdhury. Pathology instance segmentation usually trains on Dice and IoU. Those overlap scores miss merged nuclei that wreck the count a pathologist actually uses. I am treating instance count, separation, and topology as verifiable rewards for GRPO so the model can learn from point and count labels plus a small fully labeled anchor set.

The public repo already has the proposal, a 30 paper literature library, a 16 week roadmap, and typed reward interfaces. Training on public nuclei and gland sets, and live GRPO runs, are next. Target venue is MICCAI 2027.

https://github.com/JunyiZhou-Conny/Structure-Verified-RLVR-for-Label-Efficient-Pathology-Instance-Segmentation
```

## Skills to add on the card (optional)

Reinforcement Learning, Computer Vision, Medical Image Analysis, PyTorch, Research

Do not add "MICCAI author" or a Dice / PQ number until those exist.

## Interview ceiling

If someone clicks the repo: reward functions still raise NotImplementedError. Datasets are not downloaded. Say the method and the repo are real. Do not say a model is trained.
