# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> FitFindr searches secondhand listings, suggests outfits from a saved wardrobe,
> and writes a fit-card caption for a selected item.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

FitFindr takes a natural-language request for a secondhand clothing item and
searches listings by description keywords, with optional size and price filters.
For matches, it compares the result prices, chooses the top listing, suggests
outfits using saved wardrobe pieces, and creates a short fit-card caption. If
nothing matches, it stops with a helpful message; opted-in runs can also reuse a
wardrobe saved from an earlier run.

---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Finds listings whose description matches the requested keywords, with optional size and maximum-price filters.
- **Inputs:** `description` (str); `size` (str | None, optional); `max_price` (float | None, optional, inclusive).
- **Returns:** Matching listing dicts, ordered best match first and limited by `config.SEARCH_RESULT_LIMIT`; each dict has `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.
- **When it has nothing:** Returns an empty list (`[]`). A requested size matches a whole size label or a whole slash-separated size component, case-insensitively; for example, `M` matches `M`, `S/M`, and `M/L`, but not `XL` or `L/XL`.

### `suggest_outfit`

- **What it does:** Suggests one or two outfits using a listing the user is considering and, when available, pieces from their wardrobe.
- **Inputs:** `new_item` (dict with the listing fields above); `wardrobe` (dict with an `items` list of wardrobe-item dicts containing `id`, `name`, `category`, `colors`, `style_tags`, and optional `notes`).
- **Returns:** A non-empty string with one or two outfit suggestions; when wardrobe items exist, the suggestions name pieces from that wardrobe.
- **When it has nothing:** An empty wardrobe (`{"items": []}`) still returns general styling advice for `new_item`, rather than an empty string or an error.

### `create_fit_card`

- **What it does:** Writes a short, post-ready caption about the find and its suggested outfit.
- **Inputs:** `outfit` (str, the suggestion from `suggest_outfit`); `new_item` (dict with the listing fields above).
- **Returns:** A two-to-four-sentence caption that mentions the item, its price, and its platform once each, and describes its vibe.
- **When it has nothing:** If `outfit` is empty or whitespace, returns a descriptive fallback message instead of raising an error.

### `compare_prices` — stretch tool

- **What it does:** Summarizes the prices among the current search results so the user can compare the selected item with similar listings.
- **Inputs:** `listings` (list[dict], the results returned by `search_listings`).
- **Returns:** A dict with `count` (int), `lowest` and `highest` (listing dicts), and `average` (float).
- **When it has nothing:** Returns `{"count": 0, "lowest": None, "highest": None, "average": None}` for an empty list.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list and the query included a size, retry once with the same description and price ceiling but `size=None`. If that retry is also empty, put an informative message in `session["error"]` and stop. If the first search or retry returns listings, save its first result as the selected item and continue to `suggest_outfit`.

**Where it lives:** `agent.py::run_agent`

**MCP transport:** `run_agent()` calls both `search_listings` and `compare_prices` through `mcp_client.call_tool(...)`; both are registered in `mcp_server.py`. The client unwraps each response to the same native list or summary dict returned by the direct tool function.

**Unit 4 stretch plans (declared before implementation):**

- Move the existing `compare_prices` summary tool onto MCP as a second
  registered tool, and show its call in the loop trace.
- If a search with a requested size is empty, retry once with the same
  description and price ceiling but no size filter. Label the retry and the
  dropped size in the trace. I checked `graphic tee` at size `XS`: the strict
  search returned `[]`, while the same search without size returned six items.
- Measure this retry as the second improvement, with a third five-criterion,
  five-try run log and an honest before/after comparison.

**Second branch (stretch):** If the wardrobe has items, request combinations using those owned pieces. If it is empty, request general styling advice and mark the session mode as `general`.

**How the query is parsed:** Regular expressions extract an optional size and price ceiling; the remaining words become the search description.

**What moves through the session:** `parsed` → `search_results` → `price_comparison` → `selected_item` → `outfit_suggestion` → `fit_card`. Each tool's result is stored in the session and read from there for the next step.

**Style memory (stretch):** With `--remember-wardrobe`, the CLI saves a non-empty wardrobe in the ignored `.cache/` folder. On a later opted-in run with `--empty-wardrobe`, it loads the saved wardrobe and uses its pieces in outfit suggestions. Without the opt-in flag, an empty wardrobe stays empty.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'
Found:    Graphic Tee — 2003 Tour Bootleg Style — $24.0 on depop
Compare:  8 listings range from $15.00 to $27.00; average $21.75.

Outfit:   Here are two ways to style your 2003 tour bootleg tee using items already in your closet:

### Outfit 1: 90s Grunge Streetwear
Lean into the boxy, worn-in feel of the tee by pairing it with darker denim and chunky footwear.
* **Bottoms:** Baggy straight-leg jeans (dark wash)
* **Shoes:** Black combat boots
* **Accessories:** Black crossbody bag
* **How to wear it:** Tuck the graphic tee in slightly to balance the boxy fit with the baggy jeans. Finish with the combat boots and crossbody bag for an effortless, everyday grunge look.

### Outfit 2: Layered Contrast (Warm & Cool Tones)
Use the tee as a base layer to play with proportions and mix your dark streetwear pieces with earth tones.
* **Bottoms:** Wide-leg khaki trousers
* **Outerwear:** Vintage black denim jacket
* **Shoes:** Chunky white sneakers
* **Accessories:** Brown leather belt
* **How to wear it:** Wear the graphic tee untucked over the khaki trousers, cinched with the brown leather belt to break up the colors. Throw the vintage black denim jacket on top and anchor the outfit with the chunky white sneakers for a casual, high-low streetwear vibe.

Fit card: Channel effortless 90s attitude by throwing this worn-in tour tee over baggy denim and chunky combat boots. The Graphic Tee — 2003 Tour Bootleg Style is listed for $24 on depop.

1 model calls this session, 1 served from cache
```

