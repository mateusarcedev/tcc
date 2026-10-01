# Portfolio media

This directory is reserved for visual evidence of the real project.

Do not add stock images, generated mockups or screenshots that imply physical behavior that was not actually recorded.

## Target files

### `conveyor-demo.gif`

Primary README visual.

Recommended capture:

```text
QR detected
→ package continues on conveyor
→ servo routes package
→ dashboard updates
```

Target:

- 6–10 seconds
- silent and loopable
- landscape when possible
- preferably under 10 MB

Once this file exists, add it near the top of the root README.

### `dashboard.png`

Optional static screenshot of the running Next.js dashboard after demo data has been processed.

Recommended content:

- summary metrics
- charts
- recent package table
- no browser tabs, credentials or unrelated desktop content

### Full video

For a 30–60 second MP4, prefer a GitHub Release asset or external video host instead of committing a large binary to repository history.

## Accuracy rule

Visual assets should document the real system. If a component is being simulated, label it as simulation rather than presenting it as a physical run.
