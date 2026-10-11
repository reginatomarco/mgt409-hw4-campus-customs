# Campus Customs: AI shopping assistant

A storefront for Campus Customs (Yale apparel, 57 Broadway, New Haven) with a built-in AI shopping assistant.

- **Frontend:** React + Vite + TypeScript (`frontend/`)
- **Backend:** Python FastAPI (`backend/main.py`)
- **Assistant:** a PydanticAI agent made of four files in `backend/`:
  - `prompts/prompt.md`: system prompt (voice, tool use, stock rules, safety)
  - `agent.py`: builds the agent, connects the model through Portkey, runs each chat turn
  - `tools.py`: read-only tools (`search_products`, `get_product_details`, `check_stock`, `get_customer_profile`)
  - `models.py`: Pydantic types for the agent's reply, tool results, run context and chat API

Supporting backend modules: `auth.py` and `security.py` (accounts, password hashing, sessions, rate limits), `db.py` (SQLite), `blurbs.py` (product taglines), `audit.py` (audit trail).

## 1. Place the data pack

The database and product images are **not** in this repository. Put the data pack in the `hw4` folder so it looks like this:

```
hw4/
└── data/
    ├── campus_customs.db
    └── products/          # images referenced by the catalogue
```

## 2. Add your API key

```
cp .env.example .env       # Windows: copy .env.example .env
```

Open `.env` and set `PORTKEY_API_KEY`. The key is needed only for the chat assistant; browsing products and logging in work without it.

## 3. Run the backend (terminal 1)

Requires Python 3.11+.

```
pip install -r requirements.txt
cd backend
uvicorn main:app --reload --port 8000
```

The API runs on http://127.0.0.1:8000 (interactive docs at `/docs`). If `uvicorn` isn't found, use `python -m uvicorn main:app --reload --port 8000`.

## 4. Run the frontend (terminal 2)

Requires Node.js 20+.

```
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**. The frontend forwards `/api` and `/images` to the backend on port 8000, so start the backend first.

## Try it

- Browse **Products**, filter by category, open a product, pick a size.
- **Create an account** (the password needs 8+ characters with a letter, a number and a special character), then click **Ask the Bulldog**:
  - "what hoodies yall got?": results appear on the Products page as cards
  - "do you have this in XL?" on a product page: live stock from the database
  - "anything with Handsome Dan?": finds the bulldog gear
- Log out and back in: your chat history comes back.

## Project layout

```
hw4/
├── AI_prompts.md           # log of every prompt used to build this project
├── requirements.txt        # backend Python packages
├── .env.example            # copy to .env and add your key (placeholders only)
├── README.md
├── frontend/               # Vite React TypeScript app
├── backend/
│   ├── main.py             # FastAPI app: uvicorn main:app --reload --port 8000
│   ├── agent.py
│   ├── models.py
│   ├── tools.py
│   └── prompts/
│       └── prompt.md
└── output/
    ├── harness.md          # how the system works: specs, tools, model fields, safety
    ├── design.md           # design changes and why
    ├── usability.md        # usability improvements
    ├── app_check.html      # live test report with screenshots
    ├── app_check_images/   # screenshots linked from app_check.html
    └── audit_trail.json    # append-only log of agent activity
```

## Notes

- **Never commit** `.env`, `data/`, or `backend/.session_secret`; `.gitignore` covers them.
- Chat cost limits: at most 4 model calls and 25,000 tokens per message; 20 messages/hour logged in, 10/hour as a guest, 300/day site-wide.
- `output/audit_trail.json` is append-only: new agent activity is added to the end, and nothing removes old entries.
- Full documentation of the system is in **`output/harness.md`**.
