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

**Branch rule:** If `search_listings` returns an empty list, put an informative message in `session["error"]` and stop. Otherwise, take the first result, save it as the selected item, and continue to `suggest_outfit`.

**Where it lives:** `agent.py::run_agent`

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
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

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
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

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

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
