# Demo Capture Guide

The strongest portfolio artifact for this project is a short visual demonstration of the complete physical flow.

## Recommended GIF

Target: **6-10 seconds**, silent, loopable, under roughly 10 MB.

Capture one continuous sequence:

1. package approaches the camera;
2. QR code is detected;
3. package continues on the conveyor;
4. servo routes the package;
5. dashboard metric/history updates.

Suggested output path:

```text
docs/media/conveyor-demo.gif
```

Once the GIF exists, place it near the top of the root README.

## Recommended full video

Target: **30-60 seconds**.

Show:

1. physical conveyor overview;
2. QR payload briefly;
3. camera detection;
4. API request/log;
5. Arduino/servo action;
6. dashboard result;
7. one valid and one invalid package.

For a large MP4, prefer a GitHub Release asset or another video host instead of committing the raw video to Git history.

## Framing

Use landscape video when possible. Keep the camera close enough that the conveyor movement and servo action are obvious. Avoid showing personal documents, private screens, Wi-Fi credentials, serial numbers or unrelated background information.

## Suggested narration

> A camera reads the package QR code and sends the payload to a FastAPI service. The API validates the category, records the event in SQLite and sends a versioned JSON command over USB serial. The Arduino then controls the conveyor routing servo and acknowledges the command. The Next.js dashboard reads the processing metrics from the same API.
