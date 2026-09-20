import { useEffect, useState } from 'react';
import { Link } from 'wouter';
import { ArrowLeft, Check, Moon, PanelTop, SlidersHorizontal, Sun, Zap } from 'lucide-react';
import { NexusShell } from '@/components/nexus-shell';

type ToggleProps = {
  label: string;
  description: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  testId: string;
};

function Toggle({ label, description, checked, onChange, testId }: ToggleProps) {
  return (
    <div className="flex cursor-pointer items-center justify-between gap-5 rounded-2xl border border-border/75 bg-card/55 px-4 py-4 transition hover:border-primary/25 hover:bg-card">
      <span>
        <span className="block text-sm font-semibold">{label}</span>
        <span className="mt-1 block text-xs leading-5 text-muted-foreground">{description}</span>
      </span>
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        data-testid={testId}
        className={`relative h-6 w-11 shrink-0 rounded-full p-1 transition ${checked ? 'bg-primary' : 'bg-secondary'}`}
      >
        <span className={`block h-4 w-4 rounded-full bg-card shadow-sm transition-transform ${checked ? 'translate-x-5' : 'translate-x-0'}`} />
      </button>
    </div>
  );
}

export default function Settings() {
  const [theme, setTheme] = useState<'light' | 'dark'>((localStorage.getItem('nexus-theme') as 'light' | 'dark') || 'light');
  const [model, setModel] = useState(localStorage.getItem('nexus-model') || 'balanced');
  const [voice, setVoice] = useState(localStorage.getItem('nexus-voice') || 'considered');
  const [citations, setCitations] = useState(localStorage.getItem('nexus-citations') !== 'false');
  const [enterToSend, setEnterToSend] = useState(localStorage.getItem('nexus-enter-to-send') !== 'false');
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
    localStorage.setItem('nexus-theme', theme);
  }, [theme]);

  const update = (key: string, value: string | boolean) => {
    localStorage.setItem(`nexus-${key}`, String(value));
    setSaved(true);
    window.setTimeout(() => setSaved(false), 1600);
  };

  return (
    <NexusShell>
      <div className="min-h-[100dvh]">
        <header className="flex h-[76px] items-center justify-between border-b border-border/70 px-5 pl-[68px] md:px-10 md:pl-10">
          <div>
            <p className="font-mono-ui text-[10px] uppercase tracking-[.2em] text-muted-foreground">Nexus workspace</p>
            <h1 className="mt-1 font-display text-lg font-semibold tracking-[-.035em]">Preferences</h1>
          </div>
          <Link href="/" data-testid="link-back-workspace" className="flex items-center gap-2 rounded-xl border border-border bg-card/60 px-3 py-2 text-xs font-medium text-muted-foreground transition hover:bg-secondary hover:text-foreground">
            <ArrowLeft size={14} /> <span className="hidden sm:inline">Back to workspace</span>
          </Link>
        </header>
        <main className="mx-auto max-w-3xl px-5 py-9 md:px-10 md:py-14">
          <div className="appear">
            <p className="font-mono-ui text-[10px] uppercase tracking-[.2em] text-primary">Shape the room</p>
            <h2 className="mt-3 font-display text-3xl font-semibold tracking-[-.05em] sm:text-4xl">Make thinking feel like yours.</h2>
            <p className="mt-3 max-w-lg text-sm leading-6 text-muted-foreground">Small choices change the quality of a long conversation. Nexus keeps these preferences on this device.</p>
          </div>

          <section className="appear appear-delay-1 mt-10" aria-labelledby="model-heading">
            <div className="mb-3 flex items-center gap-2">
              <Zap size={16} className="text-accent" />
              <h3 id="model-heading" className="font-display text-sm font-semibold">Response character</h3>
            </div>
            <div className="grid gap-3 sm:grid-cols-3">
              {[
                { id: 'quick', title: 'Quick', detail: 'Short and direct' },
                { id: 'balanced', title: 'Balanced', detail: 'Clear with context' },
                { id: 'deep', title: 'Deep', detail: 'Take the long view' },
              ].map((option) => (
                <button
                  type="button"
                  key={option.id}
                  onClick={() => { setModel(option.id); update('model', option.id); }}
                  data-testid={`button-model-${option.id}`}
                  className={`rounded-2xl border p-4 text-left transition hover:-translate-y-0.5 ${model === option.id ? 'border-primary/45 bg-primary/8 shadow-sm' : 'border-border/75 bg-card/55 hover:border-primary/25'}`}
                >
                  <span className={`mb-5 block h-2 w-2 rounded-full ${model === option.id ? 'bg-accent' : 'bg-border'}`} />
                  <span className="block text-sm font-semibold">{option.title}</span>
                  <span className="mt-1 block text-xs text-muted-foreground">{option.detail}</span>
                </button>
              ))}
            </div>
          </section>

          <section className="appear appear-delay-2 mt-9" aria-labelledby="voice-heading">
            <div className="mb-3 flex items-center gap-2">
              <SlidersHorizontal size={16} className="text-accent" />
              <h3 id="voice-heading" className="font-display text-sm font-semibold">Assistant voice</h3>
            </div>
            <div className="rounded-2xl border border-border/75 bg-card/55 p-1.5">
              {[
                { id: 'considered', title: 'Considered', detail: 'Reflective, warm, and precise' },
                { id: 'challenging', title: 'Challenging', detail: 'Pushes ideas with useful friction' },
                { id: 'practical', title: 'Practical', detail: 'Turns thoughts into next steps' },
              ].map((option) => (
                <button
                  type="button"
                  key={option.id}
                  onClick={() => { setVoice(option.id); update('voice', option.id); }}
                  data-testid={`button-voice-${option.id}`}
                  className={`flex w-full items-center justify-between rounded-xl px-3.5 py-3 text-left transition ${voice === option.id ? 'bg-secondary' : 'hover:bg-secondary/60'}`}
                >
                  <span><span className="block text-sm font-semibold">{option.title}</span><span className="mt-0.5 block text-xs text-muted-foreground">{option.detail}</span></span>
                  {voice === option.id && <Check size={16} className="text-primary" />}
                </button>
              ))}
            </div>
          </section>

          <section className="appear appear-delay-3 mt-9" aria-labelledby="interface-heading">
            <div className="mb-3 flex items-center gap-2">
              <PanelTop size={16} className="text-accent" />
              <h3 id="interface-heading" className="font-display text-sm font-semibold">Interface</h3>
            </div>
            <div className="space-y-2.5">
              <Toggle label="Show source notes" description="Leave room for citations when Nexus uses outside knowledge." checked={citations} onChange={(value) => { setCitations(value); update('citations', value); }} testId="switch-citations" />
              <Toggle label="Enter sends message" description="Use Shift + Enter when you want a new line in the composer." checked={enterToSend} onChange={(value) => { setEnterToSend(value); update('enter-to-send', value); }} testId="switch-enter-to-send" />
            </div>
            <div className="mt-2.5 flex items-center justify-between rounded-2xl border border-border/75 bg-card/55 px-4 py-4">
              <span><span className="block text-sm font-semibold">Appearance</span><span className="mt-1 block text-xs text-muted-foreground">Choose the atmosphere for your workspace.</span></span>
              <div className="flex rounded-xl bg-secondary p-1">
                <button type="button" onClick={() => setTheme('light')} data-testid="button-theme-light" aria-label="Use light appearance" className={`rounded-lg p-2 transition ${theme === 'light' ? 'bg-card text-foreground shadow-sm' : 'text-muted-foreground'}`}><Sun size={15} /></button>
                <button type="button" onClick={() => setTheme('dark')} data-testid="button-theme-dark" aria-label="Use dark appearance" className={`rounded-lg p-2 transition ${theme === 'dark' ? 'bg-card text-foreground shadow-sm' : 'text-muted-foreground'}`}><Moon size={15} /></button>
              </div>
            </div>
          </section>
          <div className={`mt-7 flex items-center justify-end gap-2 text-xs text-primary transition ${saved ? 'opacity-100' : 'opacity-0'}`} data-testid="status-preferences-saved"><Check size={14} /> Preferences saved locally</div>
        </main>
      </div>
    </NexusShell>
  );
}