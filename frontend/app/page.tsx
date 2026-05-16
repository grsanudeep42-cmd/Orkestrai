"use client";

import Link from "next/link";
import { ArrowRight, Sparkles, Zap, Code, GitBranch, Terminal } from "lucide-react";
import { useEffect, useState } from "react";

const TerminalText = () => {
  const [text, setText] = useState("");
  const fullText = "> Initializing OrkestrAI Swarm...\n> Strategy Agent... Online\n> Architecture Agent... Online\n> Builder Agent... Compiling...\n> GitHub Agent... Repo Created\n> Pitch Agent... Deck Ready\n> Status: SYSTEM READY";
  
  useEffect(() => {
    let i = 0;
    const timer = setInterval(() => {
      setText(fullText.slice(0, i));
      i++;
      if (i > fullText.length) clearInterval(timer);
    }, 50);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="bg-background border border-border p-4 rounded-lg font-mono text-sm text-success whitespace-pre-line h-48 overflow-hidden shadow-[0_0_15px_rgba(0,255,136,0.1)]">
      {text}<span className="animate-pulse">_</span>
    </div>
  );
};

export default function Home() {
  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 z-0 pointer-events-none">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-primary/10 rounded-full blur-[120px]" />
        <div className="absolute bottom-0 right-0 w-[600px] h-[600px] bg-secondary/10 rounded-full blur-[120px]" />
      </div>

      {/* Header */}
      <header className="relative z-10 border-b border-border bg-background/80 backdrop-blur-xl">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Sparkles className="w-6 h-6 text-primary" />
            <span className="text-xl font-bold text-foreground tracking-tighter">
              OrkestrAI
            </span>
          </div>
          <nav className="hidden md:flex items-center space-x-8">
            <Link href="#features" className="text-muted-foreground hover:text-primary transition-colors">
              Features
            </Link>
            <Link href="#how-it-works" className="text-muted-foreground hover:text-primary transition-colors">
              How It Works
            </Link>
            <Link href="/create" className="bg-primary text-background px-6 py-2 rounded-md font-semibold hover:bg-primary-hover transition-colors shadow-[0_0_15px_rgba(0,212,255,0.3)]">
              Get Started
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <main className="relative z-10">
        <section className="container mx-auto px-6 py-20 md:py-32 grid lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-8">
            <div className="inline-flex items-center space-x-2 bg-surface border border-border rounded-full px-4 py-2 mb-4">
              <Zap className="w-4 h-4 text-primary" />
              <span className="font-mono text-sm text-primary">
                v2.0 Autonomous Swarm
              </span>
            </div>

            <h1 className="text-5xl md:text-7xl font-bold text-foreground leading-tight">
              Transform Ideas into <br/>
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-secondary">Production Code</span>
            </h1>

            <p className="text-xl text-muted-foreground max-w-xl">
              Watch AI agents collaborate in real-time to design, architect, and build your next project. 
              From concept to deployment in minutes, not days.
            </p>

            <div className="flex flex-col sm:flex-row items-center gap-4 pt-4">
              <Link 
                href="/create"
                className="group bg-primary text-background px-8 py-4 rounded-md font-semibold text-lg flex items-center space-x-2 hover:bg-primary-hover transition-all hover:scale-105 shadow-[0_0_20px_rgba(0,212,255,0.4)]"
              >
                <span>Start Building</span>
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link href="https://github.com" className="bg-surface border border-border text-foreground px-8 py-4 rounded-md font-semibold text-lg hover:bg-muted transition-colors flex items-center space-x-2">
                <GitBranch className="w-5 h-5" />
                <span>View Output Repo</span>
              </Link>
            </div>
            
            {/* Stats Bar */}
            <div className="grid grid-cols-3 gap-6 pt-8 border-t border-border mt-8">
              <div>
                <div className="text-3xl font-bold text-foreground">6</div>
                <div className="text-sm text-muted-foreground uppercase tracking-wider font-mono mt-1">Autonomous Agents</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-foreground">10x</div>
                <div className="text-sm text-muted-foreground uppercase tracking-wider font-mono mt-1">Faster Shipping</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-foreground">100%</div>
                <div className="text-sm text-muted-foreground uppercase tracking-wider font-mono mt-1">Ready to Deploy</div>
              </div>
            </div>
          </div>
          
          <div className="glass-panel p-2 rounded-xl relative group">
            <div className="absolute -inset-1 bg-gradient-to-r from-primary to-secondary rounded-xl blur opacity-25 group-hover:opacity-40 transition duration-1000 group-hover:duration-200"></div>
            <div className="relative bg-surface rounded-lg p-2 border border-border">
              <div className="flex items-center space-x-2 px-4 py-2 border-b border-border mb-2">
                <div className="w-3 h-3 rounded-full bg-error" />
                <div className="w-3 h-3 rounded-full bg-warning" />
                <div className="w-3 h-3 rounded-full bg-success" />
                <span className="ml-4 font-mono text-xs text-muted-foreground">orkestrai-terminal</span>
              </div>
              <TerminalText />
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section id="features" className="container mx-auto px-6 py-20 border-t border-border/50">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-foreground mb-4">
              Powered by AI Agent Swarm
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Six specialized AI agents work together to bring your vision to life
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
            {[
              {
                icon: <Sparkles className="w-6 h-6" />,
                title: "Strategy Agent",
                description: "Analyzes your idea and creates a comprehensive product strategy with features and MVP scope",
                color: "text-secondary"
              },
              {
                icon: <Code className="w-6 h-6" />,
                title: "Architecture Agent",
                description: "Designs scalable system architecture, database schemas, and API structures",
                color: "text-primary"
              },
              {
                icon: <Zap className="w-6 h-6" />,
                title: "Builder Agent",
                description: "Generates production-ready code with best practices and creates a downloadable zip",
                color: "text-warning"
              },
              {
                icon: <GitBranch className="w-6 h-6" />,
                title: "GitHub Agent",
                description: "Creates real repositories, pushes code, and configures CI/CD workflows",
                color: "text-success"
              },
              {
                icon: <Terminal className="w-6 h-6" />,
                title: "Pitch Agent",
                description: "Crafts compelling pitch decks in a self-contained HTML presentation",
                color: "text-primary"
              },
              {
                icon: <Code className="w-6 h-6" />,
                title: "Audit Agent",
                description: "Ruthlessly reviews outputs and forces retries if quality standards aren't met",
                color: "text-error"
              }
            ].map((feature, index) => (
              <div 
                key={index}
                className="glass-panel p-6 rounded-xl hover:border-primary/50 transition-all group cursor-pointer"
              >
                <div className={`${feature.color} mb-4 group-hover:scale-110 transition-transform`}>
                  {feature.icon}
                </div>
                <h3 className="text-xl font-bold text-foreground mb-2">
                  {feature.title}
                </h3>
                <p className="text-muted-foreground">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </section>

        {/* CTA Section */}
        <section className="container mx-auto px-6 py-20 mb-20">
          <div className="relative rounded-2xl p-12 text-center max-w-4xl mx-auto border border-primary/30 bg-surface overflow-hidden">
            <div className="absolute inset-0 bg-hero-glow pointer-events-none"></div>
            <div className="relative z-10">
              <h2 className="text-4xl font-bold text-foreground mb-4">
                Ready to Build Something Amazing?
              </h2>
              <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
                Stop planning. Start shipping.
              </p>
              <Link 
                href="/create"
                className="inline-flex items-center space-x-2 bg-primary text-background px-8 py-4 rounded-md font-semibold text-lg hover:bg-primary-hover transition-all hover:scale-105 shadow-[0_0_20px_rgba(0,212,255,0.4)]"
              >
                <span>Initialize Swarm</span>
                <ArrowRight className="w-5 h-5" />
              </Link>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-border bg-surface py-8">
        <div className="container mx-auto px-6">
          <div className="flex flex-col md:flex-row items-center justify-between">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <Sparkles className="w-5 h-5 text-primary" />
              <span className="font-mono text-sm text-muted-foreground">
                OrkestrAI © 2026
              </span>
            </div>
            <div className="flex items-center space-x-6">
              <Link href="#" className="text-muted-foreground hover:text-primary transition-colors font-mono text-sm">
                Documentation
              </Link>
              <Link href="#" className="text-muted-foreground hover:text-primary transition-colors font-mono text-sm">
                GitHub
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
