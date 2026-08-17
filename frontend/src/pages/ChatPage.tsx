// src/pages/ChatPage.tsx

import { useEffect, useRef, useState } from "react";
import { useParams, useLocation } from "react-router-dom";
import api from "../api/auth";
import { useAuth } from "../context/AuthContext";
import StructuredAnswerView from "./StructuredAnswerView";
import CitationSources from "../components/chat/CitationSources";
import type { Message, StructuredAnswer } from "./chatTypes";

export default function ChatPage() {
  const { token } = useAuth();
  const { document_id } = useParams();
  const location = useLocation();

  const [sessionId, setSessionId] = useState<number | null>(
    location.state?.session_id ?? null
  );
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [sending, setSending] = useState(false);
  const [historyError, setHistoryError] = useState<string | null>(null);

  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    if (!token || !document_id) return;

    let cancelled = false;

    async function loadChatHistory() {
      setLoadingHistory(true);
      setHistoryError(null);

      try {
        const res = await api.get(`/documents/${document_id}/chat-history`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (cancelled) return;

        setSessionId(res.data.session_id);
        setMessages(
          (res.data.messages ?? []).map((message: Message) => ({
            role: message.role,
            content: message.content,
          }))
        );
      } catch (error) {
        console.error(error);
        if (!cancelled) {
          setHistoryError("We could not load the chat history for this document.");
        }
      } finally {
        if (!cancelled) setLoadingHistory(false);
      }
    }

    loadChatHistory();
    return () => { cancelled = true; };
  }, [token, document_id]);

  function isStructuredAnswer(
    content: string | StructuredAnswer
  ): content is StructuredAnswer {
    return typeof content === "object" && content !== null && "type" in content;
  }

  async function sendMessage() {
    if (!question.trim() || !sessionId || !document_id || !token || sending) return;

    const currentQuestion = question.trim();

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: currentQuestion,
      },
    ]);

    setQuestion("");
    setSending(true);

    try {
      const res = await api.post(
        `/documents/${document_id}/chat`,
        {
          session_id: sessionId,
          question: currentQuestion,
        },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      const answer = res.data?.answer;
      const sourceData = res.data?.sources || [];

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            answer && typeof answer === "object" && "type" in answer
              ? (answer as StructuredAnswer)
              : {
                  type: "fact",
                  text: "I could not generate a readable answer from this document.",
                },
          sources: sourceData,
        },
      ]);
    } catch (error) {
      console.error(error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, something went wrong.",
        },
      ]);
    } finally {
      setSending(false);
    }
  }

  if (historyError && !sessionId && !loadingHistory) {
    return (
      <div className="max-w-5xl mx-auto">
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8 text-center">
          <h2 className="text-xl font-bold text-slate-800">Chat Session Not Found</h2>
          <p className="mt-2 text-slate-500">Please open the chat from the document page.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto">
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm h-[75vh] flex flex-col">
        <div className="px-6 py-4 border-b border-slate-100">
          <h1 className="font-bold text-slate-900">AI Document Chat</h1>
          <p className="text-xs text-slate-400">Ask questions about your document</p>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-5">
          {loadingHistory && (
            <div className="text-center text-slate-400 mt-20">
              <p>Loading previous chat...</p>
            </div>
          )}

          {historyError && !loadingHistory && (
            <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
              {historyError}
            </div>
          )}

          {!loadingHistory && messages.length === 0 && !historyError && (
            <div className="text-center text-slate-400 mt-20">
              <p>Start asking questions about your document.</p>
            </div>
          )}


              {messages.map((message, index) => (
                <div key={index} className="space-y-2">
                  <div
                    className={message.role === "user" ? "flex justify-end" : "flex justify-start"}
                  >
                    <div
                      className={
                        message.role === "user"
                          ? "bg-indigo-600 text-white px-4 py-3 rounded-2xl max-w-xl whitespace-pre-wrap break-words"
                          : "bg-slate-100 text-slate-800 px-4 py-3 rounded-2xl max-w-2xl break-words"
                      }
                    >
                      {isStructuredAnswer(message.content) ? (
                        <StructuredAnswerView answer={message.content} />
                      ) : (
                        <span className="whitespace-pre-wrap">{message.content}</span>
                      )}
                    </div>
                  </div>

                  {/* Show citations for assistant messages with sources */}
                  {message.role === "assistant" && message.sources && message.sources.length > 0 && (
                    <div className="ml-4 mt-2">
                      <CitationSources sources={message.sources} documentId={document_id ? Number(document_id) : undefined} />
                    </div>
                  )}
                </div>
              ))}
          {sending && (
            <div className="flex justify-start">
              <div className="bg-slate-100 px-4 py-3 rounded-2xl text-sm text-slate-500">
                Thinking...
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        <div className="border-t border-slate-100 p-4 flex gap-3">
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") sendMessage();
            }}
            placeholder="Ask something about your document..."
            className="flex-1 border border-slate-200 rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-indigo-500"
            disabled={loadingHistory || sending || !sessionId}
          />
          <button
            onClick={sendMessage}
            disabled={loadingHistory || sending || !sessionId}
            className="bg-indigo-600 text-white px-6 rounded-xl font-semibold disabled:opacity-50 hover:bg-indigo-700 transition-colors"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}







