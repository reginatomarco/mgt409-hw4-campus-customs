# AI Prompt Log

- **2026-10-11 19:17:57 UTC** — **Problem 1: Vibe coder prompts:**

> ayy. I am starting homework #4 for my ai for managers class. Root below
>
> C:\Users\marco\_laptop\Desktop\Yale\Courses\Fall 2026\MGT 409 AI Foundations for Managers\Homework\hw4
>
> first thing's first. Start a AI\_prompts.md file in this folder and have it log all of my requests, a timestamp, and the problem # for each. I will tell you the problem #. This question starts "Problem 1: Viber coder prompts".

- **2026-10-11 19:18:42 UTC** — **Problem 1: Vibe coder prompts:**

> ya change it to vibe my bad

- **2026-10-11 19:19:27 UTC** — **Problem 1: Vibe coder prompts:**

> you have my portkey good to go?

- **2026-10-11 19:22:26 UTC** — **Problem 1: Vibe coder prompts:**

> we're still on problem 1, don't worry about it. I just want to lay a serious ground rule. Dont blow up the API Key with calls. I only have a few bucks left on it and need it to last

- **2026-10-11 19:24:34 UTC** — **Problem 1: Vibe coder prompts:**

> for this homework, we're going to build a helpful chatbot for Campus Customs (https://yalebulldogblue.com/)
>
> I will need to build a react + vite typscript front end and a python fastapi backend whose brain is a pydantic ai agent

- **2026-10-11 19:25:24 UTC** — **Problem 1: Vibe coder prompts:**

> I can't paste in the assignment instructions, that's against the rules lol... go ahead and install fastapi

- **2026-10-11 19:27:08 UTC** — **Problem 2: Analyze the database:**

> This is Problem 2: Analyze the database
>
> so I saved a dbs in the data/ folder. Tell me the name of each table and a brief description of each and what you see

- **2026-10-11 19:28:51 UTC** — **Problem 2: Analyze the database:**

> cool cool.
>
> start a file output/harness.md. Write each table and its fields in it, and one single line on why each field is important to the shop or chatbot that we'll build. We'll be adding onto this file later in the problem

- **2026-10-11 19:32:01 UTC** — **Problem 3: Build the Campus Customs website:**

> Problem 3: Build the Campus Customs website
>
> we're going to make a front end for Campus Customs (website was posted earlier). Use react+vite+typescript for the work
>
> Put a navigation bar at the top that links to the main pages: Home, Products, About Us, Log in, Create Account
>
> for Home and About Us, pull the Campus Customs-style wording from https://yalebulldogblue.com/ but dont just copy it, use your own words (or how I type - see other assignments for inspiration)

- **2026-10-11 19:32:37 UTC** — **Problem 3: Build the Campus Customs website:**

> actually, put the text in a GIGACHAD way thanks

- **2026-10-11 19:45:23 UTC** — **Problem 3: Build the Campus Customs website:**

> I got ERR\_CONNECTION\_REFUSED (-102) when I tried to open the page

- **2026-10-11 19:49:15 UTC** — **Problem 3: Build the Campus Customs website:**

> ok let's work on the Products page. There are a ton of images in the data folder (use the image paths in the dbs) show the images from the catalog with basic product info (name price, short GIGACHAD description)
>
> Make each product 1 page
>
> Clicking a card on products should take shopper there
>
> Also add a chat interface on the bottom-right of the site (a floating thing). No agent yet, just a stub placeholder for now before we do the backend.
>
> If you need to, start backend/main.py to serve products and images

- **2026-10-11 19:55:57 UTC** — **Problem 4: Create account and login:**

> Problem 4: Create account and login
>
> Let's work on the login. Make a normal flow with create account (first name, last name, email, password w/ confirm and a login (with email and password).
>
> New accounts go in the "user" table. Hey you've got passwords in the dbs, make sure they're secure from hackers and beta harvard
>
> There's a test user in the dbs already you can find. And a hash function for the password (idk)

- **2026-10-11 20:00:49 UTC** — **Problem 4: Create account and login:**

> oh my bad dog here's that test user's info
>
> email: [redacted]
> password: [redacted]
> hash fn: PBKDF2-HMAC-SHA256, 120,000 (stored as pbkdf2\_sha256$salt$hash)
>
> oh yea my prof mentioned adding a salt too so please do that

