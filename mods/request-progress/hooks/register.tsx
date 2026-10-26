import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Activity, ActivityKind, RequestBoard, RequestRow, RequestStatus } from '../types'

const BOARD = atom({ plugin: 'request-progress', key: 'board' } as const, { rows: [] } as RequestBoard)
const NOW = atom({ plugin: 'request-progress', key: 'now' } as const, 0)
const HIDDEN = atom({ plugin: 'request-progress', key: 'hidden' } as const, false)

const KEEP = 20
const MAX_SHOWN = 4
const TICK_MS = 1000
// How many activities one request remembers, and how many the tree draws.
const FLOW_KEEP = 40
const TREE_NODES = 6
const TREE_ROWS = 2

const EMPTY = '#40404c'

type Look = {
  glyph: string
  label: string
  color: string
  fill: readonly [string, string]
}

const LOOK: Record<RequestStatus, Look> = {
  running: { glyph: '*', label: 'running', color: '#ff9d6b', fill: ['#ff9d6b', '#ffc9ae'] },
  done: { glyph: '✓', label: 'done', color: '#6ee7a0', fill: ['#4ade80', '#a7f3c0'] },
  'needs-you': { glyph: '!', label: 'needs you', color: '#ff6b64', fill: ['#f87171', '#fca5a5'] },
  failed: { glyph: '✗', label: 'failed', color: '#ff6b64', fill: ['#ef4444', '#f87171'] },
}

// What each kind of work looks like: one colour and one cell in the row bar.
const FLOW: Record<ActivityKind, { color: string; glyph: string }> = {
  thinking: { color: '#e5c07b', glyph: '▒' },
  writing: { color: '#61afef', glyph: '▓' },
  bash: { color: '#ff9d6b', glyph: '█' },
  tool: { color: '#56b6c2', glyph: '█' },
  ask: { color: '#ff6b64', glyph: '█' },
}

let seq = 0
// The main-loop turn now running, so a tool call or an ask finds its request.
let activeTurn = ''
// The model request the turn is on; the tools it calls belong to this step.
let currentStep = 0

const isOpen = (row: RequestRow) => row.status === 'running' || row.status === 'needs-you'

function newId(): string {
  return `${Date.now()}-${seq++}`
}

function titleOf(text: string): string {
  const line = text.replace(/\s+/g, ' ').trim()
  return line || '(empty prompt)'
}

function oneLine(text: string, width = 22): string {
  const line = text.replace(/\s+/g, ' ').trim()
  return line.length <= width ? line : `${line.slice(0, Math.max(1, width - 1))}…`
}

function cut(text: string, width: number): string {
  if (width < 1) return ''
  return text.length <= width ? text : `${text.slice(0, Math.max(1, width - 1))}…`
}

function baseName(path: string): string {
  const parts = path.split(/[\\/]/)
  return parts[parts.length - 1] || path
}

function shortTool(tool: string): string {
  const parts = tool.split('__')
  return parts.length > 2 ? parts[parts.length - 1] ?? tool : tool
}

function toolKind(tool: string): ActivityKind {
  if (tool === 'Bash' || tool === 'BashOutput') return 'bash'
  if (tool === 'AskUserQuestion') return 'ask'
  return 'tool'
}

// The tool's arguments sit beside its name on the event (`e.command` for Bash).
function toolLabel(tool: string, args: Record<string, unknown>): string {
  const text = (value: unknown) => (typeof value === 'string' ? value : '')
  const name = shortTool(tool)
  if (tool === 'Bash' || tool === 'BashOutput') {
    const command = text(args.command)
    return command ? `Bash · ${oneLine(command)}` : 'Bash'
  }
  const file = text(args.file_path) || text(args.notebook_path) || text(args.path)
  if (file) return `${name} · ${oneLine(baseName(file), 20)}`
  const pattern = text(args.pattern) || text(args.query) || text(args.url)
  if (pattern) return `${name} · ${oneLine(pattern, 20)}`
  const description = text(args.description)
  if (description) return `${name} · ${oneLine(description, 20)}`
  return name
}

