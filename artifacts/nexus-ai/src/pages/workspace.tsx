import { FormEvent, useEffect, useMemo, useRef, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { Link } from 'wouter';
import {
  ArrowUp,
  ChevronRight,
  Clock3,
  Command,
  CornerDownLeft,
  FileText,
  LoaderCircle,
  MessageSquareText,
  PanelLeft,
  Plus,
  Sparkles,
  WandSparkles,
} from 'lucide-react';
import {
  getGetConversationQueryKey,
  getListConversationsQueryKey,
  useGetConversation,
  useListConversations,
  useSendChatMessage,
} from '@workspace/api-client-react';
import { NexusShell } from '@/components/nexus-shell';

type OptimisticMessage = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  createdAt: string;
};

function formatRelativeDate(dateString: string) {
  const date = new Date(dateString);
  if (Number.isNaN(date.getTime())) return 'recently';
  const seconds = Math.max(0, Math.floor((Date.now() - date.getTime()) / 1000));
  if (seconds < 60) return 'just now';
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
  return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
}

function ConversationSkeleton() {
  return (
    <div className="space-y-2 px-1" aria-label="Loading conversations">
      {[1, 2, 3, 4].map((item) => (
        <div key={item} className="animate-pulse rounded-xl border border-border/70 p-3">
          <div className="h-3 w-3/4 rounded bg-secondary" />
          <div className="mt-2 h-2.5 w-full rounded bg-secondary/80" />
          <div className="mt-2 h-2.5 w-1/3 rounded bg-secondary/60" />
        </div>
      ))}
    </div>
  );
}

function ThreadMessage({ message }: { message: OptimisticMessage }) {
  const isUser = message.role === 'user';
  return (
    <div className={`appear flex gap-3.5 ${isUser ? 'justify-end' : 'justify-start'}`} data-testid={`message-${message.id}`}>
      {!isUser && (
        <span className="mt-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          <Sparkles size={14} />
        </span>
      )}
      <div className={`max-w-[min(680px,88%)] ${isUser ? 'items-end' : 'items-start'}`}>
        <div
          className={`whitespace-pre-wrap text-[14px] leading-7 ${
            isUser
              ? 'rounded-2xl rounded-tr-md bg-primary px-4 py-3 text-primary-foreground shadow-[0_8px_20px_hsl(var(--primary)/.13)]'
              : 'rounded-2xl rounded-tl-md border border-border/80 bg-card/80 px-4 py-3.5 text-foreground shadow-sm'
          }`}
        >
          {message.content}
        </div>
        <div className={`mt-1.5 flex items-center gap-1 font-mono-ui text-[10px] uppercase tracking-[.1em] text-muted-foreground ${isUser ? 'justify-end' : ''}`}>
          {isUser ? 'you' : 'nexus'} <span className="opacity-50">·</span> {formatRelativeDate(message.createdAt)}
        </div>
      </div>
    </div>
  );
}

function ThreadLoading() {
  return (
    <div className="flex gap-3.5" aria-label="Loading conversation">
      <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground">
        <Sparkles size={14} />
      </span>
      <div className="rounded-2xl rounded-tl-md border border-border/80 bg-card/80 px-5 py-4 shadow-sm">
        <div className="flex items-center gap-1.5">
          <span className="thinking-dot h-1.5 w-1.5 rounded-full bg-primary" />
          <span className="thinking-dot h-1.5 w-1.5 rounded-full bg-primary" />
          <span className="thinking-dot h-1.5 w-1.5 rounded-full bg-primary" />
        </div>
      </div>
    </div>
  );
}