**Empty-search branch**

```
$ python app.py ask 'designer ballgown size XXS under $5'
No listings matched 'designer ballgown'. Try size XXS or a higher price ceiling than $5 or a different item description.
0 model calls this session
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print([(item['id'], item['title'], item['price']) for item in search_listings('graphic tee', max_price=30)])"
[('lst_002', 'Y2K Baby Tee — Butterfly Print', 18.0), ('lst_006', 'Graphic Tee — 2003 Tour Bootleg Style', 24.0), ('lst_017', 'Mesh Long-Sleeve Top — Black', 15.0), ('lst_033', 'Vintage Band Tee — Faded Grey', 19.0), ('lst_011', 'Low-Rise Cargo Pants — Khaki', 27.0), ('lst_015', 'Vintage Graphic Hoodie — Faded Black', 26.0)]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[5], get_example_wardrobe()))"
Here are two ways to style your 2003 tour bootleg tee using items already in your closet:

### Outfit 1: 90s Grunge Streetwear
Lean into the boxy, worn-in feel of the tee by pairing it with darker denim and chunky footwear.
* **Bottoms:** Baggy straight-leg jeans (dark wash)
* **Shoes:** Black combat boots
* **Accessories:** Black crossbody bag
* **How to wear it:** Tuck the graphic tee in slightly to balance the boxy fit with the baggy jeans. Finish with the combat boots and crossbody bag for an effortless, everyday grunge look.

### Outfit 2: Layered Contrast (Warm & Cool Tones)
Use the tee as a base layer to play with proportions and mix your dark streetwear pieces with earth tones.
* **Bottoms:** Wide-leg khaki trousers
* **Outerwear:** Vintage black denim jacket
* **Shoes:** Chunky white sneakers
* **Accessories:** Brown leather belt
* **How to wear it:** Wear the graphic tee untucked over the khaki trousers, cinched with the brown leather belt to break up the colors. Throw the vintage black denim jacket on top and anchor the outfit with the chunky white sneakers for a casual, high-low streetwear vibe.
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
Effortless weekend energy, fueled by broken-in denim and crisp white kicks. The Vintage Levi's 501 Jeans — Medium Wash is listed for $38 on depop.
```

