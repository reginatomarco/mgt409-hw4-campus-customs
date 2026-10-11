# Campus Customs: design

The goal is a site that feels like Yale's own team store, not a template: bold, school-colored, a little GIGACHAD, with the products front and center. All styles are in `frontend/src/index.css`.

## Before → after

The first version (Problem 3) was a working but plain React page. The redesign (Problems 5 to 10) turned it into a storefront.

| Area | First version | Now |
| --- | --- | --- |
| Fonts | The computer's default font (`system-ui`) everywhere. | Oswald for headlines and prices, Inter for body text, bundled with the app. |
| Color | Navy and light blue only, flat white cards. | Navy, gold and blue with clear jobs (brand, calls to action, links); gold announcement bar and ticker. |
| Nav bar | A blue bar with the text "Campus Customs" and 5 plain links. | Gold announcement strip, "CC" logo badge with a "Yale Bulldog Blue" tagline, gold underline on the current page, a gold Create Account button, "Hi, {name}" with an avatar when logged in, and a ☰ menu on mobile. |
| Home | A blue gradient box with a headline and two buttons, 4 text-only cards, and one banner. | A full-width hero with a collage of 3 real product photos and stats (102 styles, 14 colleges, XS–XXL), a scrolling slogan ticker, Shop by category tiles with photos and counts, a featured products row, icon cards, and a Family Weekend promo. |
| Products page | A grid of small cards (photo, name, type, price) and nothing to filter with. | Search box, sort menu, category buttons with counts, result count, loading placeholders, and bigger cards with a category tag, GIGACHAD blurb, large price and "View →" on hover. Can also show the assistant's search results. |
| Product page | Photo plus plain text chips for colors and sizes, and a "← Back" link. | Breadcrumbs, a large photo that stays in view, a gold GIGACHAD callout, clickable size buttons (sold out crossed out, "🔥 Only 2 left"), "Grab it at 57 Broadway", "Ask the assistant", and a "More hoodies" row. |
| About | A text page with headings and a bullet list. | A full-width banner, a two-column story with a navy pull quote, and numbered "code" cards. |
| Log in / Create Account | A single plain form card. | A two-panel card (navy panel with a slogan and perks, then the form), rounded inputs with blue focus rings, and a live password checklist. |
| Chat | A round 💬 button and a basic panel that always replied with a placeholder. | An "Ask the Bulldog" button, a header with a 🐶 avatar and "Online" status, texting-style bubbles, typing dots, suggestion chips, product photo cards in replies, and search results that open on the page. |
| Footer | One line of text. | A navy footer with the logo, Shop / Store / Visit columns and links. |
| Motion | Only a small lift on product cards. | Hover lifts and photo zoom, nav underlines, a hero collage that fans out, the slogan ticker, loading shimmer, chat pop-in, all switched off for "reduce motion". |

## Fonts
- **Oswald** (bold, condensed, uppercase) for headlines, prices and product names: the look of varsity jerseys and stadium signs. **Inter** for body text, so descriptions and forms stay easy to read.
- Both are bundled with the app (`@fontsource`), so they load fast with no outside requests.
- **Why it sells:** the headline type says "athletic Yale gear" before the shopper reads a word, and readable body text keeps them reading product details.

## Color
- **Yale navy `#00356b`** dominates (nav, buttons, prices); **gold `#f2b632`** is used sparingly for the announcement bar, "Create Account", the slogan ticker and highlights; **blue `#286dc0`** for links and focus rings. The page background is a soft gray-blue, so the white product cards stand out.
- **Why it sells:** school colors make it feel official, which matters for "officially licensed" merch. Gold appears only where we want clicks, so the eye goes to the calls to action.

## Hierarchy
- **Home** follows a storefront path: hero ("Some people wear clothes. Bulldogs wear a legacy.") → scrolling slogans → **Shop by category** → **Certified bangers** (featured items) → why-us cards → Family Weekend promo.
- **Product page:** large photo on the left (it stays in view while you scroll); on the right, name → **price** → GIGACHAD line in a gold callout → description → colors → size buttons → actions.
- **Products page:** search and sort first, then category buttons with counts, then the grid.
- **Why it sells:** shoppers see what we sell and how to get to it in the first screen, and on a product page the price and sizes come before the fine print.

## Motion
- Cards lift and photos zoom slightly on hover; nav links get a gold underline; buttons rise 2px.
- The hero collage fans out on hover, a gold slogan ticker scrolls under the hero, gray shimmer placeholders show while products load, and the chat panel pops in.
- Every animation is short (0.15 to 0.4 s). If a shopper's device has "reduce motion" turned on, motion is switched off everywhere.
- **Why it sells:** small motion says "this is clickable" and makes the store feel alive; loading placeholders keep people from leaving on slow Wi-Fi.

## Product presentation
- Uniform cards: square photo on white, a navy category tag ("HOODIES"), the name in Oswald, a one-line GIGACHAD blurb, a big price, and "View →" on hover.
- The product page shows stock per size: sold-out sizes are crossed out, and low stock shows "🔥 Only 2 left". It also has breadcrumbs, a "More hoodies" row, and "Grab it at 57 Broadway" (opens Google Maps).
- **Why it sells:** consistent cards make the catalogue easy to compare; honest stock and urgency cues help people decide; related items keep them browsing.

## Chat feel
- A navy "**Ask the Bulldog**" button with a gold border. The chat header has a 🐶 avatar and "Online · knows every hoodie"; the bubbles look like texting, with navy for the shopper and white for the assistant.
- Animated typing dots, suggestion chips, product photo cards inside replies, and search results that open on the Products page as full cards.
- **Why it sells:** it feels like texting a store employee rather than filling in a form, and every answer is one tap away from the product page.

## Also
- **Mobile:** the nav collapses into a ☰ menu, and grids and the product page stack into one column.
- **Brand touches:** a gold announcement bar ("Officially licensed Yale gear · 57 Broadway"), a "CC" logo badge, and a dark navy footer with Shop, Store and Visit links.