function EmptyWorkspace({ onPrompt }: { onPrompt: (value: string) => void }) {
  const suggestions = ['Help me untangle a difficult decision', 'Turn a rough idea into a clear plan', 'Explain something I keep avoiding'];
  return (
    <div className="flex min-h-[calc(100dvh-17rem)] flex-col items-center justify-center px-5 py-14 text-center">
      <div className="relative mb-7 flex h-16 w-16 items-center justify-center rounded-[21px] border border-primary/15 bg-primary text-primary-foreground shadow-[0_12px_28px_hsl(var(--primary)/.18)]">
        <WandSparkles size={25} strokeWidth={1.6} />
        <span className="absolute -right-1 -top-1 h-3 w-3 rounded-full bg-accent" />
      </div>
      <p className="font-mono-ui text-[10px] uppercase tracking-[.2em] text-primary">A quiet place to think</p>
      <h2 className="mt-3 max-w-md font-display text-3xl font-semibold tracking-[-.045em] text-balance sm:text-4xl">What are we working through today?</h2>
      <p className="mt-4 max-w-md text-sm leading-6 text-muted-foreground">
        Start with a question, a half-formed thought, or a problem that needs room. Nexus will meet you there.
      </p>
      <div className="mt-8 flex max-w-lg flex-wrap justify-center gap-2">
        {suggestions.map((suggestion, index) => (
          <button
            key={suggestion}
            type="button"
            onClick={() => onPrompt(suggestion)}
            data-testid={`button-suggestion-${index}`}
            className="rounded-full border border-border bg-card/70 px-3.5 py-2 text-xs text-muted-foreground transition hover:-translate-y-0.5 hover:border-primary/35 hover:text-foreground"
          >
            {suggestion}
          </button>
        ))}
      </div>
    </div>
  );
}