**Stretch tool: `compare_prices`**

```
$ python -c "from tools import compare_prices, search_listings; s = compare_prices(search_listings('graphic tee', max_price=30)); print({'count': s['count'], 'lowest': s['lowest']['price'], 'highest': s['highest']['price'], 'average': s['average']})"
{'count': 6, 'lowest': 15.0, 'highest': 27.0, 'average': 21.5}
```

**Second branch: empty wardrobe**

```
$ python app.py ask 'denim jacket under $50' --empty-wardrobe
(running with an empty wardrobe)
Found:    Denim Jacket — Light Wash, Cropped — $42.0 on poshmark
Compare:  5 listings range from $24.00 to $45.00; average $34.20.
Styling:  general ideas because no wardrobe items are saved.
Fit card: Layering this cropped vintage wash over baggy denim brings effortless 90s attitude to your daily rotation. The Denim Jacket — Light Wash, Cropped is listed for $42 on poshmark.
```

**Style memory: two opted-in runs**

```
$ python app.py ask 'vintage graphic tee under $30' --remember-wardrobe
Saved 10 wardrobe pieces for future opted-in runs.

$ python app.py ask 'denim jacket under $50' --empty-wardrobe --remember-wardrobe
Using the wardrobe remembered from an earlier opted-in run.
Outfit: Here are two ways to style your new cropped light-wash denim jacket using only pieces from your wardrobe:
* White ribbed tank top, baggy straight-leg jeans, chunky white sneakers, and black crossbody bag.
* Black cropped zip hoodie, wide-leg khaki trousers, black combat boots, and brown leather belt.
```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* I asked AI to turn the listing fields and `search_listings` signature into a concrete tool contract, including size matching and no-match behavior.
- *What came back:* It proposed matching whole size labels and slash-separated sizes, and returning an empty list when no listings match.
- *What I changed:* I checked the actual size values, wrote the exact rule in Tool Inventory, and implemented it so `M` matches `S/M` but not `XL`.

**Moment 2**

- *What I asked for:* I asked AI to wire `run_agent()` so every tool result goes through the session and empty search stops before outfit generation.
- *What came back:* It found the tools were still stubs, then added keyword search, model-backed outfit and fit-card tools, and the early-return branch.
- *What I changed:* I recorded the ID passed into `suggest_outfit` and compared it with `session["selected_item"]["id"]`; I also checked that an impossible query leaves `fit_card` as `None` and gives a useful message.

**Moment 3 — Unit 4**

- *What I asked for:* I asked AI to compare repeated fit-card openings in the before run and choose one prompt improvement that followed that pattern.
- *What came back:* It pointed out that the same-item captions repeatedly began with “Channeling,” and suggested asking for a fresh, distinctive opening and avoiding stock lead-ins.
- *What I changed:* I updated only the prompt in `tools.py::create_fit_card`, then ran all 25 after-evaluation tries. The model connection failed with a DNS `ConnectError`, so I recorded the results as inconclusive for the prompt change instead of claiming it helped.

**Moment 4 — stretch work**

- *What I asked for:* I asked Codex to expose a second existing tool over MCP and add one retry when a size-filtered search returns nothing.
- *What came back:* It suggested keeping the description and price ceiling fixed while setting only `size` to `None`, and routing `compare_prices` through the same MCP client.
- *What I changed:* I implemented both MCP registrations/calls and the one-retry branch. A live trace showed the XS search return nothing, the size-free retry return six listings, and `compare_prices` run over MCP. I kept the retry limited to one attempt.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before tool 2 | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Selected item ID reaches `suggest_outfit` unchanged | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Same-item, same-outfit fit card has 2–4 sentences and names title, price, platform | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Five capped queries return only listings at or below their ceiling | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

