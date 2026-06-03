# The Session Briefing Method

_How I keep AI-assisted work coherent from one session to the next._

## Starting cold every session

Every time you open a fresh session with an AI assistant on a real, multi-week project, you pay a tax. You re-explain what the project is, you re-derive what's already been decided, and the assistant - helpfully, and with complete confidence - reopens a question you closed three sessions ago. Work gets duplicated. The worst version of this is when a change you make today quietly contradicts a constraint you locked last week, and nobody notices, because that constraint only ever lived in a conversation that has since scrolled off.

The natural instinct is to wait for the tooling to solve it, with bigger context windows or better memory features. I don't think this is really a capacity problem, though. Project state is its own distinct thing, and it deserves a home of its own, maintained deliberately, in a form a fresh session can take in within seconds. That home is a session briefing.

## Forgetting what a change touched

Here's the observation that shaped the whole method. Across dozens of multi-session projects, the most damaging failure was never the assistant forgetting what we did - that one is recoverable, you can read the diffs. The real damage came from forgetting what a change touched: the downstream view that depended on the data model you just altered, the content someone authored against the validation rule you just relaxed, the decision from session 3 that the change in session 12 silently broke.

A good briefing is built to catch exactly that. It doesn't only record what happened. It records the decisions and the reasoning behind them, the open questions and what each one blocks, and the places where the docs and the code disagree. Those are the load-bearing parts of continuity, and they are the first things to disappear when project state lives in a conversation.

## One boundary keeps both documents lean

The method rests on a single rule: every fact about a project is either **timeless** or **timestamped**.

The timeless facts are things like what the project is, how to build and run it, the conventions you follow, the environment quirks, the gotchas that bite you. They are true whenever you read them, so they belong in the context file your harness already loads on its own - your `AGENTS.md`, `CLAUDE.md`, or `GEMINI.md`.

The timestamped facts are the current status, what changed this session, the decisions and the reasons for them, the next priorities, the open questions, and any drift between the spec and the code. They are true as of right now, so they belong in the briefing.

That is most of the trick, and it holds in both directions. If "how to run the tests" creeps into the briefing, the briefing slowly turns into a second README. If a "current status, do not relitigate" block piles up in the context file, that file gets too heavy to be worth loading on every session. Keep the line between them clean and both stay sharp.

There is a third category that belongs in neither: your personal working style, how you like to collaborate. That goes in the assistant's memory, written once. Re-narrating it for every project is how you end up with stale, half-localized copies that mislead more than they help.

## Never drop a section

AI assistants have a strong and well-meaning habit of tidying a document up, dropping a section that looks irrelevant to whatever they happen to be working on. In a session briefing that habit does real harm. The onboarding decision that looks beside the point while you are deep in a payments integration is exactly the thing a session three weeks from now will need.

So the method holds one rule above the rest: every section carries forward, every version. Only one section, "This Session," gets replaced outright on each update. Everything else is updated in place or left alone, never removed. In the coding version this is actually checked by a script. It compares the new briefing against the last committed one and fails if a section has gone missing, so the discipline does not rely on anyone remembering it.

## How it grew from chat into coding tools

The method started in chat. With no repo, no context file, and no git, a claude.ai briefing had to be a single self-contained document that held everything - thirteen sections, including a file inventory, working-style notes, and operational notes, because there was nowhere else for any of it to live. It worked, but it carried weight that a richer setup makes unnecessary.

Moving into coding tools changed the trade-offs. Now the project already has a context file, so the timeless reference moves there, and it has git, so version history comes for free and the briefing can be plain markdown whose diffs read cleanly from one session to the next. The coding version is really the chat briefing with the parts the environment now covers taken out, which drops thirteen sections to nine, and one new thing added that the environment made possible: the constellation.

One small but real lesson came out of that move. The chat version used to produce `.docx` files, and it shouldn't have. Markdown is cheaper on tokens, it diffs, and you can edit it in place. Chat interfaces convert an uploaded `.docx` to markdown on the way in anyway, so the binary format bought nothing except a misleading file extension and some wasted turns. Both versions are markdown now.

## From one project to a whole portfolio

A single briefing handles cold starts for one project. The real leverage shows up when you are running several related ones - a platform and its services, a product and its app, a monorepo of packages.

Keeping a hand-written "where does everything stand" document across a portfolio is a losing game, because it is stale the day after you write it. So the method derives that view instead of asking you to maintain it. Each child briefing names a parent. A `rollup` step reads every child and rebuilds a component matrix inside the parent, with each component's version, status, layer, and a link, so the parent is right because it was generated rather than because someone remembered to update it. A lightweight `[surface]` tag lets a child push a specific blocker or decision up into the parent's attention list, so even when you are head-down in one service, the portfolio view stays honest.

This is the part I'd put first. Carrying state from one session to the next is the obvious win, but the bigger payoff is carrying it across projects - a live overview of the whole constellation that builds itself - and once the per-project briefings exist, that part costs almost nothing to add.

You don't start there, though. You start with one briefing for one repo, you add a parent when a second project shows up, and you grow into the constellation from there. The first step is deliberately easy to reach, and there is plenty of room above it.

## The parts that don't automate

A script can scaffold a briefing, bump a version, wire up a pointer, and regenerate a matrix. What it cannot do is the part that actually matters, and that stays with you and the assistant together:

- **Downstream-impact checking.** Before a change, trace what it touches and flag the ripples before you act, not after.
- **Discrepancy tracking.** When the docs and the code disagree, name the conflict and let a human make the call, rather than quietly picking a value.
- **Decision-deadline flagging.** Name a pending decision, work out which dependency it actually blocks, and say whether it can wait. Don't push for a call before it is needed, and don't let a blocking one drift.

The script handles the clerical, drift-prone mechanics so they run the same way no matter which model is driving, and the judgment stays with you. That split, a deterministic anchor underneath and human judgment on top, is why the method holds up across different models and tools instead of slowly decaying into whatever the assistant felt like writing that day.

## What it is, and what it isn't

It isn't a platform or a service, and there is nothing to install. It is a markdown document, a small script with no dependencies, and a boundary you hold to. That is on purpose. The lightest thing that solves the problem is the thing you will actually keep doing, and continuity is a habit before it is a tool, so the whole method is built to make the habit cheap to keep.

If there is one thing to take from this, it is to stop letting your project state live in the conversation. Give it a home of its own, separate from your timeless docs, keep the line between the two clean, and don't drop the things a later session will need. Once that is working for one project, you can roll it up across the rest.