export default function Workspace() {
  const queryClient = useQueryClient();
  const conversationsQuery = useListConversations();
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [mobileRecentOpen, setMobileRecentOpen] = useState(false);
  const [composer, setComposer] = useState('');
  const [optimisticMessages, setOptimisticMessages] = useState<OptimisticMessage[]>([]);
  const composerRef = useRef<HTMLTextAreaElement>(null);
  const conversations = useMemo(() => conversationsQuery.data ?? [], [conversationsQuery.data]);
  const activeId = selectedId ?? '';
  const conversationQuery = useGetConversation(activeId, {
    query: { enabled: Boolean(activeId), queryKey: getGetConversationQueryKey(activeId) },
  });
  const sendMessage = useSendChatMessage();
  const activeConversation = conversationQuery.data;

  useEffect(() => {
    if (!selectedId && conversations.length > 0) setSelectedId(conversations[0].id);
  }, [conversations, selectedId]);

  const messages = useMemo(() => {
    if (activeConversation?.messages) return activeConversation.messages as OptimisticMessage[];
    return optimisticMessages;
  }, [activeConversation, optimisticMessages]);

  const setPrompt = (value: string) => {
    setComposer(value);
    window.setTimeout(() => composerRef.current?.focus(), 0);
  };

  const submitPrompt = (event?: FormEvent) => {
    event?.preventDefault();
    const prompt = composer.trim();
    if (!prompt || sendMessage.isPending) return;
    const temporaryId = `pending-${Date.now()}`;
    setOptimisticMessages((current) => [
      ...current,
      { id: temporaryId, role: 'user', content: prompt, createdAt: new Date().toISOString() },
    ]);
    setComposer('');
    sendMessage.mutate(
      { data: { conversationId: selectedId, prompt } },
      {
        onSuccess: (result) => {
          setSelectedId(result.conversation.id);
          setOptimisticMessages([]);
          queryClient.setQueryData(getGetConversationQueryKey(result.conversation.id), result.conversation);
          queryClient.invalidateQueries({ queryKey: getListConversationsQueryKey() });
        },
        onError: () => {
          setComposer(prompt);
        },
      },
    );
  };

  const startNewChat = () => {
    setSelectedId(null);
    setOptimisticMessages([]);
    setComposer('');
    setMobileRecentOpen(false);
    window.setTimeout(() => composerRef.current?.focus(), 0);
  };

  return (
    <NexusShell onNewChat={startNewChat}>
      <div className="flex min-h-[100dvh] flex-col">
        <header className="flex h-[76px] shrink-0 items-center justify-between border-b border-border/70 px-5 pl-[68px] md:px-10 md:pl-10">
          <div className="min-w-0">
            <p className="font-mono-ui text-[10px] uppercase tracking-[.2em] text-muted-foreground">Nexus workspace</p>
            <h1 className="mt-1 truncate font-display text-lg font-semibold tracking-[-.035em]">
              {activeConversation?.title || (selectedId ? 'Opening conversation' : 'New conversation')}
            </h1>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setMobileRecentOpen((value) => !value)}
              aria-label="Toggle recent conversations"
              data-testid="button-toggle-recent"
              className="rounded-xl border border-border bg-card/60 p-2.5 text-muted-foreground transition hover:bg-secondary hover:text-foreground md:hidden"
            >
              <PanelLeft size={17} />
            </button>
            <Link
              href="/settings"
              data-testid="link-header-settings"
              className="hidden items-center gap-2 rounded-xl border border-border bg-card/60 px-3 py-2 text-xs font-medium text-muted-foreground transition hover:bg-secondary hover:text-foreground sm:flex"
            >
              Preferences <ChevronRight size={14} />
            </Link>
          </div>
        </header>

        <div className="relative flex min-h-0 flex-1 flex-col md:flex-row">
          <aside className={`absolute inset-x-0 top-0 z-20 border-b border-border bg-[hsl(var(--card)/.98)] px-4 py-4 shadow-lg md:static md:block md:h-auto md:w-[314px] md:shrink-0 md:border-b-0 md:border-r md:bg-card/30 md:px-5 md:py-7 md:shadow-none ${mobileRecentOpen ? 'block' : 'hidden'}`}>
            <div className="mb-4 flex items-center justify-between px-1">
              <div>
                <p className="font-mono-ui text-[10px] uppercase tracking-[.18em] text-muted-foreground">Your thinking</p>
                <p className="mt-1 text-xs text-muted-foreground">Recent conversations</p>
              </div>
              <button
                type="button"
                onClick={startNewChat}
                data-testid="button-sidebar-new-chat"
                className="rounded-lg p-2 text-primary transition hover:bg-secondary"
                aria-label="Start a new conversation"
              >
                <Plus size={17} />
              </button>
            </div>
            {conversationsQuery.isPending ? <ConversationSkeleton /> : conversationsQuery.isError ? (
              <div className="rounded-xl border border-destructive/20 bg-destructive/5 p-4 text-xs leading-5 text-destructive" data-testid="status-conversations-error">
                Recent conversations could not be loaded. <button type="button" onClick={() => conversationsQuery.refetch()} className="font-semibold underline" data-testid="button-retry-conversations">Try again</button>
              </div>
            ) : conversations.length === 0 ? (
              <div className="rounded-xl border border-dashed border-border p-4 text-center" data-testid="empty-conversations">
                <MessageSquareText className="mx-auto text-muted-foreground" size={19} />
                <p className="mt-2 text-xs font-semibold">Your first thought is waiting</p>
                <p className="mt-1 text-[11px] leading-4 text-muted-foreground">New conversations will settle here.</p>
              </div>
            ) : (
              <div className="scroll-thin max-h-[calc(100dvh-180px)] space-y-1 overflow-y-auto">
                {conversations.map((conversation) => (
                  <button
                    type="button"
                    key={conversation.id}
                    onClick={() => { setSelectedId(conversation.id); setOptimisticMessages([]); setMobileRecentOpen(false); }}
                    data-testid={`button-conversation-${conversation.id}`}
                    className={`group w-full rounded-xl border px-3 py-3 text-left transition ${
                      selectedId === conversation.id
                        ? 'border-primary/15 bg-secondary shadow-sm'
                        : 'border-transparent hover:border-border hover:bg-card/70'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <span className="line-clamp-1 text-[13px] font-semibold">{conversation.title}</span>
                      <span className="shrink-0 pt-0.5 font-mono-ui text-[9px] text-muted-foreground">{formatRelativeDate(conversation.updatedAt)}</span>
                    </div>
                    <p className="mt-1 line-clamp-2 text-[11px] leading-4 text-muted-foreground">{conversation.preview || 'No preview yet'}</p>
                    <div className="mt-2 flex items-center gap-1.5 font-mono-ui text-[9px] uppercase tracking-[.1em] text-muted-foreground">
                      <Clock3 size={11} /> {conversation.messageCount} messages
                    </div>
                  </button>
                ))}
              </div>
            )}
          </aside>

          <section className="flex min-w-0 flex-1 flex-col">
            <div className="scroll-thin flex-1 overflow-y-auto">
              {conversationQuery.isError ? (
                <div className="mx-auto flex min-h-[calc(100dvh-17rem)] max-w-md flex-col items-center justify-center px-5 text-center" data-testid="status-thread-error">
                  <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-destructive/10 text-destructive"><FileText size={21} /></div>
                  <h2 className="mt-4 font-display text-xl font-semibold">This thread is out of reach</h2>
                  <p className="mt-2 text-sm leading-6 text-muted-foreground">There was a problem opening the conversation. Your other thoughts are safe.</p>
                  <button type="button" onClick={() => conversationQuery.refetch()} data-testid="button-retry-thread" className="mt-5 rounded-xl bg-primary px-4 py-2.5 text-xs font-semibold text-primary-foreground transition hover:bg-[hsl(var(--primary)/.9)]">Retry opening</button>
                </div>
              ) : conversationQuery.isPending && selectedId ? (
                <div className="mx-auto flex max-w-3xl flex-col gap-7 px-5 py-10 md:px-10"><ThreadLoading /><ThreadLoading /></div>
              ) : messages.length === 0 ? (
                <EmptyWorkspace onPrompt={setPrompt} />
              ) : (
                <div className="mx-auto flex max-w-3xl flex-col gap-7 px-5 py-8 md:px-10 md:py-12">
                  <div className="mb-1 flex items-center gap-2 font-mono-ui text-[10px] uppercase tracking-[.16em] text-muted-foreground">
                    <span className="h-1.5 w-1.5 rounded-full bg-accent" /> Thread in focus
                  </div>
                  {messages.map((message) => <ThreadMessage key={message.id} message={message} />)}
                  {sendMessage.isPending && <ThreadLoading />}
                </div>
              )}
            </div>
            <div className="border-t border-border/70 bg-[hsl(var(--background)/.72)] px-4 pb-5 pt-4 backdrop-blur md:px-10 md:pb-7">
              <form onSubmit={submitPrompt} className="mx-auto max-w-3xl">
                <div className={`relative rounded-2xl border bg-card shadow-[0_12px_35px_rgba(35,60,61,.08)] transition focus-within:border-primary/45 focus-within:shadow-[0_12px_35px_hsl(var(--primary)/.12)] ${sendMessage.isError ? 'border-destructive/45' : 'border-border'}`}>
                  <textarea
                    ref={composerRef}
                    value={composer}
                    onChange={(event) => setComposer(event.target.value)}
                    onKeyDown={(event) => {
                      if (event.key === 'Enter' && !event.shiftKey && localStorage.getItem('nexus-enter-to-send') !== 'false') {
                        event.preventDefault();
                        submitPrompt(event);
                      }
                    }}
                    rows={3}
                    placeholder="Write what is on your mind..."
                    data-testid="input-prompt"
                    className="w-full resize-none bg-transparent px-4 pb-12 pt-4 text-sm leading-6 outline-none placeholder:text-muted-foreground/75"
                  />
                  <div className="absolute bottom-2.5 left-3.5 right-3.5 flex items-center justify-between">
                    <span className="hidden items-center gap-1.5 font-mono-ui text-[9px] uppercase tracking-[.1em] text-muted-foreground sm:flex"><Command size={11} /> Enter to send</span>
                    {sendMessage.isError && <span className="text-[11px] text-destructive" data-testid="status-send-error">Could not send. Try again.</span>}
                    <button
                      type="submit"
                      disabled={!composer.trim() || sendMessage.isPending}
                      data-testid="button-submit-prompt"
                      aria-label="Send prompt"
                      className="ml-auto flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground transition hover:-translate-y-0.5 hover:bg-[hsl(var(--primary)/.9)] disabled:cursor-not-allowed disabled:opacity-35 disabled:hover:translate-y-0"
                    >
                      {sendMessage.isPending ? <LoaderCircle size={15} className="animate-spin" /> : <ArrowUp size={16} />}
                    </button>
                  </div>
                </div>
                <p className="mt-2 flex items-center justify-center gap-1.5 text-center font-mono-ui text-[9px] uppercase tracking-[.08em] text-muted-foreground">
                  <CornerDownLeft size={11} /> Shift + Enter for a new line
                </p>
              </form>
            </div>
          </section>
        </div>
      </div>
    </NexusShell>
  );
}