**Real output from one try per criterion**. The complete uncached run and all
25 attempt records are in `results/run_2026-10-18_2231_before.md` (35 live
model calls; cache off).

**Criterion 1 — `agent.py::run_agent`, recorded by `run_eval.py::run_once`**

```text
[1] search_listings (via MCP)
      in:  {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
      out: 8 items: Graphic Tee — 2003 Tour Bootleg Style, Y2K Baby Tee — Butterfly Print, Vintage Graphic Hoodie — Faded Black … +5 more
[2] compare_prices
      in:  {'listing_count': 8}
      out: dict with keys: count, lowest, highest, average…
[3] suggest_outfit
      in:  {'item_id': 'lst_006', 'wardrobe_item_count': 10}
      out: Here are two wearable ways to style your 2003 tour bootleg tee using only what's in your closet:  **Outfit 1: …
[4] create_fit_card
      in:  {'item_id': 'lst_006'}
      out: Channeling effortless festival energy, this faded tee looks instantly cool tucked into crisp trousers or doubl…
Fit card: Channeling effortless festival energy, this faded tee looks instantly cool tucked into crisp trousers or doubled up on denim. The Graphic Tee — 2003 Tour Bootleg Style is listed for $24 on depop.
```

**Criterion 2 — `agent.py::run_agent`**

```text
[1] search_listings (via MCP)
      in:  {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
      out: [] (empty)
      →    empty result; stopping
No listings matched 'designer ballgown'. Try size XXS or a higher price ceiling than $5 or a different item description.
```

**Criterion 3 — session state and `suggest_outfit` input, `agent.py::run_agent`**

```text
session["selected_item"]["id"]: lst_006
[3] suggest_outfit
      in:  {'item_id': 'lst_006', 'wardrobe_item_count': 10}
```

**Criterion 4 — `tools.py::create_fit_card`**

```text
[3] suggest_outfit
      out: Baggy dark denim, black combat boots, and a brown leather belt.
[4] create_fit_card
      in:  {'item_id': 'lst_006'}
      out: Channeling effortless backstage energy with distressed denim and heavy boots, this worn-in tour tee looks like…
Channeling effortless backstage energy with distressed denim and heavy boots, this worn-in tour tee looks like you caught the best show of 2003 from the front row. The Graphic Tee — 2003 Tour Bootleg Style is listed for $24 on depop.
```

**Criterion 5 — `tools.py::search_listings`, called through MCP**

```text
vintage graphic tee under $30: lst_006=$24.0, lst_002=$18.0, lst_015=$26.0, lst_017=$15.0, lst_033=$19.0, lst_011=$27.0, lst_012=$20.0, lst_030=$25.0
90s track jacket under $50: lst_004=$45.0, lst_007=$42.0, lst_010=$40.0, lst_013=$30.0, lst_019=$48.0, lst_031=$36.0, lst_032=$33.0
leather belt under $20: lst_014=$12.0
denim jacket under $45: lst_007=$42.0, lst_004=$45.0, lst_016=$24.0, lst_032=$33.0, lst_038=$27.0
silk button-down under $30: lst_029=$28.0, lst_014=$12.0, lst_020=$16.0
```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | Matching query completes all three tools | 4 of 5 | MET (5/5) | All five traces show `search_listings`, `suggest_outfit`, and `create_fit_card`, with a non-empty fit card. |
| 2 | Impossible query stops before tool 2 | 5 of 5 | MET (5/5) | Every impossible-query run returned an actionable message and stopped after search, before `suggest_outfit`. |
| 3 | Selected item ID reaches `suggest_outfit` unchanged | 5 of 5 | MET (5/5) | In all five matching runs, `session["selected_item"]["id"]` and the `suggest_outfit` input were `lst_006`. |
| 4 | Same-item, same-outfit fit card meets length and detail requirements | 4 of 5 | MET (5/5) | With the item and outfit fixed, all five cards had two sentences and named the title, `$24`, and `depop`. |
| 5 | Five capped queries return only listings at or below their ceiling | 5 of 5 | MET (5/5) | Each of five distinct capped queries returned at least one listing, and every listed price was at or below its cap. |

