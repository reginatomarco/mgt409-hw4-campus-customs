# Campus Customs: usability improvements

This file lists the usability improvements in the Campus Customs app beyond what the earlier problems required. For each one it explains what it does, how to see it in the running app, and why it helps a Campus Customs shopper or the business.

The required **2 frontend + 2 agent/backend** improvements are listed first. Additional improvements follow.

**Running the app:** start the backend (`cd backend` then `uvicorn main:app --reload --port 8000`) and the frontend (`cd frontend` then `npm run dev`), then open http://localhost:5173. Improvements marked *(no API cost)* can be checked without sending a chat message.

---

## The four main improvements

### Frontend 1: Live password checklist on Create Account

**What it does:** under the password box, a checklist shows the four password rules: at least 8 characters, a letter, a number, and a special character. Each rule turns green with a ✓ as you type. The "Create account" button stays disabled until every rule passes and both password boxes match.

**How to see it** *(no API cost)*: open **Create Account**, click the Password box, and type slowly, e.g. `bulldog` → `bulldog1` → `bulldog1!`, and watch the rules tick.

**Why it helps:**
- **Shopper:** no "submit, get rejected, guess again" loop. A student signing up on their phone between classes sees exactly what's missing before pressing the button.
- **Business:** fewer abandoned sign-ups. Every account that gets created is one the assistant can remember (saved chat history, greeting by name), which brings customers back.

**Code:** `frontend/src/pages/CreateAccount.tsx` (the `rules` list and the disabled button), styles in `frontend/src/index.css` (`.password-rules`).

---

### Frontend 2: "Ask the assistant" button and suggestion chips

**What it does:**
- Every product page has a **💬 Ask the assistant** button. It opens the chat with a question about that product already typed in, e.g. "Tell me more about the District Vit Hoodie Vintage Bulldog. What goes well with it?". If a size is selected, the question asks whether that size is a good pick.
- When the chat opens with no history, it shows suggestion chips: "What hoodies yall got?", "Cheapest hoodie?", "Anything with Handsome Dan?", "Gift for a Yale mom", "Saybrook gear".
- Clicking a chip or the button only **fills in** the question. The shopper still presses Send, so nothing is sent (or paid for) by accident.

**How to see it** *(no API cost)*: open any product, e.g. **Products → Basic Hoodie Big Yale**. Click **Ask the assistant** and the chat opens with the question filled in. Log out (or use a private window), click **Ask the Bulldog** in the bottom-right, and the chips appear under the greeting.

**Why it helps:**
- **Shopper:** many people don't know what to ask a store chatbot. One click starts a useful conversation about the exact item they're looking at.
- **Business:** more shoppers actually use the assistant, which answers sizing and stock questions that would otherwise go to staff at 57 Broadway or end in a lost sale. The chips also show off what the assistant is good at (search, price, gifts, college gear).

**Code:** `frontend/src/pages/ProductPage.tsx` (button calling `openChat(...)`), `frontend/src/chatEvents.ts` (opens the chat from any page), `frontend/src/components/ChatWidget.tsx` (`SUGGESTIONS`, `onOpenChat`).

---

### Agent/backend 1: Smarter product search (shopper words → catalogue words)

**What it does:** the agent's `search_products` tool translates the way shoppers talk into the words the catalogue uses:

