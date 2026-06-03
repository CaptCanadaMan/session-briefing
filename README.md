# Session Briefing

Keep your AI assistant up to speed on your projects, so a new session picks up where the last one left off.

Session Briefing is a pair of skills that have your assistant keep a short, living notes file for each project - what it is, where things stand, what you've decided, and what's next - and read it back at the start of every new session. So instead of re-explaining the project every time you open a fresh chat, the assistant already knows where you left off.

If you've ever left a handover note for a coworker so they could pick up your work, that's basically the idea, except here the assistant writes and reads the note for you.

There are two versions, depending on where you work.

## If you work in the chat assistant (claude.ai)

This is the simple one, and you don't need to be technical to use it. Add the `chat-session-briefing` skill to claude.ai, or just attach its instructions to a Project. From then on you can ask Claude to "start a session briefing" when you begin, or "update the briefing" when you finish a working session. Everything stays in one tidy document that you bring back next time to get Claude caught up.

That's the whole thing - no setup, no command line.

→ [chat-skills/chat-session-briefing/](chat-skills/chat-session-briefing/)

## If you work in a coding tool (Claude Code and similar)

Same idea, fitted to how coding tools work. The briefing lives in a small notes folder of its own, and a tiny Python helper handles the fiddly parts for you, like version numbers and keeping the notes linked to your project. The helper needs nothing installed - it's plain Python.

The easiest way to start is to add the skill and run the guided setup, which asks you a few questions and wires everything up:

```sh
cp -r agent-skills/agent-session-briefing ~/.claude/skills/
cp -r agent-skills/setup-session-briefing ~/.claude/skills/
```

Then run the `setup-session-briefing` skill and follow along. If you'd rather just see the commands, they're all in [docs/cli.md](docs/cli.md).

It works with Claude Code out of the box, and with any tool that keeps an `AGENTS.md`, `CLAUDE.md`, or `GEMINI.md` file - the helper just notices which one you have.

→ [agent-skills/agent-session-briefing/](agent-skills/agent-session-briefing/)

## Running more than one project

If you've got a few related projects on the go, the coding version can roll them all up into a single overview, so you can see where everything stands without keeping a status doc current by hand. You don't have to use this part - one project works fine on its own - but it's there when you grow into it. There's a worked example in [docs/example-constellation.md](docs/example-constellation.md).

## More detail

- [docs/methodology.md](docs/methodology.md) - how the method works, and why it's built the way it is.
- [docs/cli.md](docs/cli.md) - the command reference for the coding version.

## License

[MIT](LICENSE).