**Diagnoses**

No criteria were missed, so there is no failing tool, branch, session handoff, or model output to diagnose. Criteria 1 and 4 were conservative for this sample: each allowed one miss and both passed 5/5. Five tries are too few to say those targets are generally too low, especially because both criteria include model calls. If I tightened one next, I would tighten criterion 4 to require all five captions to have distinct opening sentences while still naming the listing details. I am not revising the current criterion because it was measurable and met.

**Exploratory diagnosis behind the retry improvement:** A separate
`search_listings` check for `graphic tee`, size `XS`, and a $30 ceiling returned
no listings; removing only the size returned six. The mechanism was the tool's
strict size filter, followed by `run_agent` stopping on any empty result. This
wasn't a miss on criterion 2's impossible-query scenario, but it identified a
recoverable empty-search case and motivated the retry improvement below.


---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Earlier full model path (before `compare_prices` moved onto MCP)**

```
[1] search_listings (via MCP)
      in:  {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
      out: 8 items: Graphic Tee — 2003 Tour Bootleg Style, Y2K Baby Tee — Butterfly Print, Vintage Graphic Hoodie — Faded Black … +5 more
[2] compare_prices
      in:  {'listing_count': 8}
      out: dict with keys: count, lowest, highest, average…
[3] suggest_outfit
      in:  {'item_id': 'lst_006', 'wardrobe_item_count': 10}
      out: Here are two ways to style your 2003 tour bootleg tee using items already in your closet:  ### Outfit 1: 90s G…
[4] create_fit_card
      in:  {'item_id': 'lst_006'}
      out: Channel effortless 90s attitude by throwing this worn-in tour tee over baggy denim and chunky combat boots. Th…
```

**Original empty-search trace (before the size-retry improvement)**

```
[1] search_listings (via MCP)
      in:  {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
      out: [] (empty)
      →    empty result; stopping

No listings matched 'designer ballgown'. Try size XXS or a higher price ceiling than $5 or a different item description.
```

**Second MCP tool and size-retry trace** (`app.py::ask`, live run):

```text
[1] search_listings (via MCP)
      in:  {'description': 'graphic tee', 'size': 'XS', 'max_price': 30.0}
      out: [] (empty)
      →    empty; retrying once without size
[2] search_listings (retry via MCP)
      in:  {'description': 'graphic tee', 'size': None, 'max_price': 30.0}
      out: 6 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Mesh Long-Sleeve Top — Black … +3 more
      →    dropped size filter after empty first search
[3] compare_prices (via MCP)
      in:  dict with keys: listings…
      out: dict with keys: count, lowest, highest, average…
[4] suggest_outfit
      in:  {'item_id': 'lst_002'}
      out: unavailable
      →    model unavailable; stopping

I couldn't reach the model for outfit advice. Check your API key or connection and try again.
```

**Completed-path integration trace:** The same five steps completed with test
stand-ins for the model-backed `suggest_outfit` and `create_fit_card`; both MCP
calls above were live. The stand-ins were used only to verify the full control
flow while the model endpoint could not resolve.

```text
[1] search_listings (via MCP)
      in:  {'description': 'graphic tee', 'size': 'XS', 'max_price': 30.0}
      out: [] (empty)
      →    empty; retrying once without size
[2] search_listings (retry via MCP)
      in:  {'description': 'graphic tee', 'size': None, 'max_price': 30.0}
      out: 6 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Mesh Long-Sleeve Top — Black … +3 more
      →    dropped size filter after empty first search
[3] compare_prices (via MCP)
      in:  dict with keys: listings…
      out: dict with keys: count, lowest, highest, average…
[4] suggest_outfit
      in:  {'item_id': 'lst_002', 'wardrobe_item_count': 10}
      out: Test outfit with dark denim and boots.
[5] create_fit_card
      in:  {'item_id': 'lst_002'}
      out: Test fit card for Y2K Baby Tee — Butterfly Print at $18.0.
session: search_retries=1, selected_item=lst_002, price_comparison.count=6, error=None
```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