- **2026-10-11 20:04:57 UTC** — **Problem 4: Create account and login:**

> [Screenshot attached: Create Account form with the Last name box circled]
>
> ok, I tested the test user and I started a new user called gigachad and it seems to be working ok. A few cleanup things
>
> 1. For security reasons, delete the test user's credentials in the ai prompt file
> 2. In the Create Account tab, the Last Name fill in box extends past the box behind it (pic attached) can you pls fix?
> 3. update harness.md with how the authentication works (what you store for a user and how passwords are protected)

- **2026-10-11 20:08:37 UTC** — **Problem 5: PydanticAI agent backend:**

> Problem 5: PydanticAI agent backend
>
> make a chatbot as a pydanticai agent behind fastapi, plugged into the frontend chat widget. Put the api app in backend/main.py. Keep the agent as these 4 files next to it
>
> - backend/prompts/prompt.md - system prompt
> - backend/agent.py - agent entry/wiring
> - backend/tools.py - tools the agent can call
> - backend/models.py - pydantic/pydanticAI structured types
>
> in main.py show a chat route so a message from website returns a reply from agent

- **2026-10-11 20:14:31 UTC** — **Problem 5: PydanticAI agent backend:**

> in prompt.md, put Campus Customs voice and safety basics. Start or update types in models.py for chat replies / product cards as needed
>
> Update harness.md on how the front end talks to fastAPI and how the agent is loaded (prompt file + model)
>
> Can you make sure the backend runs from the backend/ folder like this?
>
> uvicorn main:app --reload --port 8000

- **2026-10-11 20:16:49 UTC** — **Problem 5: PydanticAI agent backend:**

> let me send a prompt right now

- **2026-10-11 20:17:56 UTC** — **Problem 5: PydanticAI agent backend:**

> ok I just ran a test w giga chad user and it works

- **2026-10-11 20:18:53 UTC** — **Problem 5: PydanticAI agent backend:**

> this website looks weak, can you pimp it out? Do I need to move you to Opus?

- **2026-10-11 20:34:26 UTC** — **Problem 5: PydanticAI agent backend:**

> Tried to inject sql into the chatbot and it doesnt like like it blew up a table. command below
>
> '; DROP TABLE users; --

- **2026-10-11 20:35:26 UTC** — **Problem 5: PydanticAI agent backend:**

> yeah add it to harness please

- **2026-10-11 20:36:46 UTC** — **Problem 5: PydanticAI agent backend:**

> also log that I tried to prompt the chat with non-related queries (ie hijacking it to use as my own AI without having to pay) and it was blocked

- **2026-10-11 20:37:44 UTC** — **Problem 5: PydanticAI agent backend:**

> yes please add that and include that in harness

- **2026-10-11 20:42:09 UTC** — **Problem 6: Tools: product info and stock:**

> Problem 6: Tools: product info and stock
>
> from campus\_customs.db give the agent product description, price, how many in stock by size so it can look up real info. I think you may have done this already?
>
> DONT INVENT STUFF. Say if an item is out of stock
>
> add this to prompt.md so the agent can call these tools for questions. Update return types in models.py
>
> in harness.md list each tool and explain which model fields you chose for lookup results and why

- **2026-10-11 20:45:47 UTC** — **Problem 6: Tools: product info and stock:**

> thanks looks like its working

- **2026-10-11 20:46:33 UTC** — **Problem 6: Tools: product info and stock:**

> hey just to double check on the password protection, is it secure and salted etc? I dont know much about that stuff

- **2026-10-11 20:47:25 UTC** — **Problem 6: Tools: product info and stock:**

> ok yeah add the includes a number and special character idea like normal passwords always require

- **2026-10-11 20:53:22 UTC** — **Problem 7: Chat search that updates the page:**

> Problem 7: Chat search that updates the page
>
> Ok lets do something cool. If a customer asks "what hoodies yall got?" the agent should search the catalog and the website should dynamically show those items as product cards with info
>
> After the dynamic card's loaded make sure the single-item behavior in Problem 3 stills works (each product should still open that detail view)
>
> update prompt.md and harness.md so it's clear how search results reach the page

- **2026-10-11 21:03:24 UTC** — **Problem 8: Customer memory:**

