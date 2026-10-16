# Profile animations

`generate_animations.py` uses Python 3's standard library. It generates a deterministic digital-rain header and a contribution arcade, plus static versions and a dated data snapshot. SVGs have no JavaScript, external fonts, or external resources.

The Actions workflow queries GitHub's GraphQL contribution calendar for WallfacerX with the repository's built-in `GITHUB_TOKEN`. It runs at 00:37 and 12:37 UTC and supports manual dispatch. GitHub schedules can be delayed. The existing language refresh remains at 00:17 and 12:17 UTC. No PAT or third-party animation service is needed. The sole action is GitHub's official checkout, pinned to the reviewed v4.2.2 commit.

Every square is a real calendar date. Its color uses GitHub's activity quartile, and its SVG title includes the actual count. The character sweeps consecutive columns, alternately down and up, consuming only dates with contributions. Empty days remain empty. The grid restores at the end of the loop. This image does not alter the native profile contribution grid. The token's view of contributions may differ from the owner's signed-in view of private activity.

Both SVGs respect `prefers-reduced-motion` internally. README picture sources also select dedicated static SVGs when supported. Explicit static links remain available. Without CSS animation, the header and complete contribution grid remain useful still images.

Run `GH_TOKEN=... python3 scripts/generate_animations.py` to regenerate. For local previews without credentials, save the official `https://github.com/users/WallfacerX/contributions` HTML and use `--public-html path/to/calendar.html`. Both input paths validate consecutive dates and nonnegative counts before replacing assets. API failures fail the workflow and preserve the last good images.