**What changed:** I replaced the direct `search_listings(...)` call in `agent.py::run_agent` with `mcp_client.call_tool("search_listings", ...)`; `search_listings` and `compare_prices` are now registered with descriptions and typed inputs in `mcp_server.py`. `python mcp_client.py` listed both, and MCP `compare_prices` returned the same count, lowest and highest listings, and average as the direct function. The live query shows the second MCP call in the trace. The price-summary shape did not change; the size retry is the separately described search behavior change.

**Three failure checks**

- **Empty search:** `python app.py ask 'designer ballgown size XXS under $5' --trace` returned: “No listings matched 'designer ballgown' even after dropping size XXS. Try a higher price ceiling than $5 or a different item description.” The trace shows the initial empty MCP search and one retry with `size=None`, then stops before `suggest_outfit`.
- **Empty wardrobe:** `python app.py ask 'denim jacket under $50' --empty-wardrobe --trace` completed without a crash or blank suggestion. It printed “Styling: general ideas because no wardrobe items are saved.” and returned general outfit advice.

  ```text
  Here are two wearable, high-contrast ways to style this cropped light-wash denim jacket:

  **1. The 90s Streetwear Contrast**
  * **The Look:** Pair the jacket with baggy, wide-leg dark bottoms (like black cargo pants or dark fatigue trousers) to play with proportions against the cropped, structured shoulders.
  * **Details:** Layer it over a tight, ribbed white baby tee or a black crop top. Finish with chunky sneakers and a casual crossbody bag.

  **2. The Texture Play**
  * **The Look:** Throw it over a floral, slip-style midi dress in a darker color (like emerald green, burgundy, or black) to mix rugged denim with something delicate and fluid.
  * **Details:** Ground the sweetness of the dress with chunky combat boots or retro leather loafers.

  *Stylist Tip:* Because it’s a blank canvas, let the jacket's structure do the work—pop the collar slightly and push up the sleeves for an effortless, lived-in feel.
  ```

- **Model unavailable:** The live query `graphic tee size XS under $30` reached `suggest_outfit` after retrying search and comparing prices, then reported “I couldn't reach the model for outfit advice. Check your API key or connection and try again.” It stopped without a raw stack trace.

```text
[1] search_listings (via MCP)
      in:  {'description': 'graphic tee', 'size': 'XS', 'max_price': 30.0}
      out: [] (empty)
      →    empty; retrying once without size
[2] search_listings (retry via MCP)
      in:  {'description': 'graphic tee', 'size': None, 'max_price': 30.0}
      out: 6 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Mesh Long-Sleeve Top — Black … +3 more
      →    dropped size filter after empty first search
[3] compare_prices (via MCP)
      in:  dict with keys: listings…
      out: dict with keys: count, lowest, highest, average…
[4] suggest_outfit
      in:  {'item_id': 'lst_002'}
      out: unavailable
      →    model unavailable; stopping
```

---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

In `tools.py::create_fit_card`, I changed the prompt to ask for a fresh,
distinctive opening, avoid stock lead-ins such as “Channeling” and “This look,”
and vary sentence structure. The before log's same-item captions repeatedly
opened with “Channeling,” even though they met the original length and detail
criterion.

**Which failure it was meant to fix:**

The repetitive opening pattern in the fit-card model output. My earlier
diagnosis suggested checking whether repeated cards could have distinct
openings, so I changed only the fit-card prompt to target that pattern.

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools | 4 of 5 | FAIL | FAIL | FAIL | FAIL | FAIL | MISSED (0/5) |
| 2. Impossible query stops before tool 2 | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Selected item ID reaches `suggest_outfit` unchanged | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Same-item fit card meets length and detail requirements | 4 of 5 | FAIL | FAIL | FAIL | FAIL | FAIL | MISSED (0/5) |
| 5. Five capped queries return only listings at or below their ceiling | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

