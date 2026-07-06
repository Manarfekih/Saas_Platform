import { useEffect, useRef, useState } from "react";
import api from "../api/auth";
import { useAuth } from "../context/AuthContext";
import StructuredAnswerView from "./StructuredAnswerView";
import type { StructuredAnswer } from "./chatTypes";

type Message = {
  role: "user" | "assistant";
  content: string | StructuredAnswer;
};

function isStructuredAnswer(
  content: string | StructuredAnswer
): content is StructuredAnswer {
  return typeof content === "object" && content !== null && "type" in content;
}

export default function GlobalChatPage() {
  const { token } = useAuth();

  const [sessionId, setSessionId] = useState<number | null>(null);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    let cancelled = false;

    async function initSession() {
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        setHistoryLoading(true);
        setError(null);

        const sessionRes = await api.get("/chat/all/session", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (cancelled) {
          return;
        }

        const nextSessionId = sessionRes.data.session_id as number;
        setSessionId(nextSessionId);

        const historyRes = await api.get("/chat/all/history", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
          params: {
            session_id: nextSessionId,
          },
        });

        if (cancelled) {
          return;
        }

        setMessages(
          (historyRes.data.messages ?? []).map((message: Message) => ({
            role: message.role,
            content: message.content,
          }))
        );
      } catch (err) {
        console.error("Failed to initialize global chat", err);

        if (!cancelled) {
          setError("We could not start the global chat right now.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
          setHistoryLoading(false);
        }
      }
    }

    initSession();

    return () => {
      cancelled = true;
    };
  }, [token]);

  async function sendMessage() {
    if (!question.trim() || !sessionId || sending) return;

    const current = question.trim();

    setMessages((prev) => [...prev, { role: "user", content: current }]);
    setQuestion("");
    setSending(true);

    try {
      const res = await api.post(
        "/chat/global",
        {
          session_id: sessionId,
          question: current,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const answer = res.data.answer as StructuredAnswer | undefined;

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            answer && typeof answer === "object" && "type" in answer
              ? answer
              : {
                  type: "fact",
                  text: res.data.answer?.text || "No response",
                },
        },
      ]);
    } catch (err) {
      console.error(err);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: {
            type: "fact",
            text: "Something went wrong.",
          },
        },
      ]);
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="max-w-5xl mx-auto">
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm h-[75vh] flex flex-col">
        <div className="px-6 py-4 border-b border-slate-100">
          <h1 className="font-bold text-slate-900">Knowledge Base Chat</h1>
          <p className="text-xs text-slate-400">Ask anything across all your documents</p>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {loading && (
            <p className="text-slate-400 text-center mt-10">Initializing chat...</p>
          )}

          {error && !loading && (
            <div className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
              {error}
            </div>
          )}

          {historyLoading && !loading && (
            <p className="text-slate-400 text-center mt-10">
              Loading previous conversation...
            </p>
          )}

          {messages.length === 0 && !loading && !historyLoading && !error && (
            <p className="text-slate-400 text-center mt-10">
              Ask a question across your knowledge base
            </p>
          )}

          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`px-4 py-3 rounded-2xl max-w-2xl whitespace-pre-wrap ${
                  msg.role === "user"
                    ? "bg-indigo-600 text-white"
                    : "bg-slate-100 text-slate-800"
                }`}
              >
                {isStructuredAnswer(msg.content) ? (
                  <StructuredAnswerView answer={msg.content} />
                ) : (
                  <span className="whitespace-pre-wrap">{msg.content}</span>
                )}
              </div>
            </div>
          ))}

          {sending && <div className="text-slate-400 text-sm">Thinking...</div>}

          <div ref={bottomRef} />
        </div>

        <div className="border-t border-slate-100 p-4 flex gap-3">
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") sendMessage();
            }}
            placeholder="Ask across all documents..."
            className="flex-1 border border-slate-200 rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-indigo-500"
            disabled={!sessionId || sending || loading}
          />

          <button
            onClick={sendMessage}
            disabled={!sessionId || sending || loading}
            className="bg-indigo-600 text-white px-6 rounded-xl font-semibold disabled:opacity-50"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
