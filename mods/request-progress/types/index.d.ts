export type RequestStatus = 'running' | 'done' | 'needs-you' | 'failed'

export type ActivityKind = 'thinking' | 'writing' | 'bash' | 'tool' | 'ask'

export type ActivityStatus = 'active' | 'done' | 'failed'

/** One thing the turn did, in order: a thought, a written word, a tool. */
export type Activity = {
  id: string
  kind: ActivityKind
  /** What the tree calls it: "thinking", "Bash · npm test". */
  label: string
  /** The model request (turn.step index) that produced it. */
  step: number
  status: ActivityStatus
  startedAt: number
  endedAt: number
}

/** One prompt the person sent, and how far its turn got. */
export type RequestRow = {
  id: string
  /** The prompt, whitespace collapsed, cut when drawn. */
  title: string
  status: RequestStatus
  startedAt: number
  /** 0 until the turn ends. */
  endedAt: number
  /** The turn's own wall-clock length, from `turn.complete`. */
  durationMs: number
  /** Model requests this turn has made. */
  steps: number
  /** Tool calls this turn has made. */
  tools: number
  /** The turn that carries this request; empty until a turn starts. */
  turnId: string
  /** The turn's realtime flow, oldest first; the bar draws the newest cells. */
  flow: Activity[]
}

/** The list the band draws, oldest first. */
export type RequestBoard = {
  rows: RequestRow[]
}

declare module 'claude-code' {
  interface PluginState {
    'request-progress': {
      board: RequestBoard
      /** Clock time of the last tick, so the bar and timers move. */
      now: number
      /** True while `/requests hide` hides the band. */
      hidden: boolean
    }
  }
}