The complete uncached evaluation (all 25 tries) is in
[`results/run_2026-10-19_0020_after.md`](results/run_2026-10-19_0020_after.md).
The API connection check is also recorded below; the full test output is from
`test.py::main`.

**Real output from one try per criterion** (`run_eval.py::run_once`):

**Criterion 1 — matching query**

```text
[1] search_listings (via MCP) — 8 items, including Graphic Tee — 2003 Tour Bootleg Style
[2] compare_prices — dict with keys: count, lowest, highest, average
[3] suggest_outfit — unavailable; stopping
Message: I couldn't reach the model for outfit advice. Check your API key or connection and try again.
```

**Criterion 2 — impossible query**

```text
[1] search_listings (via MCP)
      out: [] (empty)
      → empty result; stopping
No listings matched 'designer ballgown'. Try size XXS or a higher price ceiling than $5 or a different item description.
```

**Criterion 3 — selected item reaches `suggest_outfit`**

```text
selected_item: Graphic Tee — 2003 Tour Bootleg Style ($24.0, depop)
[3] suggest_outfit
      in: {'item_id': 'lst_006', 'wardrobe_item_count': 10}
      out: unavailable
```

**Criterion 4 — fit card**

```text
[3] suggest_outfit
      out: Baggy dark denim, black combat boots, and a brown leather belt.
[4] create_fit_card
      in: {'item_id': 'lst_006'}
      out: unavailable
      → model unavailable; stopping
```

**Criterion 5 — capped searches**

```text
vintage graphic tee under $30: lst_006=$24.0, lst_002=$18.0, lst_015=$26.0, lst_017=$15.0, lst_033=$19.0, lst_011=$27.0, lst_012=$20.0, lst_030=$25.0
90s track jacket under $50: lst_004=$45.0, lst_007=$42.0, lst_010=$40.0, lst_013=$30.0, lst_019=$48.0, lst_031=$36.0, lst_032=$33.0
leather belt under $20: lst_014=$12.0
denim jacket under $45: lst_007=$42.0, lst_004=$45.0, lst_016=$24.0, lst_032=$33.0, lst_038=$27.0
silk button-down under $30: lst_029=$28.0, lst_014=$12.0, lst_020=$16.0
```

**Did it help, and how do I know:**

The first after-run missed criteria 1 and 4 because the model endpoint failed
DNS resolution: `agent.py::run_agent` stopped at `suggest_outfit` for criterion
1, and the `create_fit_card` call returned unavailable for criterion 4. No
model output came back, so that run could not tell whether the prompt changed
caption quality. After `test.py` passed with network access, the full live
rerun below produced five same-item cards with five distinct opening sentences;
all five before-run cards began with “Channeling.” The prompt change appears to
have reduced the repeated opening pattern. Criterion 4's original
length-and-detail target passed 5/5 both before and after.

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

### Second Improvement — retry without size

**Diagnosis:** Before the change, `search_listings("graphic tee", size="XS", max_price=30)` returned no items, while the same description and price ceiling without a size returned six. The `search_listings` tool's strict size filter produced the empty result; `run_agent` treated that as a total miss even though looser results existed in the data.

```text
tools.py::search_listings before retry:
graphic tee XS []
loose ['lst_002', 'lst_006', 'lst_017', 'lst_033', 'lst_011', 'lst_015']
```

**Change:** After an empty size-filtered MCP search, `agent.py::run_agent` makes exactly one more `search_listings` call with the same description and maximum price and `size=None`. It records the dropped size in the trace. I also moved the already-existing `compare_prices` call to MCP, as declared in the stretch plan above.

### Run Log — After Second Improvement

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before tool 2 | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Selected item ID reaches `suggest_outfit` unchanged | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Same-item fit card meets length and detail requirements | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Five capped queries return only listings at or below their ceiling | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

The final live, uncached five-try-per-criterion output is in
[`results/run_2026-10-19_0035_after-retry-final.md`](results/run_2026-10-19_0035_after-retry-final.md).
The run is produced by `run_eval.py::main`; each attempt calls
`agent.py::run_agent` through `run_eval.py::run_once`.