| Shopper says | Search understands | Result (real data) |
| --- | --- | --- |
| "Handsome Dan" (Yale's bulldog mascot) | bulldog | 10 bulldog items (before: 0 results) |
| "hoodie", "hoodies", "hoody" | also matches "hooded sweatshirt" and "Full Zip Hood" | 27 hoodies |
| "1/4 zip", "quarter zip" | the catalogue's "1 4 Zip" names | 11 quarter-zips |
| "tee", "tees" | t-shirt | 25 tees |
| "grey" | gray | gray items |

It also ignores filler words ("do you have any…") and ranks name matches above description matches.

**How to see it:**
- *(no API cost)* run `python -c "from tools import search_products as s; print(s(None, query='handsome dan').total_matches)"` from `backend/` and it prints `10`.
- *(1 chat message)* ask the chat "anything with Handsome Dan?".

**Why it helps:**
- **Shopper:** they find what they want in their own words. In the original chat logs (`chat_messages`), a shopper asked for "handsome dan" three times and was told there was nothing, even though the store sells 10 bulldog items.
- **Business:** a "we don't have that" when the product is on the shelf is a lost sale. Mapping campus slang (Handsome Dan) and spelling variants turns those dead ends into recommendations.

**Code:** `backend/tools.py` (`SYNONYMS`, `STOPWORDS`, `_normalize`, `_terms`).

---

### Agent/backend 2: Password strength rules with clear error messages

**What it does:** the backend refuses new passwords that don't have at least 8 characters, a letter, a number and a special character. The error says exactly what's missing, e.g. "Password needs a number, a special character (like ! @ # $)." Rejected forms also never send the typed password back in the error response.

**How to see it** *(no API cost)*: the frontend checklist (Frontend 1) normally stops weak passwords before they're sent. To see the backend rule on its own, send a weak password straight to the API:

```
curl -X POST http://localhost:5173/api/auth/register -H "Content-Type: application/json" \
  -d "{\"first_name\":\"a\",\"last_name\":\"b\",\"email\":\"x@test.edu\",\"password\":\"password1\",\"confirm_password\":\"password1\"}"
```

It returns `422` with `"Password needs a special character (like ! @ # $)."` and no copy of the password.

**Why it helps:**
- **Shopper:** their account, chat history and saved details are harder to break into, and the message tells them exactly how to fix the password.
- **Business:** protects the store's customer accounts and reputation. Enforcing the rule on the server means it can't be bypassed by skipping the website. Existing accounts aren't locked out, because the rules apply only when signing up.

**Code:** `backend/auth.py` (`strong_password`), `backend/main.py` (`validation_error` handler, which drops the typed input from errors).

---

## Additional improvements

### Frontend

| Improvement | How to see it *(all no API cost)* | Why it helps |
| --- | --- | --- |
| **Products search, sort and category filters**, saved in the URL | **Products**: type "bulldog" in the search box, pick "Price: low to high", click **Hoodies**. The address becomes e.g. `/products?category=hoodies&sort=price-asc`. Refresh or share it and the same view comes back. The footer's Shop links use the same URLs. | Shoppers narrow 102 products to what they want in seconds. Shareable links help with "look at these" texts to friends or parents. |
| **Size buttons with live stock** on product pages | Open **Baseball Left Chest Crewneck**: XS and XL are crossed out and can't be clicked (sold out). Open **Yale Mom Hoodie** and click **XXL**: "🔥 Only 2 left in XXL. Move fast." Click **L**: "✓ L is in stock." | Shoppers don't fall for a size that's gone, and low-stock messages nudge them to buy. Fewer disappointed in-store trips. |
| **Breadcrumbs and "More hoodies"** on product pages | Any product page: *Products / Hoodies / …* at the top, and 4 similar items at the bottom. | Easy to step back to the category or keep browsing instead of leaving the site. |
| **Mobile menu** | Make the browser window narrow: the nav collapses into a ☰ menu. | Students often browse on their phones between classes; the site stays usable on a small screen. |
| **Loading placeholders** | Products page while loading: grey shimmer cards instead of a blank page. | The site feels fast and doesn't look broken on slow campus Wi-Fi. |
| **Product cards inside chat replies** | Ask the chat about a product (1 message): the reply shows clickable photo cards. | Shoppers go from chat answer to product page in one tap. |

### Agent/backend

| Improvement | How to see it | Why it helps |
| --- | --- | --- |
| **Sold-out alternatives** | *(no API cost)* from `backend/`: `python -c "from tools import check_stock as c; print(c(None,'baseball-left-chest-crewneck','XL'))"` prints a result including `status='sold_out' other_sizes_in_stock=['S', 'M', 'L', 'XXL']`. In chat (1 message): "do you have the Baseball Left Chest Crewneck in XL?" | Instead of a dead-end "sold out", the assistant offers sizes that are in stock, which saves the sale. |
| **Chat rate limits** | 20 messages/hour when logged in, 10/hour as a guest, 300/day site-wide. Over the limit, the chat shows "Easy, legend. That's 10 messages this hour. Try again in N minutes." (Triggering it live would take 10+ paid messages; it was tested offline with lowered limits: 200, 200, then 429, and the blocked message never reached the AI.) | Keeps the assistant available and affordable. One person or script can't run up the store's AI bill or slow it down for other shoppers. |
| **Login lockout and safe errors** | 5 wrong passwords for the same email lock it for 15 minutes. Wrong email and wrong password both say "Invalid email or password." | Stops password guessing without revealing which emails have accounts. |

---

## Live test log from the audit trail (Problem 12)

After the audit trail was added, three test messages were sent to the live assistant as a guest on 2026-10-11 (21:25 UTC). The audit trail (`output/audit_trail.json`) recorded what the agent did for each one:

| Shopper message | Tools the agent called (from the audit trail) | Reply | Usability result |
| --- | --- | --- | --- |
| "do you have this in XL?" on the **Baseball Left Chest Crewneck** page | `check_stock` → "XL: 0 left (sold_out)" | "The **Baseball Left Chest Crewneck** is sold out in XL. It's in stock in **S, M, L, and XXL**." | Page context worked ("this" = the open product), and **sold-out alternatives** worked: the shopper gets sizes they can buy instead of a dead end. |
| "what hoodies yall got?" | `search_products {"garment_type": "hoodie"}` → 27 matches | "Found **27 hoodies**, all on the page now. Top picks: …" | Search with "yall" slang worked, and all 27 results went to the page as cards. |
| "what is the square root of 25?" | `search_products {"query": "square root 25"}` → 1 match | "I'm here to help you shop officially licensed Yale apparel, not solve math problems…" | Off-topic request declined, so the store's AI isn't used as a free homework helper. |

Each turn took 2 model calls, about 6,200 to 7,000 input tokens and 95 to 140 output tokens, finishing with `stop_reason: final_result`.

### Experiment: skipping the wasted lookup on off-topic questions (tried, measured, reverted)

The audit trail showed that the off-topic question still triggered a catalogue search ("square root 25"), which wastes one model call per off-topic message. Two prompt changes were tried, each tested with the same question, and compared using the audit trail:

| Version | Tool calls | Model calls | Input tokens | Reply |
| --- | --- | --- | --- | --- |
| Original prompt | `search_products` | 2 | 6,190 | Declined ✅ |
| + "decline off-topic requests without calling any tools" in Safety | `search_products` | 2 | 6,304 | Declined ✅ |
| + a "When not to use tools" rule at the top of the tools section | `search_products` | 2 | 6,418 | **Answered the math ("5")** ❌ |

**Result:** neither change stopped the extra search, and the second one made things worse: the assistant answered the off-topic question. Both changes were **reverted**; the prompt is back to the original wording, confirmed by its size being identical to before (9,511 characters).

**Takeaway:** prompt wording alone didn't control this model's tool use, and a "helpful" prompt edit can quietly break a safety rule. The audit trail made both problems visible with numbers instead of guesses. If the extra lookup ever becomes a real cost problem, the fix belongs in code (for example, a cheap check for obviously off-topic messages before the agent runs) rather than in more prompt text. For now, the cost is already capped by the chat rate limits and per-message token limits.

## Verification

Each improvement was checked in the running app on 2026-10-11:

| Improvement | Check | Result |
| --- | --- | --- |
| Password checklist | Rendered `/create-account` | 4 checklist rules present |
| Ask the assistant / chips | Rendered a product page; code check | Button present; 5 `SUGGESTIONS` in the chat widget |
| Smarter search | Called `search_products` on the real database | "handsome dan" 10, "hoodies" 27, "1/4 zip" 11, "tees" 25 |
| Password rules | Live `POST /api/auth/register` with `password1` | 422 "needs a special character", no password echoed |
| Products filters | Rendered `/products?category=hoodies&sort=price-asc&q=yale` | Search box, sort menu, category chips, "27 styles" |
| Size buttons | Rendered `/products/baseball-left-chest-crewneck` | 2 disabled (sold-out) size buttons, breadcrumbs, 4 related items |
| Mobile menu | Rendered home page | Menu toggle present |
| Sold-out alternatives | Called `check_stock(..., "XL")` | `sold_out`, offers S, M, L, XXL |
| Rate limits | Offline test, guest limit 2, fake AI model | 200, 200, 429; 2 model calls |
