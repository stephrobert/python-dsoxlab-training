# Challenge: the pipeline's security gate

5 tasks, 100 points, 40 minutes.

The project is in `challenge/work`. Everything happens in
`.github/workflows/`, which you create. The tests play your workflow with act
and read what it produces; they do not read your commands.

### Task 1: a clean report lets the change through (20 pts)

On a report with no vulnerability, `act push` plays a single green job,
where the tool's tests pass and the tool summarises `rapports/trivy.json`.

### Task 2: a CRITICAL stops the pipeline (20 pts)

On the shipped report, the job fails on the threshold: the tool writes its
`FAILED: ...` line.

### Task 3: the threshold is CRITICAL, not lower (20 pts)

A report carrying only HIGH and MEDIUM lets the change through.

### Task 4: a broken tool decides nothing (20 pts)

With a broken tool, the job fails on its tests, and the threshold is not
applied.

### Task 5: pull requests go through the gate, with minimal permissions (20 pts)

`act pull_request` plays the same job, green on a clean report. The workflow
declares `permissions: contents: read`, and every action is pinned to the
full SHA of its commit.
