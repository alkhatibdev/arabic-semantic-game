# web: Next.js frontend

The playable game: RTL Arabic, light and dark, no state library. See the
[root README](../README.md) for the full project.

## Run it

```bash
npm install
cp .env.example .env.local    # NEXT_PUBLIC_API_URL defaults to localhost:8000
npm run dev
```

The backend must be running. See [`../api`](../api/README.md).

## Checks

```bash
npm run lint
npm run typecheck
npm run format
npm run build
```

## Layout

```
app/                    App Router pages, layout, global CSS
├── page.tsx            today's game
└── game/[date]/        archive game by date
components/             GameBoard owns game state; modals share Modal.tsx
lib/
├── api.ts              the only place that talks to the backend
├── session.ts          anonymous UUID in localStorage
├── theme.ts            theme context
└── utils.ts            scoring colours, UTC date helpers, share text
types/                  API response shapes
public/                 favicon, OG image, manifest
```

## Notes

- **Dates are UTC.** Use `getTodayDateUTC()` and `shiftDateUTC()` from
  `lib/utils.ts`; a local-time round-trip shifts the challenge by a day for
  players west of UTC.
- **Tailwind v4 is configured from CSS**, in `app/globals.css`. There is no
  `tailwind.config.ts`.
- `NEXT_PUBLIC_*` values are inlined at build time. Changing one means
  rebuilding, not restarting.