> Problem 8: Customer memory
>
> Now we're adding memory. When someone is logged in save their chat history in the dbs and reload when they come back. Put who (name, email) in agent deps and /or tools that the agent can call.
>
> Pass enough page context so if someone asks something like "do u have this in pink?" the agent knows that it's talking about
>
> document this in harness.md: how user chat history is stored, what customer fields the agent sees, and how page context is passed

- **2026-10-11 21:08:25 UTC** — **Problem 9: Usability improvements:**

> Problem 9: Usability improvements
>
> So on this question of the homework, I have to add 2 front-end and 2 agent/backend improvements.
>
> I think we kind of did this in the backend, where we made the password require a special character and capital letter. Have we/you done any other improvements?

- **2026-10-11 21:10:24 UTC** — **Problem 9: Usability improvements:**

> nice. Make a file called usability.md, add all these in there, and say why it helps a campus customs shopper or the business. Make sure all these things are actually in the app so the grader will be able to see them

- **2026-10-11 21:10:34 UTC** — **Problem 9: Usability improvements:**

> usability.md should be in output

- **2026-10-11 21:14:10 UTC** — **Problem 10: Style the website:**

> Problem 10: Style the website
>
> We're supposed to pimp this website out, but I think we did that earlier. The prompt is to add creative design "so that the site feels like a real Campus Customs storefront - fonts, color, hierarchy, motion, product presentation, chat feel"
>
> write output/design.md what you changed and why it should help customers stick around and buy. Keep it concrete and short

- **2026-10-11 21:15:33 UTC** — **Problem 10: Style the website:**

> remember the first version of this site? Can you explain in design.md what you changed from it to this version? So we get full credit

- **2026-10-11 21:18:49 UTC** — **Problem 11: Site testing (app check):**

> Problem 11: Site testing (app check)
>
> vibe check time. test the live site and document it in output/app\_check.html. Include clear screenshots and short captions for:
>
> - Chat checking the inventory level of an item (stock/price from dbs)
> - the dynamic search-result cards appearing after a category question (ie hoodie)
> - One of the usability features we added in Problem 9
>
> make the html easy to grade: heading for each check, screenshot, one or two sentences on what the screenshot proves.
>
> Put the screenshots in output/app\_check\_images/ and link them to app\_check.html with relative paths (ie app\_check\_images/inventory.png)
>
> hey make sure this all works and checks out, it's for my grade

- **2026-10-11 21:22:58 UTC** — **Problem 12: Audit trail, safety, finish harness:**

> Problem 12: Audit trail, safety, finish harness
>
> keep an append-only output/audit\_trail.json of agent-loop activity (time, tool name, short args/result, stop reason). Do not wipe it.

- **2026-10-11 21:25:40 UTC** — **Problem 12: Audit trail, safety, finish harness:**

> send 3 test messages for me please so that it logs

- **2026-10-11 21:27:00 UTC** — **Problem 12: Audit trail, safety, finish harness:**

> go for it if you think that makes it better. Be sure to log those results in the usability file too for full credit

- **2026-10-11 21:29:42 UTC** — **Problem 12: Audit trail, safety, finish harness:**

> any other safety rules you can think of for the agent? Are they all cataloged in prompts.md, right?

- **2026-10-11 21:30:17 UTC** — **Problem 12: Audit trail, safety, finish harness:**

> go for it

- **2026-10-11 21:34:55 UTC** — **Problem 12: Audit trail, safety, finish harness:**

> finish up harness.md so its clear how the system works
>
> - model fields in models.py and why you chose them
> - tools and abilities
> - safety rules
> - specs (loop limits, result caps, models, how to run front + back)

- **2026-10-11 21:40:42 UTC** — **Problem 13: Push to GitHub and submit the URL:**

> [Screenshots attached: expected hw4 file layout, and the local-only data pack (data/campus\_customs.db, data/products/)]
>
> Problem 13: Push to GitHub and submit the URL
>
> Alright, last part. We need to push this out. The stuff is all in a folder called hw4 (no API key in here please!). We need to push to a public GitHub repository (mine that is logged in). And I need to submit the repo URL to my grader
>
> Do not put the real .env, campus\_customs.db, or product images in the GitHub repo. Use .gitignore. Include .env.example with placeholders only. The expected file layout is attached.
>
> Local-only data pack (not in git) included as a screen shot
>
> The agent itself is four files under backend/ : promots/prompt.md, agent.py, tools,py, and models.py
>
> README.md should explain how to run the front and back end after placing the data pack
