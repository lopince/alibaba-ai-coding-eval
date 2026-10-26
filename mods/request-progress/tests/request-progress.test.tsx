import type { On } from 'claude-code'
import { expect, test } from 'claude-code/testing'

const BAND = {
  plugin: 'request-progress',
  component: 'AbovePrompt',
  requestId: 'band',
  props: {
    hasSurvey: false,
    isWorking: true,
    maxRows: 6,
    bodyColumns: 100,
    scroll: { offset: 0, bodyRows: 5 },
    view: {},
  },
} as const

// What the engine answers beneath the mod: the session, the clock and the
// events the mod raises on its way through.
function engineBelow(on: On) {
  on('session.start', () => ({ cwd: '/' }))
  on('clock.now', () => ({ value: 1_000 }))
  on('clock.every', () => ({ value: undefined }))
  on('command.register', () => ({ value: { command: 'requests' } }))
  on('prompt.submit', (_$, e) => ({ text: e.text }))
  on('turn.start', () => ({ turnId: 't1' }))
  on('turn.complete', () => ({ text: '' }))
  on('tool.call', () => ({ result: {} }))
  // The engine's own drawing beneath the mod: an empty band.
  on('ui.render', ($, e) => {
    const { Text } = $.ui.resolve(e)
    return <Text> </Text>
  })
}

test('a prompt draws as a running row', async ($, on) => {
  engineBelow(on)
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  await $.prompt.submit({ text: 'Fix the login bug', origin: { kind: 'composer' }, wait: false })

  const ui = await $.ui.mount({ ...BAND, surface: 'terminal' })

  expect((await ui.find({ type: 'Text', text: /Fix the login bug/ }))?.text).toContain('Fix the login bug')
  expect((await ui.find({ type: 'Text', text: /running/ }))?.text).toContain('running')
  expect((await ui.find({ type: 'Text', text: /waiting for the model/ }))?.text).toContain('waiting for the model')
  await ui.unmount()
})

test('a turn moves its row to done', async ($, on) => {
  engineBelow(on)
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  await $.prompt.submit({ text: 'Run the tests', origin: { kind: 'composer' }, wait: false })
  await $.turn.start({ text: 'Run the tests', turnId: 't1' })
  await $.turn.complete({ answer: 'done', durationMs: 12_000, isAborted: false, turnId: 't1', reason: 'answer' })

  const ui = await $.ui.mount({ ...BAND, surface: 'terminal' })

  expect((await ui.find({ type: 'Text', text: /✓ 1 done/ }))?.text).toContain('done')
  await ui.unmount()
})

test('a tool call joins the request flow', async ($, on) => {
  engineBelow(on)
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  await $.prompt.submit({ text: 'Run the tests', origin: { kind: 'composer' }, wait: false })
  await $.turn.start({ text: 'Run the tests', turnId: 't1' })
  await $.tool.call({ tool: 'Bash', command: 'npm test' })

  const ui = await $.ui.mount({ ...BAND, surface: 'terminal' })

  expect((await ui.find({ type: 'Text', text: /Bash · npm test/ }))?.text).toContain('Bash · npm test')
  expect((await ui.find({ type: 'Text', text: /step 1/ }))?.text).toContain('step 1')
  expect((await ui.find({ type: 'Text', text: /✓/ }))?.text).toContain('✓')
  await ui.unmount()
})

test('a prompt from another origin adds no row', async ($, on) => {
  engineBelow(on)
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  await $.prompt.submit({ text: 'background work', origin: { kind: 'task-notification' }, wait: false })

  const ui = await $.ui.mount({ ...BAND, surface: 'terminal' })

  expect(await ui.find({ type: 'Text', text: /background work/ })).toBeUndefined()
  await ui.unmount()
})
