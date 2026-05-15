"use client";

import Link from "next/link";
import { ArrowRight, Sparkles, Zap, Code, GitBranch } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 z-0">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-primary/5 rounded-full blur-[120px]" />
        <div className="absolute bottom-0 right-0 w-[600px] h-[600px] bg-secondary/5 rounded-full blur-[120px]" />
      </div>

      {/* Header */}
      <header className="relative z-10 border-b border-outline-variant/30 bg-background/80 backdrop-blur-xl">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Sparkles className="w-6 h-6 text-primary" />
            <span className="font-display-lg text-headline-md text-primary tracking-tighter">
              OrkestrAI
            </span>
          </div>
          <nav className="hidden md:flex items-center space-x-8">
            <Link href="#features" className="text-on-surface-variant hover:text-primary transition-colors">
              Features
            </Link>
            <Link href="#how-it-works" className="text-on-surface-variant hover:text-primary transition-colors">
              How It Works
            </Link>
            <Link href="/create" className="bg-primary text-on-primary px-6 py-2 rounded-lg font-semibold hover:bg-primary-fixed transition-colors">
              Get Started
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <main className="relative z-10">
        <section className="container mx-auto px-6 py-20 md:py-32">
          <div className="max-w-4xl mx-auto text-center space-y-8">
            <div className="inline-flex items-center space-x-2 bg-surface-container-low border border-outline-variant/30 rounded-full px-4 py-2 mb-4">
              <Zap className="w-4 h-4 text-tertiary" />
              <span className="font-code-sm text-code-sm text-on-surface-variant">
                AI-Powered Development Orchestration
              </span>
            </div>

            <h1 className="font-display-lg text-5xl md:text-7xl font-bold text-on-surface leading-tight">
              Transform Ideas into
              <span className="text-primary"> Production Code</span>
            </h1>

            <p className="font-body-base text-xl text-on-surface-variant max-w-2xl mx-auto">
              Watch AI agents collaborate in real-time to design, architect, and build your next project. 
              From concept to deployment in minutes, not days.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
              <Link 
                href="/create"
                className="group bg-primary text-on-primary px-8 py-4 rounded-lg font-semibold text-lg flex items-center space-x-2 hover:bg-primary-fixed transition-all hover:scale-105"
              >
                <span>Start Building</span>
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <button className="bg-surface-container-low border border-outline-variant/30 text-on-surface px-8 py-4 rounded-lg font-semibold text-lg hover:bg-surface-container-high transition-colors">
                Watch Demo
              </button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-8 pt-12 max-w-2xl mx-auto">
              <div className="text-center">
                <div className="font-display-lg text-4xl font-bold text-primary">5</div>
                <div className="font-code-sm text-code-sm text-on-surface-variant mt-1">AI Agents</div>
              </div>
              <div className="text-center">
                <div className="font-display-lg text-4xl font-bold text-tertiary">10x</div>
                <div className="font-code-sm text-code-sm text-on-surface-variant mt-1">Faster</div>
              </div>
              <div className="text-center">
                <div className="font-display-lg text-4xl font-bold text-secondary">100%</div>
                <div className="font-code-sm text-code-sm text-on-surface-variant mt-1">Automated</div>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section id="features" className="container mx-auto px-6 py-20">
          <div className="text-center mb-16">
            <h2 className="font-display-lg text-4xl font-bold text-on-surface mb-4">
              Powered by AI Agent Swarm
            </h2>
            <p className="font-body-base text-xl text-on-surface-variant max-w-2xl mx-auto">
              Five specialized AI agents work together to bring your vision to life
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
                title: "Code Builder Agent",
                description: "Generates production-ready code with best practices and modern frameworks",
                color: "text-tertiary"
              },
              {
                icon: <GitBranch className="w-6 h-6" />,
                title: "GitHub Agent",
                description: "Creates repositories, issues, and project boards for seamless collaboration",
                color: "text-error"
              },
              {
                icon: <Sparkles className="w-6 h-6" />,
                title: "Pitch Agent",
                description: "Crafts compelling pitch decks and demo scripts for presentations",
                color: "text-secondary-fixed-dim"
              },
              {
                icon: <Code className="w-6 h-6" />,
                title: "Real-time Updates",
                description: "Watch agents think and collaborate live with WebSocket streaming",
                color: "text-primary-fixed-dim"
              }
            ].map((feature, index) => (
              <div 
                key={index}
                className="glass-panel p-6 rounded-xl hover:border-primary/50 transition-all group cursor-pointer"
              >
                <div className={`${feature.color} mb-4 group-hover:scale-110 transition-transform`}>
                  {feature.icon}
                </div>
                <h3 className="font-headline-md text-headline-md text-on-surface mb-2">
                  {feature.title}
                </h3>
                <p className="font-body-base text-body-base text-on-surface-variant">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </section>

        {/* How It Works */}
        <section id="how-it-works" className="container mx-auto px-6 py-20">
          <div className="text-center mb-16">
            <h2 className="font-display-lg text-4xl font-bold text-on-surface mb-4">
              From Idea to Code in 3 Steps
            </h2>
          </div>

          <div className="max-w-4xl mx-auto space-y-8">
            {[
              {
                step: "01",
                title: "Describe Your Idea",
                description: "Tell us what you want to build in plain English. No technical jargon required."
              },
              {
                step: "02",
                title: "Watch Agents Work",
                description: "See AI agents collaborate in real-time, making decisions and generating code."
              },
              {
                step: "03",
                title: "Download & Deploy",
                description: "Get production-ready code, documentation, and deployment instructions instantly."
              }
            ].map((item, index) => (
              <div key={index} className="flex items-start space-x-6 group">
                <div className="flex-shrink-0 w-16 h-16 rounded-full bg-primary/10 border-2 border-primary flex items-center justify-center font-code-sm text-code-sm text-primary font-bold">
                  {item.step}
                </div>
                <div className="flex-1 pt-2">
                  <h3 className="font-headline-md text-headline-md text-on-surface mb-2 group-hover:text-primary transition-colors">
                    {item.title}
                  </h3>
                  <p className="font-body-base text-body-base text-on-surface-variant">
                    {item.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* CTA Section */}
        <section className="container mx-auto px-6 py-20">
          <div className="glass-panel rounded-2xl p-12 text-center max-w-4xl mx-auto">
            <h2 className="font-display-lg text-4xl font-bold text-on-surface mb-4">
              Ready to Build Something Amazing?
            </h2>
            <p className="font-body-base text-xl text-on-surface-variant mb-8 max-w-2xl mx-auto">
              Join developers who are shipping faster with AI-powered orchestration
            </p>
            <Link 
              href="/create"
              className="inline-flex items-center space-x-2 bg-primary text-on-primary px-8 py-4 rounded-lg font-semibold text-lg hover:bg-primary-fixed transition-all hover:scale-105"
            >
              <span>Start Your Project</span>
              <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-outline-variant/30 bg-background/80 backdrop-blur-xl">
        <div className="container mx-auto px-6 py-8">
          <div className="flex flex-col md:flex-row items-center justify-between">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <Sparkles className="w-5 h-5 text-primary" />
              <span className="font-code-sm text-code-sm text-on-surface-variant">
                OrkestrAI © 2026
              </span>
            </div>
            <div className="flex items-center space-x-6">
              <Link href="#" className="text-on-surface-variant hover:text-primary transition-colors font-code-sm text-code-sm">
                Documentation
              </Link>
              <Link href="#" className="text-on-surface-variant hover:text-primary transition-colors font-code-sm text-code-sm">
                GitHub
              </Link>
              <Link href="#" className="text-on-surface-variant hover:text-primary transition-colors font-code-sm text-code-sm">
                Support
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

// Made with Bob
