"use client";

import * as React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Send, Sparkles, Loader2, AlertTriangle, ShieldAlert, MessageCircle, Clock } from "lucide-react";

import { api } from "@/lib/api";
import { Input } from "@/components/ui/input";
import { Button as UIButton } from "@/components/ui/button";
import { useToast } from "@/components/ui/toast";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

interface Conversation {
  id: string;
  created_at: string;
  messages: Message[];
}

export default function AssistantPage() {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [message, setMessage] = React.useState("");
  const [activeConversationId, setActiveConversationId] = React.useState<string | null>(null);
  const [providerStatus, setProviderStatus] = React.useState<string | null>(null);
  const [disclaimer, setDisclaimer] = React.useState<string | null>(null);

  const messageEndRef = React.useRef<HTMLDivElement>(null);

  // Fetch list of conversations
  const { data: conversations = [], isLoading: listsLoading } = useQuery<Conversation[]>({
    queryKey: ["conversations"],
    queryFn: async () => {
      const response = await api.get("/assistant/conversations");
      return response.data;
    },
  });

  // Fetch details of active conversation (messages)
  const { data: activeConvo } = useQuery<Conversation>({
    queryKey: ["conversation", activeConversationId],
    queryFn: async () => {
      const response = await api.get(`/assistant/conversations/${activeConversationId}`);
      return response.data;
    },
    enabled: activeConversationId !== null,
  });

  // Automatically scroll to bottom when messages load/update
  React.useEffect(() => {
    messageEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [activeConvo?.messages]);

  // Send message mutation
  const chatMutation = useMutation({
    mutationFn: async (payload: { message: string; conversation_id?: string | null }) => {
      const response = await api.post("/assistant/chat", payload);
      return response.data;
    },
    onSuccess: (data) => {
      setMessage("");
      setProviderStatus(data.provider_status);
      setDisclaimer(data.disclaimer);
      
      // Update active conversation context and query caches
      if (!activeConversationId) {
        setActiveConversationId(data.conversation_id);
      }
      queryClient.invalidateQueries({ queryKey: ["conversations"] });
      queryClient.invalidateQueries({ queryKey: ["conversation", data.conversation_id] });
    },
    onError: (err: unknown) => {
      const errMsg = (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || "AI Chat submission failed.";
      toast({
        title: "Chat Error",
        description: errMsg,
        variant: "destructive",
      });
    },
  });

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim().length === 0) return;
    chatMutation.mutate({
      message: message.trim(),
      conversation_id: activeConversationId,
    });
  };

  const handleNewConversation = () => {
    setActiveConversationId(null);
    setProviderStatus(null);
    setDisclaimer(null);
  };

  const messages = activeConvo?.messages || [];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 h-[calc(100vh-140px)] flex flex-col md:flex-row gap-6">
      {/* Sidebar - Conversation list */}
      <div className="w-full md:w-64 shrink-0 flex flex-col h-1/3 md:h-full border border-secondary/20 bg-secondary/5 rounded-2xl p-4 shadow-sm">
        <UIButton
          onClick={handleNewConversation}
          variant="outline"
          className="font-bold w-full justify-start gap-2 mb-4 text-xs py-5"
        >
          <Sparkles className="h-4 w-4 text-primary" /> New Conversation
        </UIButton>

        <div className="text-[10px] text-muted-foreground font-extrabold uppercase tracking-wider mb-2 flex items-center gap-1.5 pl-1">
          <Clock className="h-3.5 w-3.5" /> Recent Chats
        </div>

        <div className="flex-grow overflow-y-auto space-y-1 pr-1">
          {listsLoading ? (
            <div className="flex justify-center py-6">
              <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
            </div>
          ) : conversations.length === 0 ? (
            <div className="text-center py-8 text-xs text-muted-foreground italic">
              No chat history.
            </div>
          ) : (
            conversations.map((c) => {
              const lastMsg = c.messages?.[c.messages.length - 1]?.content || "Empty chat";
              const isActive = activeConversationId === c.id;
              return (
                <button
                  key={c.id}
                  onClick={() => setActiveConversationId(c.id)}
                  className={`w-full text-left p-3 rounded-xl text-xs font-medium border transition-colors flex flex-col gap-1 ${
                    isActive
                      ? "bg-primary/10 text-primary border-primary/20"
                      : "bg-background border-muted/30 text-foreground hover:bg-secondary/10"
                  }`}
                >
                  <span className="font-bold flex items-center gap-1">
                    <MessageCircle className="h-3 w-3" />
                    Chat session
                  </span>
                  <span className="line-clamp-1 text-muted-foreground text-[10px]">
                    {lastMsg}
                  </span>
                </button>
              );
            })
          )}
        </div>
      </div>

      {/* Main chat log viewport */}
      <div className="flex-grow flex flex-col h-2/3 md:h-full border border-secondary/20 rounded-2xl bg-background shadow-md overflow-hidden">
        {/* Top Header info */}
        <div className="p-4 border-b border-muted flex justify-between items-center bg-primary/5">
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary animate-pulse" />
            <div>
              <h2 className="text-sm font-extrabold text-foreground">AI Agriculture Advisor</h2>
              <p className="text-[10px] text-muted-foreground">Ask questions on soil chemistry, pesticide usage limits, or planting guides.</p>
            </div>
          </div>
          {providerStatus === "demo" && (
            <span className="bg-amber-100 text-amber-800 dark:bg-amber-950/40 dark:text-amber-400 text-[9px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1 border border-amber-200">
              <AlertTriangle className="h-3 w-3" /> Demo Mode
            </span>
          )}
        </div>

        {/* Warning card for baseline demo fallback */}
        {providerStatus === "demo" && (
          <div className="p-3 bg-amber-50 text-amber-900 border-b border-amber-200 text-xs font-semibold flex items-start gap-2">
            <span className="shrink-0 mt-0.5 text-base">⚠️</span>
            <div>
              <p className="font-bold text-amber-950">AI Provider Key Not Configured</p>
              <p className="text-[10px] text-amber-800 font-medium mt-0.5">Running in rule-based baseline mock mode. Provide a valid Gemini/OpenAI API key to enable live LLM replies.</p>
            </div>
          </div>
        )}

        {/* Messages list */}
        <div className="flex-grow overflow-y-auto p-4 space-y-4 bg-slate-50/35">
          {messages.length === 0 && !chatMutation.isPending ? (
            <div className="h-full flex flex-col items-center justify-center text-center p-6 space-y-3">
              <Sparkles className="h-10 w-10 text-muted/40 mx-auto" />
              <h3 className="font-bold text-foreground">Consult AgroGuide Advisor</h3>
              <p className="text-xs text-muted-foreground max-w-sm mx-auto leading-relaxed">
                Type your agricultural questions below. Our model can assist with crop disease identifiers, fertilizer balance formulas, or market trends.
              </p>
            </div>
          ) : (
            <>
              {messages.map((msg) => {
                const isAssistant = msg.role === "assistant";
                return (
                  <div
                    key={msg.id}
                    className={`flex ${isAssistant ? "justify-start" : "justify-end"}`}
                  >
                    <div
                      className={`max-w-[80%] rounded-2xl p-4 text-xs leading-relaxed shadow-sm border ${
                        isAssistant
                          ? "bg-background text-foreground border-secondary/20 rounded-tl-none"
                          : "bg-primary text-primary-content border-primary/20 rounded-tr-none"
                      }`}
                    >
                      <div className="font-bold text-[10px] mb-1 opacity-70 uppercase tracking-wider">
                        {isAssistant ? "AgroGuide Assistant" : "You"}
                      </div>
                      <div className="whitespace-pre-wrap">{msg.content}</div>
                    </div>
                  </div>
                );
              })}
              
              {chatMutation.isPending && (
                <div className="flex justify-start">
                  <div className="max-w-[80%] rounded-2xl p-4 bg-background border border-secondary/20 rounded-tl-none shadow-sm flex items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin text-primary" />
                    <span className="text-xs text-muted-foreground font-semibold">Consulting agricultural data models...</span>
                  </div>
                </div>
              )}
              
              <div ref={messageEndRef} />
            </>
          )}
        </div>

        {/* Disclaimer / Safety notice */}
        {disclaimer && (
          <div className="p-3 bg-red-50/50 border-t border-red-200/50 text-[10px] text-red-800 font-medium flex gap-2 items-start">
            <ShieldAlert className="h-4 w-4 text-red-700 shrink-0 mt-0.5" />
            <div>
              <strong className="text-red-950 uppercase text-[8px] tracking-wider block mb-0.5">⚠️ Safety Disclaimer:</strong>
              {disclaimer}
            </div>
          </div>
        )}

        {/* Input Form footer */}
        <form onSubmit={handleSend} className="p-4 border-t border-muted bg-background flex gap-2 items-center">
          <Input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Type your message..."
            disabled={chatMutation.isPending}
            className="flex-grow py-5"
          />
          <UIButton
            type="submit"
            disabled={chatMutation.isPending || message.trim().length === 0}
            className="font-bold flex items-center justify-center p-3 h-10 w-10 shrink-0"
          >
            <Send className="h-4 w-4" />
          </UIButton>
        </form>
      </div>
    </div>
  );
}