An initial attempt from the restricted shell is also recorded in
[`results/run_2026-10-19_0027_after-retry.md`](results/run_2026-10-19_0027_after-retry.md);
it hit the DNS error. After `test.py` passed with network access, I reran the
same scenarios with live model calls. The table above reflects that final run.

**Real output from the after-retry run:**

```text
Criterion 2 — Try 1:
[1] search_listings (via MCP)
      in:  {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
      out: [] (empty)
      →    empty; retrying once without size
[2] search_listings (retry via MCP)
      in:  {'description': 'designer ballgown', 'size': None, 'max_price': 5.0}
      out: [] (empty)
      →    dropped size filter after empty first search
No listings matched 'designer ballgown' even after dropping size XXS. Try a higher price ceiling than $5 or a different item description.

Criterion 1 — Try 1:
[1] search_listings (via MCP)
      in:  {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
      out: 8 items: Graphic Tee — 2003 Tour Bootleg Style, Y2K Baby Tee — Butterfly Print, Vintage Graphic Hoodie — Faded Black … +5 more
[2] compare_prices (via MCP)
      in:  dict with keys: listings…
      out: dict with keys: count, lowest, highest, average…
[3] suggest_outfit
      in:  {'item_id': 'lst_006', 'wardrobe_item_count': 10}
      out: Here are two practical, wearable ways to style your new graphic tee using only items already in your wardrobe:…
[4] create_fit_card
      in:  {'item_id': 'lst_006'}
      out: Worn-in tour merch meets off-duty skater grit when heavy cotton denim and fresh white kicks enter the chat. Th…

Criterion 3 — Try 1:
selected_item: Graphic Tee — 2003 Tour Bootleg Style ($24.0, depop)
[3] suggest_outfit
      in:  {'item_id': 'lst_006', 'wardrobe_item_count': 10}
      out: **Outfit 1: 90s Streetwear Grunge** * **The Look:** Lean into the tee’s boxy fit and vintage vibe by pairing i…

Criterion 4 — Try 1:
Fit card: Slouchy 2003 tour merch paired with heavyweight denim and stompy black boots brings effortless, mosh-pit energy to a rainy Tuesday. The Graphic Tee — 2003 Tour Bootleg Style is listed for $24 on depop.

Criterion 5 — returned listing prices:
vintage graphic tee under $30: lst_006=$24.0, lst_002=$18.0, lst_015=$26.0, lst_017=$15.0, lst_033=$19.0, lst_011=$27.0, lst_012=$20.0, lst_030=$25.0
90s track jacket under $50: lst_004=$45.0, lst_007=$42.0, lst_010=$40.0, lst_013=$30.0, lst_019=$48.0, lst_031=$36.0, lst_032=$33.0
leather belt under $20: lst_014=$12.0
denim jacket under $45: lst_007=$42.0, lst_004=$45.0, lst_016=$24.0, lst_032=$33.0, lst_038=$27.0
silk button-down under $30: lst_029=$28.0, lst_014=$12.0, lst_020=$16.0
```

**Did it help:** Yes. The live `graphic tee size XS under $30` query changed from no size-specific results to six listings after dropping only the size filter; the $30 ceiling remained in effect. The latest full run met all five criteria at their stated targets. The earlier DNS-limited attempt is kept as a separate record and is superseded by the live run above.

---

## What's Still Broken

The final live run (`results/run_2026-10-19_0035_after-retry-final.md`) met all
five criteria, so no criterion is currently missed. The earlier restricted
shell attempt failed at the model calls with a DNS `ConnectError`; I stopped
that attempt there, ran `test.py` again with network access, and reran all 25
tries successfully. The model-backed features still need a working network;
that was an environment issue in the first attempt, not a remaining code fix.

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with both tools registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] Second improvement, with a third five-try run log
       [ ] Empty size search retries once with the size filter removed
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