function mmss(ms: number): string {
  const s = Math.max(0, Math.floor(ms / 1000))
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`
}

function duration(ms: number): string {
  if (ms < 1000) return `${Math.max(0, Math.round(ms))}ms`
  const s = ms / 1000
  return s < 10 ? `${s.toFixed(1)}s` : `${Math.round(s)}s`
}

function timeText(row: RequestRow, clock: number): string {
  if (row.status === 'done') return mmss(row.durationMs || row.endedAt - row.startedAt)
  if (row.status === 'needs-you') return 'waiting'
  if (row.status === 'failed') return 'failed'
  return mmss(clock - row.startedAt)
}

function findTarget(rows: RequestRow[], turnId: string): number {
  if (turnId) {
    const hit = rows.findIndex(row => row.turnId === turnId && isOpen(row))
    if (hit >= 0) return hit
  }
  for (let i = rows.length - 1; i >= 0; i--) {
    const row = rows[i]
    if (row && isOpen(row)) return i
  }
  return -1
}

// Changes the request its turn is on. After a reload activeTurn is empty, so
// the newest open row stands in.
async function touchOpen($: EngineInterface, change: (row: RequestRow) => RequestRow) {
  await update($, BOARD, board => {
    const rows = board.rows.slice()
    let hit = false
    for (let i = 0; i < rows.length; i++) {
      const row = rows[i]
      if (!row) continue
      if (activeTurn && row.turnId === activeTurn && isOpen(row)) {
        rows[i] = change(row)
        hit = true
      }
    }
    if (!hit) {
      const index = findTarget(rows, '')
      const row = rows[index]
      if (row) rows[index] = change(row)
    }
    return { rows }
  })
}

// Thinking and writing end when the next thing starts, or when the step stops.
function closeThoughts(flow: Activity[]): Activity[] {
  let changed = false
  const next = flow.map(activity => {
    if (activity.status !== 'active') return activity
    if (activity.kind !== 'thinking' && activity.kind !== 'writing') return activity
    changed = true
    return { ...activity, status: 'done' as const, endedAt: Date.now() }
  })
  return changed ? next : flow
}

async function addActivity($: EngineInterface, turnId: string, activity: Activity) {
  await update($, BOARD, board => {
    const rows = board.rows.slice()
    const index = findTarget(rows, turnId)
    const row = rows[index]
    if (!row) return board
    const last = row.flow[row.flow.length - 1]
    if (last && last.kind === activity.kind && last.label === activity.label && last.status === 'active') {
      return board
    }
    const flow = closeThoughts(row.flow).concat(activity).slice(-FLOW_KEEP)
    rows[index] = { ...row, flow, turnId: row.turnId || turnId }
    return { rows }
  })
}

async function finishActivity($: EngineInterface, id: string, status: 'done' | 'failed', endedAt: number) {
  await update($, BOARD, board => {
    let changed = false
    const rows = board.rows.map(row => {
      const index = row.flow.findIndex(activity => activity.id === id)
      const activity = row.flow[index]
      if (index < 0 || !activity) return row
      changed = true
      const flow = row.flow.slice()
      flow[index] = { ...activity, status, endedAt }
      return { ...row, flow }
    })
    return changed ? { rows } : board
  })
}

async function tick($: EngineInterface) {
  const board = await read($, BOARD)
  if (!board.rows.some(row => row.status === 'running')) return
  const now = await $.clock.now()
  await update($, NOW, () => now)
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'requests',
      description: 'Request Progress: "/requests" shows the list, "/requests hide" hides it, "/requests clear" forgets every row',
      argumentHint: '[hide|show|clear]',
      immediate: true,
    })
    $.clock.every(TICK_MS, () => {
      void tick($).catch(() => undefined)
    })
    return next(e)
  })

  on('prompt.submit', async ($, e, next) => {
    const kind = e.origin.kind
    if (e.command || e.isMeta || (kind !== 'composer' && kind !== 'bridge')) return next(e)
    const now = await $.clock.now()
    const row: RequestRow = {
      id: `${now}-${seq++}`,
      title: titleOf(e.text),
      status: 'running',
      startedAt: now,
      endedAt: 0,
      durationMs: 0,
      steps: 0,
      tools: 0,
      turnId: e.turnId ?? '',
      flow: [],
    }
    await update($, BOARD, board => ({ rows: [...board.rows, row].slice(-KEEP) }))
    await update($, NOW, () => now)
    return next(e)
  })

  on('turn.start', async ($, e, next) => {
    if (e.agentId !== undefined) return next(e)
    activeTurn = e.turnId
    currentStep = 0
    await update($, BOARD, board => {
      const index = board.rows.findIndex(row => isOpen(row) && !row.turnId)
      const row = board.rows[index]
      if (index < 0 || !row) return board
      const rows = board.rows.slice()
      rows[index] = { ...row, turnId: e.turnId, status: 'running' }
      return { rows }
    })
    return next(e)
  })

  // The stream of one model request: watch what the model does as it does it.
  on('turn.step', async function* ($, e, next) {
    if (e.agentId === undefined) {
      currentStep = e.index
      if (!activeTurn) activeTurn = e.turnId
      await touchOpen($, row => ({ ...row, steps: row.steps + 1, status: 'running', turnId: row.turnId || e.turnId }))
    }
    let lastKind = ''
    for await (const chunk of next(e)) {
      if (e.agentId === undefined) {
        if (chunk.kind === 'thinking' || chunk.kind === 'text') {
          if (lastKind !== chunk.kind) {
            lastKind = chunk.kind
            const kind: ActivityKind = chunk.kind === 'thinking' ? 'thinking' : 'writing'
            const activity: Activity = {
              id: newId(),
              kind,
              label: kind,
              step: e.index,
              status: 'active',
              startedAt: Date.now(),
              endedAt: 0,
            }
            void addActivity($, e.turnId, activity).catch(() => undefined)
          }
        } else if (chunk.kind === 'stop') {
          lastKind = ''
          void touchOpen($, row => ({ ...row, flow: closeThoughts(row.flow) })).catch(() => undefined)
        }
      }
      yield chunk
    }
  })

  on('tool.call', async ($, e, next) => {
    if (e.agentId !== undefined) return next(e)
    const asking = e.tool === 'AskUserQuestion'
    const id = newId()
    const activity: Activity = {
      id,
      kind: asking ? 'ask' : toolKind(e.tool),
      label: asking ? 'question' : toolLabel(e.tool, e as unknown as Record<string, unknown>),
      step: currentStep,
      status: 'active',
      startedAt: Date.now(),
      endedAt: 0,
    }
    try {
      await touchOpen($, row => ({
        ...row,
        tools: row.tools + 1,
        status: asking ? 'needs-you' : 'running',
        turnId: row.turnId || activeTurn,
        flow: closeThoughts(row.flow).concat(activity).slice(-FLOW_KEEP),
      }))
    } catch {
      // The call goes on even when the drawing's bookkeeping fails.
    }
    const result = await next(e)
    try {
      const failed = typeof result === 'object' && result !== null && 'isError' in result && result.isError === true
      await finishActivity($, id, failed ? 'failed' : 'done', Date.now())
      if (asking) await touchOpen($, row => ({ ...row, status: 'running' }))
    } catch {
      // Same: the tool's answer is what matters.
    }
    return result
  })

  on('tool.check', async ($, e, next) => {
    const verdict = await next(e)
    if (e.agentId === undefined && verdict.decision === 'ask' && e.approver === 'person') {
      await touchOpen($, row => ({ ...row, status: 'needs-you' }))
    }
    return verdict
  })

  on('turn.complete', async ($, e, next) => {
    if (e.agentId !== undefined) return next(e)
    const now = await $.clock.now()
    const status: RequestStatus = e.reason === 'answer' ? 'done' : 'failed'
    await update($, BOARD, board => ({
      rows: board.rows.map(row => {
        if (row.turnId !== e.turnId || !isOpen(row)) return row
        const flow = row.flow.map(activity =>
          activity.status === 'active' ? { ...activity, status, endedAt: now } : activity,
        )
        return { ...row, status, endedAt: now, durationMs: e.durationMs, flow }
      }),
    }))
    if (activeTurn === e.turnId) activeTurn = ''
    await update($, NOW, () => now)
    return next(e)
  })

  on('command.run', { command: 'requests' }, async ($, e) => {
    const arg = e.args.trim().toLowerCase()
    if (arg === 'clear') {
      await update($, BOARD, () => ({ rows: [] }))
      return { text: 'Request Progress: cleared.' }
    }
    if (arg === 'hide') {
      await update($, HIDDEN, () => true)
      return { text: 'Request Progress hidden. Type /requests to show it again.' }
    }
    await update($, HIDDEN, () => false)
    const board = await read($, BOARD)
    if (board.rows.length === 0) {
      return { text: 'Request Progress is on: it lists each prompt once you send one.' }
    }
    return {
      text: `Request Progress: showing ${board.rows.length} request${board.rows.length === 1 ? '' : 's'}. /requests hide hides it, /requests clear forgets them.`,
    }
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (e.props.hasSurvey) return next(e)
    const [board, hidden, now] = await Promise.all([read($, BOARD), read($, HIDDEN), read($, NOW)])
    if (hidden || board.rows.length === 0) return next(e)
    // The other mods' bands draw above this one. Claude Code's own placeholder is never nested.
    const drawn = await Promise.resolve(next(e)).catch(() => null)
    const rest = drawn && typeof drawn === 'object' && (drawn as { type?: string }).type !== 'engine' ? drawn : null
    const { Box, Text } = $.ui.resolve(e)

    const cols = Math.max(24, Math.floor(e.props.bodyColumns) || 100)
    const barW = cols >= 72 ? 10 : cols >= 54 ? 7 : 0
    const statusW = 12
    const timeW = 7
    const titleW = Math.max(6, Math.min(38, cols - statusW - (barW ? barW + 2 : 0) - timeW - 4))
    const clock = Math.max(now, 0)

    const counts: Record<RequestStatus, number> = { running: 0, done: 0, 'needs-you': 0, failed: 0 }
    for (const row of board.rows) counts[row.status] += 1

    // The newest request still working gets the tree; finished ones stay one line.
    const active = [...board.rows].reverse().find(row => isOpen(row))
    const treeShown = active !== undefined && cols >= 40
    const room = Math.max(
      1,
      Math.min(treeShown ? TREE_ROWS : MAX_SHOWN, (e.props.maxRows || MAX_SHOWN + 1) - 1),
    )
    let shown = board.rows.slice(-room)
    if (active && !shown.some(row => row.id === active.id)) {
      shown = [active, ...board.rows.slice(-(room - 1))]
    }

    const blink = Math.floor(clock / 500) % 2 === 0

    const rows = shown.map(row => {
      const look = LOOK[row.status]
      const cells: unknown[] = []
      if (barW) {
        if (row.status === 'done') {
          for (let i = 0; i < barW; i++) {
            cells.push(
              <Text key={`b${i}`} color={i % 2 === 0 ? look.fill[0] : look.fill[1]}>
                █
              </Text>,
            )
          }
        } else {
          const items = row.flow.length > barW ? row.flow.slice(-barW) : row.flow
          for (let i = 0; i < barW; i++) {
            const activity = items[i]
            if (!activity) {
              cells.push(<Text key={`b${i}`} color={EMPTY}>·</Text>)
              continue
            }
            const style = FLOW[activity.kind]
            const newest = i === items.length - 1
            const live = newest && isOpen(row) && blink
            cells.push(
              <Text key={`b${i}`} color={style.color}>
                {live ? '▒' : style.glyph}
              </Text>,
            )
          }
        }
      }
      let tree: unknown = null
      if (treeShown && active && active.id === row.id) {
        const flat = row.flow.slice(-TREE_NODES)
        const trimmed = row.flow.length - flat.length
        const groups: { step: number; items: Activity[] }[] = []
        for (const activity of flat) {
          const last = groups[groups.length - 1]
          if (last && last.step === activity.step) last.items.push(activity)
          else groups.push({ step: activity.step, items: [activity] })
        }
        tree = (
          <Box key="tree" flexDirection="column" paddingLeft={statusW + 1} width={cols}>
            {trimmed > 0 ? <Text dimColor>{`… ${trimmed} earlier`}</Text> : null}
            {groups.length === 0 ? <Text dimColor>waiting for the model…</Text> : null}
            {groups.map((group, gi) => {
              const lastGroup = gi === groups.length - 1
              return (
                <Box key={`s${group.step}`} flexDirection="column">
                  <Text wrap="truncate-end">
                    <Text dimColor>{lastGroup ? '└─ ' : '├─ '}</Text>
                    <Text dimColor>{`step ${group.step + 1}`}</Text>
                  </Text>
                  {group.items.map((activity, ai) => {
                    const lastItem = ai === group.items.length - 1
                    const lead = lastGroup ? '   ' : '│  '
                    const thought = activity.kind === 'thinking' || activity.kind === 'writing'
                    return (
                      <Text key={activity.id} wrap="truncate-end">
                        <Text dimColor>{`${lead}${lastItem ? '└─ ' : '├─ '}`}</Text>
                        <Text color={FLOW[activity.kind].color}>{activity.label}</Text>
                        {thought ? null : activity.status === 'active' ? (
                          <Text dimColor>{blink ? ' ▸' : ' ▹'}</Text>
                        ) : (
                          <Text color={activity.status === 'failed' ? LOOK.failed.color : undefined} dimColor={activity.status !== 'failed'}>
                            {` ${activity.status === 'failed' ? '✗' : '✓'} ${duration(activity.endedAt - activity.startedAt)}`}
                          </Text>
                        )}
                      </Text>
                    )
                  })}
                </Box>
              )
            })}
          </Box>
        )
      }
      return (
        <Box key={row.id} flexDirection="column">
          <Box flexDirection="row" gap={1}>
            <Box width={statusW} flexShrink={0}>
              <Text color={look.color} bold>{look.glyph}</Text>
              <Text color={look.color}> {look.label}</Text>
            </Box>
            <Box width={titleW} flexShrink={0}>
              <Text wrap="truncate-end">{cut(row.title, titleW)}</Text>
            </Box>
            {barW ? (
              <Text key="bar">
                <Text dimColor>[</Text>
                {cells as never}
                <Text dimColor>]</Text>
              </Text>
            ) : null}
            <Box width={timeW} justifyContent="flex-end" flexShrink={0}>
              <Text
                color={row.status === 'failed' || row.status === 'needs-you' ? look.color : undefined}
                dimColor={row.status === 'running'}
              >
                {timeText(row, clock)}
              </Text>
            </Box>
          </Box>
          {tree as never}
        </Box>
      )
    })

    const summary = (
      <Box key="summary" flexDirection="row" justifyContent="space-between" gap={1}>
        <Text>
          <Text color={counts.running ? LOOK.running.color : undefined} dimColor={counts.running === 0}>
            * {counts.running} running
          </Text>
          {counts.done > 0 ? <Text dimColor>{'  ·  '}</Text> : null}
          {counts.done > 0 ? <Text color={LOOK.done.color}>✓ {counts.done} done</Text> : null}
          {counts['needs-you'] > 0 ? <Text dimColor>{'  ·  '}</Text> : null}
          {counts['needs-you'] > 0 ? (
            <Text color={LOOK['needs-you'].color}>! {counts['needs-you']} needs you</Text>
          ) : null}
          {counts.failed > 0 ? <Text dimColor>{'  ·  '}</Text> : null}
          {counts.failed > 0 ? <Text color={LOOK.failed.color}>✗ {counts.failed} failed</Text> : null}
          {board.rows.length > room ? (
            <Text dimColor>{`  ·  +${board.rows.length - room} earlier`}</Text>
          ) : null}
        </Text>
        <Text dimColor>/requests</Text>
      </Box>
    )

    return (
      <Box flexDirection="column">
        {rest as never}
        <Box key="request-progress" flexDirection="column">
          {rows as never}
          {summary as never}
        </Box>
      </Box>
    )
  })
}
