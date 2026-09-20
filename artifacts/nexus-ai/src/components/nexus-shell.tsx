import { useEffect, useState, type ReactNode } from 'react';
import { Link, useLocation } from 'wouter';
import { Activity, BrainCircuit, Menu, Plus, Settings2, X } from 'lucide-react';
import { useHealthCheck } from '@workspace/api-client-react';

type NexusShellProps = {
  children: ReactNode;
  onNewChat?: () => void;
};

export function NexusShell({ children, onNewChat }: NexusShellProps) {
  const [location] = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);
  const health = useHealthCheck();
  const online = health.isSuccess && health.data?.status !== 'error';

  useEffect(() => {
    document.documentElement.classList.toggle('dark', localStorage.getItem('nexus-theme') === 'dark');
  }, []);

  const handleNewChat = () => {
    onNewChat?.();
    setMobileOpen(false);
  };

  return (
    <div className="noise app-shell flex min-h-[100dvh] flex-col md:flex-row">
      <button
        type="button"
        aria-label="Open navigation"
        data-testid="button-open-navigation"
        onClick={() => setMobileOpen(true)}
        className="fixed left-4 top-4 z-30 flex h-10 w-10 items-center justify-center rounded-xl border border-border bg-card/90 text-foreground shadow-sm backdrop-blur md:hidden"
      >
        <Menu size={18} />
      </button>
      {mobileOpen && (
        <button
          type="button"
          aria-label="Close navigation overlay"
          data-testid="button-close-navigation-overlay"
          onClick={() => setMobileOpen(false)}
          className="fixed inset-0 z-40 bg-foreground/20 backdrop-blur-[2px] md:hidden"
        />
      )}
      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-[286px] -translate-x-full flex-col border-r border-border bg-[hsl(var(--card)/.96)] px-5 py-6 shadow-xl backdrop-blur transition-transform duration-300 md:static md:z-auto md:translate-x-0 md:bg-card/70 md:shadow-none ${
          mobileOpen ? 'translate-x-0' : ''
        }`}
      >
        <div className="flex items-center justify-between">
          <Link
            href="/"
            onClick={() => setMobileOpen(false)}
            data-testid="link-brand-home"
            className="group flex items-center gap-3"
          >
            <span className="relative flex h-9 w-9 items-center justify-center rounded-[11px] bg-primary text-primary-foreground shadow-[0_7px_18px_hsl(var(--primary)/.2)]">
              <BrainCircuit size={19} strokeWidth={1.7} />
              <span className="absolute -right-0.5 -top-0.5 h-2 w-2 rounded-full bg-accent" />
            </span>
            <span className="font-display text-[19px] font-semibold tracking-[-.04em]">nexus</span>
          </Link>
          <button
            type="button"
            aria-label="Close navigation"
            data-testid="button-close-navigation"
            onClick={() => setMobileOpen(false)}
            className="rounded-lg p-1.5 text-muted-foreground transition hover:bg-secondary hover:text-foreground md:hidden"
          >
            <X size={17} />
          </button>
        </div>

        <button
          type="button"
          onClick={handleNewChat}
          data-testid="button-new-chat"
          className="mt-9 flex h-11 items-center justify-center gap-2 rounded-xl border border-primary/15 bg-primary px-4 text-sm font-semibold text-primary-foreground shadow-[0_8px_18px_hsl(var(--primary)/.16)] transition hover:-translate-y-0.5 hover:bg-[hsl(var(--primary)/.92)] active:translate-y-0"
        >
          <Plus size={17} />
          New conversation
        </button>

        <nav className="mt-auto space-y-1">
          <Link
            href="/"
            onClick={() => setMobileOpen(false)}
            data-testid="link-workspace"
            className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition ${
              location === '/' ? 'bg-secondary font-semibold text-foreground' : 'text-muted-foreground hover:bg-secondary/70 hover:text-foreground'
            }`}
          >
            <Activity size={16} />
            Workspace
          </Link>
          <Link
            href="/settings"
            onClick={() => setMobileOpen(false)}
            data-testid="link-settings"
            className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition ${
              location === '/settings' ? 'bg-secondary font-semibold text-foreground' : 'text-muted-foreground hover:bg-secondary/70 hover:text-foreground'
            }`}
          >
            <Settings2 size={16} />
            Settings
          </Link>
        </nav>

        <div className="mt-7 flex items-center gap-2.5 border-t border-border pt-4">
          <span className={`h-2 w-2 rounded-full ${online ? 'bg-[#5d9b72]' : health.isPending ? 'bg-accent' : 'bg-destructive'}`} />
          <span className="font-mono-ui text-[10px] uppercase tracking-[.12em] text-muted-foreground" data-testid="status-connection">
            {health.isPending ? 'Checking link' : online ? 'Systems ready' : 'Offline mode'}
          </span>
        </div>
      </aside>
      <main className="min-w-0 flex-1">{children}</main>
    </div>
  );
}