# 求职操作系统 / Job Search OS

这个仓库是求职的策略层和记忆层。它不是第二个 Simplify，也不是招聘网站。

Simplify 记你投了谁。这个仓库记为什么投、用哪份简历、授权怎么答、下一步做什么。Polar 是装在你 Mac 上的生产执行器。它按小时发现岗位，把队列写进 Google Sheet，并在雇主网站上填表。Cursor 负责改这个仓库、编译 Polar 运行时，以及在 Polar 还没稳的时候做影子发现。

生产还在变。若本文与 [`docs/automation/POLAR.md`](docs/automation/POLAR.md) 冲突，以 Polar 文为准。若与 [`knowledge/polar_operator.yaml`](knowledge/polar_operator.yaml) 冲突，以 YAML 为准。要粘贴的 Polar 提示词以 `python3 scripts/print_polar_bootstrap.py` 当场打出来的文本为准。

[English version](#english)

## 中文

### 给 agent 的说明

把下面整段交给你的 Cursor agent。人类先完成「只有你能做的账号」和私人 fork。

```text
你在帮人类配置一份个人求职操作系统。先读 README.md 的中文或英文，整篇按顺序做。
身份访谈问题在 docs/collaborators/SETUP.md 第 6 节。
不要编造技能、日期、成绩、签证或申请结果。不知道就写 unknown。
不要提交申请。不要代发邮件或 LinkedIn。
不要把密码、验证码、cookie 写进聊天或 git。
origin 若仍是 JunyiZhou-Conny/job-search-2026-2027-starter，立刻停下，让人类先 fork。
Polar 提示词里的 GitHub 地址必须是这个人的 fork，不能是模板仓库。
未改信任地址之前，不要让人类把模板里的 Polar 提示词贴进 Polar。
不要打开指向上游的身份重置。
不要把个人身份文件、简历、账本或 secrets 开到上游 PR。
```

本地也可以跑 `/collaborator-setup`。更短的粘贴稿在 [`docs/collaborators/AGENT_KICKOFF.md`](docs/collaborators/AGENT_KICKOFF.md)。

### 这套系统在干什么

四层不要混。

| 层 | 谁拥有 | 记什么 |
|---|---|---|
| 发现 | Polar 在你的 Mac 上读已登录的 Jobright | 现在有哪些岗位 |
| 运行时队列 | 你的 Google Sheet | Polar 每小时的 checkpoint |
| 申请账本 | 你的 Simplify | 公司、岗位、链接、投递日期、基础状态 |
| 策略和记忆 | 你的 GitHub fork | 简历版本、赛道、授权答案、人脉、下一步 |

GitHub 不能改 Polar 本机里已经存好的 Workflow。改完提示词源文件后，要重新打印并粘贴。Cloud Agent 看不到你笔记本上的登录态。

Polar 目前只支持 macOS。不要假设有 Windows 版。依据是 Polar 自己的产品说明，见 [`docs/automation/POLAR.md`](docs/automation/POLAR.md)。

### 先选模式

| 模式 | 做什么 | 不要做什么 |
|---|---|---|
| A. 自己求职 | 私人 fork，换成自己的身份，自己的 Polar、Sheet、Simplify、Cursor | 不要沿用 Junyi 的简历、账本或 Polar 信任地址 |
| B. 只改引擎 | 修脚本或文档，开上游 PR | 不要跑身份重置 |
| C. 帮别人操作 | 看 PR、改引擎 | 不要登录对方的 Simplify，不要代点提交 |

没说清楚时，按「我想用这套系统投简历」处理，也就是模式 A。

### 装完后你应该看到什么

- `origin` 是你的 fork。`upstream` 是模板仓库。
- `config/profile.yaml` 里是你的名字和日期，没有 `REPLACE_ME`。
- Polar 信任地址指向你的 fork，不是 `JunyiZhou-Conny/job-search-2026-2027-starter`。
- Polar 能用 `google_sheets` 写你的 Sheet。
- 申请邮箱在 Polar 本地档案里。学校邮箱是另一套，只有表格明确要学校邮箱时才用。
- Cursor 连上了你的 fork。
- 你跑过一次 `polar-scheduler-heartbeat`。屏幕锁着、Mac 开着时，Sheet 的 `heartbeat` 页多了一行。
- 你还没有向雇主提交任何申请。

### 1. 只有你能做的账号

Agent 列清单，然后等。不要让 agent 在聊天里要密码。

1. GitHub 账号。
2. 付费 Cursor。Hobby 跑不了 Cloud Agent。
3. 一个 Google 账号。它要能开 Google Sheet，也要能收验证码。常用做法是一个 Gmail。
4. 申请邮箱。这是 ATS、Simplify、简历抬头、密码重置用的默认邮箱。推荐单独的 Gmail。不要用学校邮箱当默认申请邮箱。
5. 学校邮箱，如果你有。只在表格写明学校、大学或机构邮箱时使用。放在 Polar 本地档案，不要写进 git。
6. Polar。在 Mac 上打开 [polarbrowser.com](https://polarbrowser.com)，按 Polar 当前页面下载。本仓库不拥有 Polar 的安装界面。
7. [Simplify](https://simplify.jobs) 账号，必须是你自己的。
8. Jobright 账号。Polar 小时发现依赖已登录的 Jobright，并点击 **Original Job Post**。不要点 Jobright 的 **APPLY WITH AUTOFILL**。

Google 账号、申请邮箱、学校邮箱可以不是同一个地址。申请邮箱和学校邮箱必须分开记。简历解析器如果把学校邮箱填进普通联系栏，提交前改回申请邮箱。

### 2. 建立私人 fork

1. 打开 `https://github.com/JunyiZhou-Conny/job-search-2026-2027-starter`。
2. Fork 成**私有**仓库。模板里有真实简历和账本。
3. 克隆你的 fork，并加上 upstream。

```bash
git clone git@github.com:<YOU>/job-search-2026-2027-starter.git
cd job-search-2026-2027-starter
git remote add upstream git@github.com:JunyiZhou-Conny/job-search-2026-2027-starter.git
git remote -v
```

`origin` 必须是你的 GitHub 用户或组织。若 `origin` 仍是模板仓库，停下。

4. 在 [Cursor Integrations](https://cursor.com/dashboard/integrations) 连接 GitHub。给这个 fork 读写权限。
5. 用 Cursor 打开这个克隆，或在 [cursor.com/agents](https://cursor.com/agents) 里把仓库选成你的 fork。

### 3. 重置模板身份

在你的 fork 上先空跑，再写入。

```bash
python3 scripts/init_personal_copy.py
python3 scripts/init_personal_copy.py --i-am-on-a-personal-fork --write
```

脚本会把身份文件换成模板，并把个人账本收成只有表头。它不会改 Polar 的信任地址。下一步单独做。

### 4. 填写你的事实

Agent 问 [`docs/collaborators/SETUP.md`](docs/collaborators/SETUP.md) 第 6 节的问题。人类回答。agent 只写已确认的事实。其余写 `unknown`。不要从 Junyi 的文件里猜。

写这些文件。

| 文件 | 写完长什么样 |
|---|---|
| `config/profile.yaml` | 你的名字、链接、日期、赛道、是否接受远程 |
| `knowledge/work_authorization.yaml` | 只写不敏感的授权答案 |
| `knowledge/evidence_bank.yaml` | 你能在面试里守住的项目。`verified` 和 `resume_eligible` 只有为真时才标真 |
| `knowledge/discovery_triage_rules.yaml` 的 `profile_anchors` | 日期和远程规则是你的。`guide_rules` 不要改 |
| `docs/automation/DAILY_JOB_DISCOVERY.md` 的候选人段 | 只改 fork 本地。不要把这段开到上游 |
| `data/outreach_templates.csv` | 占位符换成你的学校和毕业信息 |
| `resumes/base/` | 你的简历。不要登记 `JZ_resume` 当自己的 |

不要把护照、SEVIS、SSN、EAD 扫描件或 ATS 密码放进仓库。

### 5. 准备 Google 和两套邮箱

1. 用第 1 步那个 Google 账号登录 Polar。后面的 Sheet、Gmail 验证码、Polar 发信都走这个浏览器登录态。
2. 在 Google Drive 新建一个空白表格。名字自定，例如 `Polar Jobs`。不要复制别人的生产表。
3. 在 Polar 里打开这个表格，并接上 Polar 会话里的 `google_sheets` 能力。具体按钮以 Polar 当前界面为准。本仓库不拥有那些屏幕。不要去配 [Polar Analytics](https://www.polaranalytics.com)。那是另一个产品。
4. 把申请邮箱写进 Polar 本地档案、Simplify，以及磁盘上的 `secrets/.env`。

```bash
cp secrets/.env.example secrets/.env
```

申请邮箱对应 `RESUME_EMAIL` 或 `SIMPLIFY_EMAIL`。不要设 `HARVARD_EMAIL` 当简历联系邮箱。不要把 `.env` 提交进 git。

5. 学校邮箱只放在 Polar 本地档案。不要写进 Sheet、学习报告或 git。
6. 电话和街道地址也只放 Polar 本地档案。编译进 `POLAR_RUNTIME` 的文件不会带这些值。这样是对的。

`daily-job-summary` 还需要 Polar 的 `email` 能力。用同一个 Google 登录态收那封每日摘要。摘要主题形如 `Polar daily job summary YYYY-MM-DD`。

### 6. 把 Polar 的信任地址改到你的 fork

模板编译出的 Polar 提示词指向 `JunyiZhou-Conny/job-search-2026-2027-starter`。你若原样粘贴，Polar 会去读 Junyi 的身份和日期。

在 fork 上做这一步。不要把这次改动开到上游。

```bash
python3 scripts/set_polar_trusted_repo.py <YOU>/job-search-2026-2027-starter
python3 scripts/set_polar_trusted_repo.py <YOU>/job-search-2026-2027-starter --write --rebuild
git add scripts/polar_policy.py generated/polar
git commit -m "chore(polar): point Polar trust URLs at this fork"
git push origin main
```

Polar 只从 `main` 上的 raw URL 拉配置。没推到 `main` 之前，不要贴提示词。

然后打印一条，确认仓库名是你的。

```bash
python3 scripts/print_polar_bootstrap.py apply-ready-jobs
```

你应该看到 `Trusted repository: <YOU>/job-search-2026-2027-starter`。若仍是 `JunyiZhou-Conny`，停下。

### 7. 安装 Polar 并贴上提示词

Polar 的产品界面会变。按 Polar 当前 UI 做。缺连接器就停，并记下 `CAPABILITY_MISSING`。不要发明 Polar 没有的按钮。

1. 打开 Polar。用一个**具名**本地浏览器配置。后面所有生产 Workflow 都用这一个。
2. 在这个配置里登录 Google、Gmail、Jobright、Simplify。
3. 在 Polar 里安装 Simplify Copilot。Polar 是 Chromium 分支。Copilot 必须出现在雇主申请页上。只登录 [simplify.jobs](https://simplify.jobs) 不够。
4. 若 Polar 还有本地 `SKILL.md`，并且它仍写着去 GitHub 拉 workflow 再执行，用 [`docs/automation/POLAR_SKILL_BOOTSTRAP.md`](docs/automation/POLAR_SKILL_BOOTSTRAP.md) 里的那段替换。不要把 `POLAR_RUNTIME.md` 整份贴进 skill。
5. 按 [`docs/automation/POLAR_WORKFLOWS.md`](docs/automation/POLAR_WORKFLOWS.md) 为每个 Workflow 建一条**已保存**的 Polar Workflow。提示词用打印出来的文本，不要手抄模板里的 Junyi 地址。

先建并跑一次手动的 `polar-sheet-migration`。它会加上这些页和表头。已有行要保留。

- `queue`
- `writing_log`
- `heartbeat`
- `run_log`
- `incident_log`
- `control`
- `learning_reports`

字段以 [`docs/automation/POLAR_QUEUE.md`](docs/automation/POLAR_QUEUE.md) 和 `generated/polar/*_schema.csv` 为准。缺页是迁移问题，不是 `CAPABILITY_MISSING`。缺的是 `google_sheets` 这个连接器才算 `CAPABILITY_MISSING`。

然后建这些定时任务。时刻是 America/New_York。

| Workflow | 时间 | 作用 |
|---|---|---|
| `discover-jobs-hourly` | 每小时 00 分 | 只发现和写队列。不点申请。 |
| `apply-ready-jobs` | 每小时 20 分 | 执行。先不要通宵自动提交。 |
| `polar-scheduler-heartbeat` | 每小时 05 分，直到你记下结果 | 打开无害页面，写一行 heartbeat。 |
| `daily-job-summary` | 每天 21:30 | 读 Sheet，发一封邮件。不点申请。 |
| `production-learning-daily` | 每天 22:00 | 写一份脱敏学习报告。 |

`polar-github-write-canary`、`chatgpt-production-review`、`cursor-production-maintenance` 先留着手动。写路径还没证明。

6. 在本机建 `/home/polar/PREFERENCES.md`。这是本地收件箱，不是第二套策略库。
7. 让 Mac 开着、在线。锁屏可以。睡眠不行，除非你已经用 heartbeat 证明 Polar 在锁屏时仍能写 Sheet。

GitHub 改了 bootstrap 之后，每一条已保存的 Polar Workflow 都要重新贴一次。GitHub 改不了 Polar 本机文件。

### 8. 配置 Cursor

Cursor 是工程师，不是生产投递员。

1. 打开 [Cloud Agents Environments](https://cursor.com/dashboard/cloud-agents#environments)。把**你的 fork** 接上去。
2. 密钥放在 Cloud Agents 的 Secrets，或本地 `secrets/.env`。不要把密码贴进对话。
3. 可选。在 [cursor.com/automations](https://cursor.com/automations) 建私有的 Daily Job Discovery。仓库选你的 fork。Agent Instructions 只贴 [`docs/automation/UI_POINTER.md`](docs/automation/UI_POINTER.md) 里的那一块。不要把 Polar Workflow 提示词贴进 Cursor Automation。
4. 前 48 小时不要关 Cloud 发现。Polar 小时发现是生产候选。Cloud 早间和晚间发现仍是影子和退路。对照表在 [`docs/automation/POLAR_SHADOW.md`](docs/automation/POLAR_SHADOW.md)。
5. 仓库里的 `.cursor/rules/` 和 `.cursor/commands/` 会跟着 clone 来。它们不是定时器。

### 9. 验收

```bash
git remote -v
python3 scripts/init_personal_copy.py --check
python3 scripts/validate_data.py
python3 scripts/print_polar_bootstrap.py apply-ready-jobs
```

`--check` 失败时，按打印出来的文件改。不要靠删共享政策文字来「通过」。

再看这些人类界面。

| 检查 | 你应该看到 |
|---|---|
| Polar 打开你的 Sheet | 七个页都在，表头和 `POLAR_QUEUE.md` 一致 |
| Polar 申请邮箱 | 默认联系邮箱是申请邮箱，不是学校邮箱 |
| Polar Copilot | 打开任意雇主申请页，能看到 Simplify Copilot |
| heartbeat | 锁屏跑一次后，`heartbeat` 页多了一行 |
| Cursor | Cloud Agent 能推到你的 fork |

### 10. 先试跑，不要提交

先跑 `polar-sheet-migration`，再跑一次 `polar-scheduler-heartbeat`。不要先跑 `apply-ready-jobs` 通宵提交。

heartbeat 还没在锁屏下写成功之前，不要提高通宵提交的信心。提交开关在 [`docs/policy/SUBMIT_ROLLOUT.md`](docs/policy/SUBMIT_ROLLOUT.md)。

本地队列仍可用来看发现结果。

```bash
python3 scripts/serve_apply_queue.py --date $(date +%F)
```

打开 `http://127.0.0.1:8765/`。**Applied** 只写本地账本。它不会替你点雇主网站上的 Submit。

### 现在还没做稳的事

这些在 [`docs/automation/POLAR.md`](docs/automation/POLAR.md) 里标成未证明或仍在迁移。

- Polar 无人值守地从 GitHub raw URL 拉 `POLAR_RUNTIME`，仍是推断。
- 锁屏时 Polar 写 Google Sheet，要等 heartbeat 证明。
- Polar 小时发现是否赶上 Cloud 发现，要等 48 小时对照。
- 不是每个 Original Job Post 都是雇主 ATS。
- 简历一页纸的生产挂载还在 Resume Stack BUILD。空简历控件时不要上传两页的 master PDF。标 `REVIEW_READY`，blocker 写 `missing_production_resume`。

政策、配额、提示词还会改。改完后重新编译，推到 `main`，再重新粘贴 Polar Workflow。

### 装好之后每天做什么

**Polar。** 小时发现写 Sheet。小时执行处理 READY 行。晚上发摘要。

**你。** 看每日邮件。处理 `REVIEW_READY` 和 `SUBMISSION_UNKNOWN`。不要盲着重提。

**Cursor。** 改规则、证据库、简历。编译 `POLAR_RUNTIME`。在结果核对后，把 Sheet 里已证实的投递写回 `data/applications.csv`。

**每周。** 从 Simplify 导出 CSV，放到 `data/imports/simplify/YYYY-MM-DD.csv`，然后导入。

```bash
python3 scripts/jobsearch.py import-simplify --file data/imports/simplify/YYYY-MM-DD.csv
python3 scripts/dedupe_applications.py
python3 scripts/validate_data.py
python3 scripts/jobsearch.py dashboard
```

### 硬规则

1. 不要编造。
2. 未经本人当场确认，不要提交或外发。
3. 不要把密钥提交进 git。
4. 赞助不明或公司不赞助，不是硬性淘汰。
5. `label_source=manual` 不能被自动覆盖。
6. 文件胜过聊天记忆。
7. 不要把模板作者的身份当成你的。
8. 缺连接器就停。缺 Copilot 就停申请轮次，不要改成手点。
9. 非美国工作地点直接跳过。

更细的引擎说明在 [`docs/collaborators/SETUP.md`](docs/collaborators/SETUP.md)。上游 PR 规则在 [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md)。

## English

### For the agent

Give your Cursor agent this block after the human finishes the accounts they must create and the private fork.

```text
You are setting up a personal copy of this job-search OS. Read README.md in Chinese or English and follow it in order.
Identity interview questions live in docs/collaborators/SETUP.md section 6.
Never invent skills, dates, grades, visa facts, or application outcomes. Write unknown when the human does not know.
Do not submit applications. Do not send email or LinkedIn.
Do not put passwords, OTP codes, or cookies in chat or git.
If origin is still JunyiZhou-Conny/job-search-2026-2027-starter, stop and tell the human to fork first.
Polar prompt GitHub URLs must name this person's fork, not the template repo.
Do not let the human paste template Polar prompts until those trust URLs are rewritten.
Do not run the identity reset on upstream.
Do not open an upstream PR that contains identity files, resumes, ledgers, or secrets.
```

You can also run `/collaborator-setup`. The shorter paste file is [`docs/collaborators/AGENT_KICKOFF.md`](docs/collaborators/AGENT_KICKOFF.md).

### What this system is

Keep the four layers apart.

| Layer | Who owns it | What it stores |
|---|---|---|
| Discovery | Polar on your Mac, using logged-in Jobright | Which roles exist |
| Runtime queue | Your Google Sheet | Polar's hourly checkpoint |
| Application ledger | Your Simplify | Company, role, URL, date applied, base status |
| Strategy and memory | Your GitHub fork | Resume version, lane, auth answers, networking, next action |

GitHub cannot edit a Polar Workflow already saved on the Mac. After a prompt source changes, print it again and paste it again. A Cloud Agent cannot see laptop logins.

Polar is macOS only for now. Do not assume a Windows Polar exists. That limit comes from Polar's own product note, cited in [`docs/automation/POLAR.md`](docs/automation/POLAR.md).

### Pick a mode

| Mode | Do this | Do not do this |
|---|---|---|
| A. Your own search | Private fork, your identity, your Polar, Sheet, Simplify, and Cursor | Do not keep Junyi's resume, ledger, or Polar trust URLs |
| B. Engine only | Fix scripts or docs, open an upstream PR | Do not run the identity reset |
| C. Help someone else | Review PRs, improve the engine | Do not log into their Simplify or click Submit for them |

If they said they want this system for their own applications, that is Mode A.

### What done looks like

- `origin` is your fork. `upstream` is the template.
- `config/profile.yaml` has your name and dates, with no `REPLACE_ME`.
- Polar trust URLs point at your fork, not `JunyiZhou-Conny/job-search-2026-2027-starter`.
- Polar can write your Sheet through `google_sheets`.
- The application mailbox lives in the local Polar profile. The academic mailbox is separate and is used only when a form asks for a school, university, or institutional email.
- Cursor is connected to your fork.
- You have run `polar-scheduler-heartbeat` once. With the screen locked and the Mac awake, the Sheet `heartbeat` tab gained a row.
- You have not submitted any employer application.

### 1. Accounts only you can create

The agent lists these and waits. It must not ask for passwords in chat.

1. A GitHub account.
2. Paid Cursor. Hobby cannot run Cloud Agents.
3. A Google account that can own a Google Sheet and receive OTP mail. A Gmail account is the usual choice.
4. An application mailbox. This is the default address for ATS forms, Simplify, the resume header, and password reset. A dedicated Gmail is the usual choice. Do not use a school address as the default application mailbox.
5. A school mailbox, if you have one. Use it only when the form asks for a school, university, or institutional email. Keep it in the local Polar profile. Do not commit it.
6. Polar. On a Mac, open [polarbrowser.com](https://polarbrowser.com) and follow Polar's current download page. This repo does not own Polar's installer screens.
7. Your own [Simplify](https://simplify.jobs) account.
8. A Jobright account. Polar hourly discovery needs a logged-in Jobright session and the **Original Job Post** control. Do not click Jobright **APPLY WITH AUTOFILL**.

The Google account, the application mailbox, and the school mailbox may be different addresses. Keep the application mailbox and the school mailbox as two facts. If a resume parser fills the school address into a normal contact field, correct it before Submit.

### 2. Create a private fork

1. Open `https://github.com/JunyiZhou-Conny/job-search-2026-2027-starter`.
2. Fork it as a **private** repository. The template contains a real resume and ledger.
3. Clone your fork and add upstream.

```bash
git clone git@github.com:<YOU>/job-search-2026-2027-starter.git
cd job-search-2026-2027-starter
git remote add upstream git@github.com:JunyiZhou-Conny/job-search-2026-2027-starter.git
git remote -v
```

`origin` must be your GitHub user or org. If `origin` is still the template, stop.

4. Connect GitHub at [Cursor Integrations](https://cursor.com/dashboard/integrations). Grant read-write on this fork.
5. Open the clone in Cursor, or pick this fork at [cursor.com/agents](https://cursor.com/agents).

### 3. Reset the template identity

Dry-run first, then write, and only on your fork.

```bash
python3 scripts/init_personal_copy.py
python3 scripts/init_personal_copy.py --i-am-on-a-personal-fork --write
```

The script replaces identity files with blanks and keeps personal ledgers as headers only. It does not retarget Polar trust URLs. Do that in the next Polar step.

### 4. Fill your facts

The agent asks the questions in [`docs/collaborators/SETUP.md`](docs/collaborators/SETUP.md) section 6. The human answers. The agent writes confirmed facts only. Everything else is `unknown`. Do not infer from Junyi's files.

Write these files.

| File | Done looks like |
|---|---|
| `config/profile.yaml` | Your name, links, dates, tracks, remote rule |
| `knowledge/work_authorization.yaml` | Non-sensitive auth answers only |
| `knowledge/evidence_bank.yaml` | Projects you can defend. Mark `verified` and `resume_eligible` only when those are true |
| `profile_anchors` in `knowledge/discovery_triage_rules.yaml` | Your dates and remote rule. Leave `guide_rules` shared |
| Candidate block in `docs/automation/DAILY_JOB_DISCOVERY.md` | Fork-local only. Do not PR this rewrite |
| `data/outreach_templates.csv` | Your school and graduation placeholders |
| `resumes/base/` | Your resume. Do not register `JZ_resume` as yours |

Do not put passport, SEVIS, SSN, EAD scans, or ATS passwords in the repo.

### 5. Set up Google and the two mailboxes

1. Sign into Polar with the Google account from step 1. The Sheet, Gmail OTP, and Polar outbound mail use this browser session.
2. Create a blank Google Sheet in that account. Name it something you will recognize, such as `Polar Jobs`. Do not copy someone else's production Sheet.
3. Open that Sheet in Polar and attach Polar's `google_sheets` session capability. Use Polar's current connector UI. This repo does not own those screens. Do not set up [Polar Analytics](https://www.polaranalytics.com). That is a different product.
4. Put the application mailbox in the local Polar profile, in Simplify, and in `secrets/.env` on disk.

```bash
cp secrets/.env.example secrets/.env
```

The application mailbox is `RESUME_EMAIL` or `SIMPLIFY_EMAIL`. Do not use `HARVARD_EMAIL` as the resume contact. Do not commit `.env`.

5. Keep the school mailbox in the local Polar profile only. Do not write it into the Sheet, a learning report, or git.
6. Keep phone and street address in the local Polar profile too. Compiled `POLAR_RUNTIME` omits those values on purpose.

`daily-job-summary` also needs Polar's `email` capability. Use the same Google session to receive that digest. The subject looks like `Polar daily job summary YYYY-MM-DD`.

### 6. Point Polar trust URLs at your fork

The template compiles Polar prompts that name `JunyiZhou-Conny/job-search-2026-2027-starter`. If you paste those prompts unchanged, Polar reads Junyi's identity and dates.

Do this on the fork. Do not send this rewrite upstream.

```bash
python3 scripts/set_polar_trusted_repo.py <YOU>/job-search-2026-2027-starter
python3 scripts/set_polar_trusted_repo.py <YOU>/job-search-2026-2027-starter --write --rebuild
git add scripts/polar_policy.py generated/polar
git commit -m "chore(polar): point Polar trust URLs at this fork"
git push origin main
```

Polar loads configuration from raw URLs on `main`. Do not paste prompts before that push.

Print one prompt and confirm the repository is yours.

```bash
python3 scripts/print_polar_bootstrap.py apply-ready-jobs
```

You should see `Trusted repository: <YOU>/job-search-2026-2027-starter`. If it still says `JunyiZhou-Conny`, stop.

### 7. Install Polar and paste the prompts

Polar's product UI changes. Follow the screens Polar shows today. If a connector is missing, stop and record `CAPABILITY_MISSING`. Do not invent a Polar control that is not there.

1. Open Polar. Use one **named** local browser profile. Every production Workflow uses that same profile.
2. Sign into Google, Gmail, Jobright, and Simplify in that profile.
3. Install Simplify Copilot in Polar. Polar is a Chromium fork. Copilot must appear on the employer application page. A login on [simplify.jobs](https://simplify.jobs) is not proof.
4. If Polar still has a local `SKILL.md` that says fetch a GitHub workflow and follow it, replace that body with the block in [`docs/automation/POLAR_SKILL_BOOTSTRAP.md`](docs/automation/POLAR_SKILL_BOOTSTRAP.md). Do not paste all of `POLAR_RUNTIME.md` into the skill.
5. Create one **saved** Polar Workflow per name in [`docs/automation/POLAR_WORKFLOWS.md`](docs/automation/POLAR_WORKFLOWS.md). Paste the printed prompt. Do not hand-copy the template URLs that name Junyi's repo.

Create and run `polar-sheet-migration` once by hand. It adds these tabs and headers. It keeps existing rows.

- `queue`
- `writing_log`
- `heartbeat`
- `run_log`
- `incident_log`
- `control`
- `learning_reports`

Fields come from [`docs/automation/POLAR_QUEUE.md`](docs/automation/POLAR_QUEUE.md) and `generated/polar/*_schema.csv`. A missing tab is a migration issue. It is `CAPABILITY_MISSING` only when the `google_sheets` connector itself is missing.

Then create these schedules. Times are America/New_York.

| Workflow | When | What it does |
|---|---|---|
| `discover-jobs-hourly` | minute 00 every hour | Discovery and queue writes only. No apply clicks. |
| `apply-ready-jobs` | minute 20 every hour | Execution. Do not leave overnight Submit on yet. |
| `polar-scheduler-heartbeat` | minute 05 every hour until you record a result | Opens a harmless page and writes one heartbeat row. |
| `daily-job-summary` | 21:30 daily | Reads the Sheet and sends one email. No apply clicks. |
| `production-learning-daily` | 22:00 daily | Writes one sanitized learning report. |

Leave `polar-github-write-canary`, `chatgpt-production-review`, and `cursor-production-maintenance` manual. The write path is not proven.

6. Create `/home/polar/PREFERENCES.md` on the Mac. That file is a local inbox. It is not a second strategy database.
7. Leave the Mac powered on and online. A locked screen is fine. Sleep is not, until heartbeat proves Polar can write the Sheet while locked.

After GitHub changes a bootstrap, paste every saved Polar Workflow again. GitHub cannot mutate Polar-local files.

### 8. Set up Cursor

Cursor is the engineer, not the production applicant.

1. Open [Cloud Agents Environments](https://cursor.com/dashboard/cloud-agents#environments) and attach **your fork**.
2. Put secrets in the Cloud Agents Secrets tab or in local `secrets/.env`. Do not paste passwords into chat.
3. Optional. Create a private Daily Job Discovery automation at [cursor.com/automations](https://cursor.com/automations). Point it at your fork. Paste only the block in [`docs/automation/UI_POINTER.md`](docs/automation/UI_POINTER.md). Do not paste a Polar Workflow prompt into a Cursor Automation.
4. Do not disable Cloud discovery for the first 48 hours. Polar hourly discovery is the production candidate. Cloud morning and evening discovery stay as shadow and fallback. The comparison list is [`docs/automation/POLAR_SHADOW.md`](docs/automation/POLAR_SHADOW.md).
5. `.cursor/rules/` and `.cursor/commands/` arrive with the clone. They are not timers.

### 9. Verify

```bash
git remote -v
python3 scripts/init_personal_copy.py --check
python3 scripts/validate_data.py
python3 scripts/print_polar_bootstrap.py apply-ready-jobs
```

If `--check` fails, rewrite the files it names. Do not pass by deleting shared policy text.

Then check these human surfaces.

| Check | You should see |
|---|---|
| Polar opens your Sheet | All seven tabs exist. Headers match `POLAR_QUEUE.md` |
| Polar application mailbox | Default contact email is the application mailbox, not the school mailbox |
| Polar Copilot | Simplify Copilot is visible on an employer application page |
| heartbeat | After one locked-screen run, the `heartbeat` tab has a new row |
| Cursor | A Cloud Agent can push to your fork |

### 10. First smoke, no submit

Run `polar-sheet-migration`, then one `polar-scheduler-heartbeat`. Do not start overnight `apply-ready-jobs` Submit.

Do not raise overnight Submit confidence until heartbeat writes while the screen is locked. Submit gates live in [`docs/policy/SUBMIT_ROLLOUT.md`](docs/policy/SUBMIT_ROLLOUT.md).

The local apply queue can still show discovery rows.

```bash
python3 scripts/serve_apply_queue.py --date $(date +%F)
```

Open `http://127.0.0.1:8765/`. **Applied** writes the local ledger only. It does not click Submit on the employer site.

### What is still unsettled

[`docs/automation/POLAR.md`](docs/automation/POLAR.md) marks these as unproven or still in migration.

- Polar loading `POLAR_RUNTIME` from a GitHub raw URL with no human present is still an inference.
- Polar writing the Google Sheet while the screen is locked waits on the heartbeat test.
- Polar hourly discovery versus Cloud discovery waits on the 48-hour shadow.
- Not every Original Job Post is an employer ATS.
- Production one-pager attach is still in Resume Stack BUILD. If the resume widget is empty, do not upload the two-page master PDF. Mark `REVIEW_READY` with blocker `missing_production_resume`.

Policy, caps, and prompts will keep moving. After a change, recompile, push `main`, and paste the Polar Workflows again.

### Daily loop after setup

**Polar.** Hourly discovery writes the Sheet. Hourly apply handles READY rows. Evening mail sends the digest.

**You.** Read the daily mail. Handle `REVIEW_READY` and `SUBMISSION_UNKNOWN`. Do not blindly resubmit.

**Cursor.** Edit rules, the evidence bank, and resumes. Compile `POLAR_RUNTIME`. After a result is verified, reconcile Sheet rows into `data/applications.csv`.

**Weekly.** Export Simplify to `data/imports/simplify/YYYY-MM-DD.csv`, then import.

```bash
python3 scripts/jobsearch.py import-simplify --file data/imports/simplify/YYYY-MM-DD.csv
python3 scripts/dedupe_applications.py
python3 scripts/validate_data.py
python3 scripts/jobsearch.py dashboard
```

### Hard rules

1. Never invent.
2. Do not submit or send without the applicant present and confirming.
3. Do not commit secrets.
4. Sponsorship unknown or no is not hard ineligibility.
5. `label_source=manual` is not auto-overwritten.
6. Files beat chat memory.
7. Do not keep the template owner's identity as yours.
8. Stop when a connector is missing. If Copilot is missing, stop the apply run. Do not fall back to hand clicking.
9. Skip a non-US work location.

The longer identity-reset runbook is [`docs/collaborators/SETUP.md`](docs/collaborators/SETUP.md). Upstream PR rules are [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md).
