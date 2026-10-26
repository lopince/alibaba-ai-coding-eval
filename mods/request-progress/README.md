# Request Progress

A band above the prompt with one row for every request you send in a session.

Each row keeps its bar — one cell per activity, coloured by kind and scrolling
once full — then the prompt title, state and elapsed time. The request still
working grows a tree beneath it, one branch per model step:

```
* running  Fix the login bug        █▓█▓█░░··  0:24
           ├─ step 1
           │  ├─ thinking
           │  ├─ Bash · npm test          ✓ 3.2s
           │  └─ Read · app.ts            ✓ 0.4s
           └─ step 2
              └─ thinking                 ▸
```

Leaves are the turn's real work, coloured by kind (amber thinking, blue
writing, orange bash, cyan tools, red asks); a finished tool carries `✓` and
its duration, a failed one `✗`, and the live one blinks `▸`. States:

- `* running` — the turn is working.
- `✓ done` — the turn answered; the row collapses to one line.
- `! needs you` — a permission ask or a question tool is waiting on you.
- `✗ failed` — the turn ended on an error, a refusal, or an interrupt.

The tree keeps the newest six activities and the newest two requests; older
rows roll into `+N earlier` in the summary line.

A summary line counts the states, and `/requests hide`, `/requests show` and
`/requests clear` control the band. It draws above the prompt, next to the
other bands; nothing is sent anywhere and no tool is called.

## Install

Installed at user scope from the `local-mods` marketplace on this machine:

```
/plugin install request-progress --marketplace ~/.claude/local-mods
```

New sessions load it automatically. After editing `hooks/register.tsx`, run
`/reload-plugins` (installed plugins are read from this folder, not hot-reloaded).
