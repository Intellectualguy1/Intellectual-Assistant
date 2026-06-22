\# Intellectual Assistant



An open-source AI assistant that checks a local knowledge base first, uses web search when needed, and generates grounded answers with source links.



\## Features



\* Local knowledge-base responses

\* Tavily web-search fallback for questions outside the knowledge base

\* Ollama-powered local AI responses

\* Casual conversation handling without wasting web-search requests

\* Source links for web-based responses

\* React chat interface

\* FastAPI backend

\* Configurable AI and search providers

\* Time-complexity notes documented in major modules

\* SQLite conversation memory architecture for persistent chat history



\## Architecture



```text

User Message

&#x20;    ↓

Casual Conversation Check

&#x20;    ↓

Local Knowledge Base

&#x20;    ↓

Context / Follow-up Resolution

&#x20;    ↓

Tavily Web Search Fallback

&#x20;    ↓

Ollama Local LLM

&#x20;    ↓

Final Answer + Sources

```



\## Tech Stack



\### Backend



\* Python

\* FastAPI

\* SQLite

\* Tavily Search API

\* Ollama

\* Mistral or DeepSeek local model

\* python-dotenv



\### Frontend



\* React

\* Vite

\* CSS



\## Project Structure



```text

intellectual-assistant/

├── backend/

│   ├── main.py

│   ├── config.py

│   ├── schemas.py

│   ├── conversation.py

│   ├── context\_resolver.py

│   ├── knowledge\_base.py

│   ├── web\_search.py

│   ├── llm\_provider.py

│   ├── database.py

│   ├── memory.py

│   └── requirements.txt

├── frontend/

│   ├── src/

│   │   ├── App.jsx

│   │   └── index.css

│   └── package.json

├── data/

│   └── knowledge.json

├── .env.example

├── .gitignore

└── README.md

```



\## How It Works



1\. The assistant checks whether a user message is casual conversation, such as “Hello” or “How are you?”

2\. It checks the local knowledge base for relevant saved information.

3\. If no answer is found, it uses Tavily to search the web.

4\. Search results are passed to a local Ollama model.

5\. The model generates a concise answer based on the retrieved sources.

6\. The frontend displays the answer and source links.



\## Local Setup



\### Prerequisites



Install:



\* Python 3.10+

\* Node.js 18+

\* Ollama

\* A local Ollama model such as Mistral or DeepSeek

\* A Tavily API key



\### Clone the Repository



```bash

git clone https://github.com/Intellectualguy1/Intellectual-Assistant.git

cd Intellectual-Assistant

```



\### Backend Setup



```bash

cd backend

python -m venv venv

```



Windows:



```powershell

venv\\Scripts\\activate

```



Install dependencies:



```bash

pip install -r requirements.txt

```



Create a `.env` file in the project root using `.env.example` as a guide:



```env

AI\_PROVIDER=ollama

SEARCH\_PROVIDER=tavily



TAVILY\_API\_KEY=your\_tavily\_api\_key



OLLAMA\_BASE\_URL=http://localhost:11434

OLLAMA\_MODEL=mistral

```



Run the backend:



```bash

uvicorn main:app --reload

```



The backend runs at:



```text

http://127.0.0.1:8000

```



API documentation:



```text

http://127.0.0.1:8000/docs

```



\### Frontend Setup



Open a second terminal:



```bash

cd frontend

npm install

npm run dev

```



The frontend runs at:



```text

http://localhost:5173

```



\## API Example



\### Request



```json

{

&#x20; "message": "Who is the president of France?",

&#x20; "conversation\_id": "example-conversation-id"

}

```



\### Response



```json

{

&#x20; "answer": "Emmanuel Macron is the President of France.",

&#x20; "source": "web\_search\_fallback",

&#x20; "sources": \[

&#x20;   {

&#x20;     "title": "Write to the President - Élysée",

&#x20;     "url": "https://www.elysee.fr/en/contact"

&#x20;   }

&#x20; ]

}

```



\## Time Complexity Notes



The project documents time complexity in major functions.



| Feature                       | Complexity   |

| ----------------------------- | ------------ |

| Casual conversation matching  | O(l)         |

| Knowledge-base lookup         | O(n × k)     |

| Conversation-memory retrieval | O(log n + h) |

| Source formatting             | O(r)         |

| Frontend message rendering    | O(m)         |

| Source-link rendering         | O(s)         |



Where:



\* `l` = message length

\* `n` = number of knowledge-base records

\* `k` = average keywords per record

\* `h` = recent history length

\* `r` = web-search result count

\* `m` = message count in the current chat

\* `s` = source-link count



\## Security



\* API keys are stored in `.env` and are excluded from Git using `.gitignore`.

\* `.env.example` contains placeholders only.

\* The local SQLite database and saved chat history are excluded from Git.

\* No Tavily key, local model files, or user chat records should be committed.



\## Roadmap



\* \[x] FastAPI backend

\* \[x] React chat interface

\* \[x] Local knowledge base

\* \[x] Tavily web-search fallback

\* \[x] Ollama local model integration

\* \[x] Source links

\* \[x] Basic casual conversation routing

\* \[ ] Complete and test persistent SQLite memory

\* \[ ] New-chat button and multiple saved conversations

\* \[ ] Better follow-up and pronoun resolution

\* \[ ] Provider switching: Mock, Ollama, OpenAI, Gemini

\* \[ ] Automated tests

\* \[ ] Docker support

\* \[ ] GitHub Actions CI

\* \[ ] Deployment guide



\## Author



Created by \*\*Adesoji Abdulrahmon\*\* as an open-source AI engineering portfolio project.



