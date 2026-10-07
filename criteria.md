# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
I chose 4 of 5 because search is based on keyword overlap, so a query can
match the idea of an item without sharing enough of its description's words.
The two model calls can also vary, so one imperfect run should not mean the
whole path is unusable.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
I chose 5 of 5 because this is a direct, deterministic branch: an empty search
result should always stop the loop before either model-backed tool is called.
The agent can give the same useful next-step message on every such run.

---

## 3. Something about state

For a matching query, the `id` in `session["selected_item"]` is the same as
the `new_item["id"]` received by `suggest_outfit` in 5 of 5 tries.

**Why this target:**
I chose 5 of 5 because passing the selected dict into the next tool is a
deterministic state handoff. Comparing IDs makes it observable even if other
fields are reformatted or omitted from a trace.



---

## 4. Something about the fit card

Across 5 fit cards generated for the same item and outfit, at least 4 of 5
are 2–4 sentences and mention the item's title, price, and platform. Different
wording between cards is acceptable.

**Why this target:**
I chose 4 of 5 because model wording can vary, but the caption still needs its
key listing details and a postable length most of the time. I care more about
those details being present than identical wording across calls.



---

## 5. Your choice

For 5 queries with a price ceiling and at least one matching listing, every
listing returned by `search_listings` costs no more than that ceiling in 5 of
5 tries.

**Why this target:**
I chose 5 of 5 because comparing a listing's numeric `price` with the user's
maximum is deterministic, and a single over-budget result breaks the filter's
promise.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
