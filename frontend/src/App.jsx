import { useEffect, useState } from "react";
import "./index.css";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const CONVERSATION_STORAGE_KEY =
  "intellectual-assistant-conversation-id";

const welcomeMessage = {
  role: "assistant",
  content:
    "Hello, I am Intellectual Assistant. Ask me anything, and I will check my knowledge base or search the web when needed.",
  sources: [],
  sourceType: "system",
};

function createConversationId() {
  if (window.crypto?.randomUUID) {
    return window.crypto.randomUUID();
  }

  return `conversation-${Date.now()}-${Math.random()
    .toString(16)
    .slice(2)}`;
}

function getOrCreateConversationId() {
  const existingId = window.localStorage.getItem(
    CONVERSATION_STORAGE_KEY
  );

  if (existingId) {
    return existingId;
  }

  const newId = createConversationId();

  window.localStorage.setItem(
    CONVERSATION_STORAGE_KEY,
    newId
  );

  return newId;
}

function App() {
  const [conversationId] = useState(() => getOrCreateConversationId());

  const [messages, setMessages] = useState([welcomeMessage]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isRestoring, setIsRestoring] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let isMounted = true;

    async function restoreSavedConversation() {
      try {
        const response = await fetch(
          `${API_BASE_URL}/conversations/${conversationId}/messages`
        );

        if (!response.ok) {
          throw new Error(
            `Conversation restore failed with status ${response.status}`
          );
        }

        const storedMessages = await response.json();

        if (isMounted && storedMessages.length > 0) {
          setMessages(
            storedMessages.map((message) => ({
              role: message.role,
              content: message.content,
              sources: message.sources || [],
              sourceType:
                message.source ||
                (message.role === "user" ? "user" : "assistant"),
            }))
          );
        }
      } catch (restoreError) {
        console.error(restoreError);

        if (isMounted) {
          setError(
            "Your saved chat could not be restored. You can still start a new conversation."
          );
        }
      } finally {
        if (isMounted) {
          setIsRestoring(false);
        }
      }
    }

    restoreSavedConversation();

    return () => {
      isMounted = false;
    };
  }, [conversationId]);

  async function handleSubmit(event) {
    event.preventDefault();

    const trimmedMessage = input.trim();

    if (!trimmedMessage || isLoading || isRestoring) {
      return;
    }

    const userMessage = {
      role: "user",
      content: trimmedMessage,
      sources: [],
      sourceType: "user",
    };

    setMessages((currentMessages) => [
      ...currentMessages,
      userMessage,
    ]);

    setInput("");
    setError("");
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: trimmedMessage,
          conversation_id: conversationId,
        }),
      });

      if (!response.ok) {
        throw new Error(
          `Request failed with status ${response.status}`
        );
      }

      const data = await response.json();

      const assistantMessage = {
        role: "assistant",
        content: data.answer || "I could not generate a response.",
        sources: data.sources || [],
        sourceType: data.source || "assistant",
      };

      setMessages((currentMessages) => [
        ...currentMessages,
        assistantMessage,
      ]);
    } catch (requestError) {
      console.error(requestError);

      setError(
        "I could not connect to the backend. Confirm that FastAPI is running on port 8000."
      );
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <section className="chat-card">
        <header className="app-header">
          <div>
            <p className="eyebrow">OPEN-SOURCE AI ASSISTANT</p>
            <h1>Intellectual Assistant</h1>
            <p className="subtitle">
              Persistent memory · Knowledge base · Web-search fallback
            </p>
          </div>

          <span className="status-badge">
            <span className="status-dot" />
            Online
          </span>
        </header>

        <section className="messages" aria-live="polite">
          {isRestoring && (
            <article className="message-row assistant">
              <div className="message-avatar">IA</div>

              <div className="message-content loading-message">
                <div className="message-label">
                  Intellectual Assistant
                </div>
                <p>Restoring saved conversation...</p>
              </div>
            </article>
          )}

          {!isRestoring &&
            messages.map((message, index) => (
              <article
                className={`message-row ${message.role}`}
                key={`${message.role}-${index}`}
              >
                <div className="message-avatar">
                  {message.role === "user" ? "U" : "IA"}
                </div>

                <div className="message-content">
                  <div className="message-label">
                    {message.role === "user"
                      ? "You"
                      : "Intellectual Assistant"}
                  </div>

                  <p>{message.content}</p>

                  {message.role === "assistant" &&
                    message.sourceType !== "system" && (
                      <small className="answer-type">
                        Answer source:{" "}
                        {message.sourceType.replaceAll("_", " ")}
                      </small>
                    )}

                  {message.sources?.length > 0 && (
                    <div className="sources">
                      <strong>Sources</strong>

                      <div className="source-list">
                        {message.sources.map(
                          (source, sourceIndex) => (
                            <a
                              className="source-link"
                              href={source.url}
                              key={`${source.url}-${sourceIndex}`}
                              target="_blank"
                              rel="noreferrer"
                            >
                              <span>{sourceIndex + 1}</span>
                              {source.title || "Untitled source"}
                            </a>
                          )
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </article>
            ))}

          {isLoading && (
            <article className="message-row assistant">
              <div className="message-avatar">IA</div>

              <div className="message-content loading-message">
                <div className="message-label">
                  Intellectual Assistant
                </div>
                <p>
                  Thinking
                  <span className="loading-dots">...</span>
                </p>
              </div>
            </article>
          )}
        </section>

        {error && <p className="error-message">{error}</p>}

        <form className="chat-form" onSubmit={handleSubmit}>
          <input
            type="text"
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Ask Intellectual Assistant anything..."
            disabled={isLoading || isRestoring}
            aria-label="Your message"
          />

          <button
            type="submit"
            disabled={
              isLoading ||
              isRestoring ||
              !input.trim()
            }
          >
            Send
          </button>
        </form>

        <footer>
          SQLite conversation memory · Local knowledge base · Tavily web
          search · Ollama response generation
        </footer>
      </section>
    </main>
  );
}

export default App;

/*
Time Complexity Notes:
- Rendering visible messages: O(m), where m is the message count.
- Restoring a conversation: O(m + s), where s is stored source links.
- Sending a message: O(1) frontend request setup.
- Persistent memory lookup is handled by the backend with indexed SQLite queries.
*/
