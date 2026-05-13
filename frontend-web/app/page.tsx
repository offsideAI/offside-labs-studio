import { Card, CardContent, CardHeader, Eyebrow, Hairline, StatusPill } from "@offside/ui";
import Link from "next/link";

export default function HomePage() {
  return (
    <div className="bg-render-dark text-white min-h-screen overflow-hidden font-sans">
      {/* Top Navigation */}
      <nav className="flex items-center justify-between px-6 py-4 bg-[#0a0a0a] border-b border-gray-800/50 sticky top-0 z-50 backdrop-blur-md bg-opacity-90">
        <div className="flex items-center gap-8">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 group">
            <svg className="h-6 w-auto text-white group-hover:text-render-purple transition-colors" viewBox="0 0 103.8 72.8" xmlns="http://www.w3.org/2000/svg">
              <path fill="currentColor" d="M67.5.2c-3.1,0-6,.4-8.9,1.1-2.3.6-4.6,1.4-6.7,2.4-2.1-1-4.4-1.8-6.7-2.4-2.9-.7-5.8-1.1-8.9-1.1C16.3.2,0,16.5,0,36.5s16.3,36.3,36.3,36.3,6-.4,8.9-1.1c-4-2.5-7.6-5.7-10.5-9.5-13.5-.8-24.2-12.1-24.2-25.8s10.7-25,24.2-25.8h1.6c1.7,0,3.4.2,5.1.5,3.9.8,7.4,2.4,10.5,4.7,1.5,1.1,2.8,2.3,4,3.7.4.4.7.8,1,1.2.6.8,1.2,1.6,1.7,2.5.3.4.5.9.8,1.3.3.6.6,1.2.9,1.8.3.8.6,1.6.9,2.4.1.4.2.8.4,1.2.1.5.2,1,.4,1.6.2.8.3,1.6.4,2.4,0,.8.1,1.6.1,2.5s0,1.6-.1,2.5-.2,1.6-.4,2.4c-.1.5-.2,1.1-.4,1.6-.1.4-.2.8-.4,1.2-.2.8-.6,1.6-.9,2.4-.3.6-.6,1.2-.9,1.8-.2.4-.5.9-.8,1.3-.5.9-1.1,1.7-1.7,2.5-.3.4-.6.8-1,1.2-1.2,1.4-2.5,2.6-4,3.7-1.5-1.1-2.8-2.3-4-3.7-3.9-4.5-6.3-10.4-6.3-16.9s2.4-12.4,6.3-16.9c-3-2.1-6.6-3.4-10.5-3.6-4,5.8-6.3,12.9-6.3,20.5s2.3,14.6,6.3,20.5c1.2,1.7,2.5,3.4,4,4.9,3,3.1,6.5,5.6,10.5,7.5,2.1,1,4.3,1.8,6.7,2.4,2.9.7,5.8,1.1,8.9,1.1,7.7,0,15-2.4,21.2-6.9l-6.1-8.5c-4,2.9-8.6,4.5-13.5,4.8h-1.6c-1.7,0-3.4-.2-5.1-.5,1.5-1.5,2.8-3.1,4-4.9,4-5.8,6.3-12.9,6.3-20.5s-2.3-14.7-6.3-20.5c-1.2-1.7-2.5-3.4-4-4.8,1.6-.3,3.4-.5,5.1-.5s1.1,0,1.6,0c13.5.8,24.2,12.1,24.2,25.8v35.7h10.5v-35.7C103.8,16.3,87.5,0,67.5,0h0v.2Z"></path>
            </svg>
            <span className="font-bold text-lg tracking-tight">OffsideStudio</span>
          </Link>

          {/* Desktop Links */}
          <div className="hidden lg:flex items-center gap-6 text-sm text-gray-300">
            <Link href="#product" className="hover:text-white transition-colors">Product</Link>
            <Link href="#pricing" className="hover:text-white transition-colors">Pricing</Link>
            <Link href="#customers" className="hover:text-white transition-colors">Customers</Link>
            <Link href="#docs" className="hover:text-white transition-colors">Docs</Link>
            <Link href="#templates" className="hover:text-white transition-colors">Templates</Link>
            <Link href="#company" className="hover:text-white transition-colors">Company</Link>
          </div>
        </div>

        {/* Right Actions */}
        <div className="hidden md:flex items-center gap-6 text-sm">
          <Link href="/contact" className="text-gray-300 hover:text-white transition-colors">Contact</Link>
          <Link href="/login" className="text-gray-300 hover:text-white transition-colors">Sign In</Link>
          <Link href="/marketplace" className="bg-white text-black px-4 py-2 rounded-sm font-semibold hover:bg-gray-200 transition-colors">
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="relative max-w-[1400px] mx-auto px-6 py-20 lg:py-32 grid lg:grid-cols-2 gap-12 items-center">
        {/* Background glow */}
        <div className="absolute top-0 right-0 w-full h-full bg-render-glow -z-10 pointer-events-none" />

        <div className="space-y-8 z-10 animate-fade-in-up">
          <Eyebrow className="text-render-purpleLight border border-render-purple/30 rounded-full px-4 py-1.5 inline-block bg-render-purple/10">
            OffsideStudio — Agent Marketplace
          </Eyebrow>
          <h1 className="text-5xl lg:text-7xl font-bold tracking-tight leading-[1.1]">
            Your fastest path to production agents
          </h1>
          <p className="text-xl lg:text-2xl text-gray-400 max-w-xl leading-relaxed">
            Execution agent infrastructure to scale your ecommerce, sales, marketing and custom agents from your first customer to your millionth.
          </p>
          <div className="flex flex-wrap gap-4 pt-4">
            <Link
              href="/marketplace"
              className="px-6 py-3 bg-white text-black font-semibold rounded-sm hover:bg-gray-100 transition-colors"
            >
              Start for free &rarr;
            </Link>
            <Link
              href="/contact"
              className="px-6 py-3 border border-gray-600 text-white font-semibold rounded-sm hover:bg-gray-800 transition-colors"
            >
              Get in touch
            </Link>
          </div>
        </div>

        {/* Hero Diagram (CSS representation) */}
        <div className="relative h-[400px] lg:h-[500px] hidden lg:block animate-float">
          {/* Faint grid background */}
          <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.05)_1px,transparent_1px)] bg-[size:40px_40px] [mask-image:radial-gradient(ellipse_at_center,black_40%,transparent_70%)]" />

          <div className="absolute top-1/4 left-0 bg-render-gray border border-gray-700 p-3 rounded-sm font-mono text-sm text-gray-300 shadow-2xl z-20">
            $ git push origin main
          </div>

          {/* Workflow boxes */}
          <div className="absolute top-1/2 left-1/4 w-[400px] bg-render-gray/80 backdrop-blur-md border border-gray-700 rounded-sm p-4 shadow-2xl z-10">
            <div className="text-xs font-mono text-gray-500 mb-4">PRODUCTION FLOW</div>
            <div className="grid grid-cols-2 gap-4">
              <div className="border border-gray-700 bg-black/50 p-3 rounded-sm relative overflow-hidden">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-xs font-semibold text-gray-300">crm-sync</span>
                  <span className="text-[10px] text-render-green flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-render-green animate-pulse-glow" /> Active
                  </span>
                </div>
                <div className="h-6 w-full mt-2 relative">
                  <div className="absolute inset-x-0 bottom-0 border-b border-render-purple/30" />
                  <svg className="absolute inset-0 w-full h-full" preserveAspectRatio="none" viewBox="0 0 100 20">
                    <path d="M0,10 Q20,20 40,5 T60,15 T100,10" fill="none" stroke="var(--brand-tan)" strokeWidth="1.5" className="animate-pulse-glow" />
                  </svg>
                </div>
              </div>
              <div className="border border-gray-700 bg-black/50 p-3 rounded-sm relative overflow-hidden">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-xs font-semibold text-gray-300">agent-runtime</span>
                  <span className="text-[10px] text-render-purple flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-render-purple animate-pulse-glow" /> Running
                  </span>
                </div>
                <div className="h-6 w-full mt-2 relative">
                  <div className="absolute inset-x-0 bottom-0 border-b border-render-purple/30" />
                  <svg className="absolute inset-0 w-full h-full" preserveAspectRatio="none" viewBox="0 0 100 20">
                    <path d="M0,15 Q30,5 50,15 T80,5 T100,15" fill="none" stroke="#9b51e0" strokeWidth="1.5" className="animate-pulse-glow" />
                  </svg>
                </div>
              </div>
            </div>

            {/* Connection lines */}
            <svg className="absolute -top-12 -left-12 w-20 h-20 pointer-events-none" style={{ zIndex: -1 }}>
              <path d="M 10 10 L 10 50 L 70 50" fill="none" stroke="#9b51e0" strokeWidth="2" strokeDasharray="4 4" className="animate-pulse-glow" />
            </svg>
          </div>
        </div>
      </div>

      {/* Agent Carousel */}
      <section className="border-y border-gray-800 bg-[#0a0a0a] overflow-hidden py-6 flex items-center relative z-20">
        {/* Left and right fade gradients */}
        <div className="absolute left-0 top-0 bottom-0 w-32 bg-gradient-to-r from-[#0a0a0a] to-transparent z-10 pointer-events-none" />
        <div className="absolute right-0 top-0 bottom-0 w-32 bg-gradient-to-l from-[#0a0a0a] to-transparent z-10 pointer-events-none" />

        <div className="flex whitespace-nowrap animate-marquee">
          {/* Group 1 */}
          <div className="flex items-center justify-around shrink-0 gap-8 px-4">
            <div className="flex items-center gap-3 px-4 py-2 border border-gray-800 bg-render-gray/50 rounded-full hover:border-render-purple transition-colors">
              <span className="text-xl">🤖</span>
              <div className="flex flex-col">
                <span className="text-sm font-semibold text-white">Multi-channel Sales Orchestrator</span>
                <span className="text-[10px] text-gray-400 uppercase tracking-widest font-mono">OpenClaw</span>
              </div>
            </div>

            <div className="flex items-center gap-3 px-4 py-2 border border-gray-800 bg-render-gray/50 rounded-full hover:border-render-green transition-colors">
              <span className="text-xl">🧠</span>
              <div className="flex flex-col">
                <span className="text-sm font-semibold text-white">Predictive Lead Researcher</span>
                <span className="text-[10px] text-gray-400 uppercase tracking-widest font-mono">Hermes</span>
              </div>
            </div>

            <div className="flex items-center gap-3 px-4 py-2 border border-gray-800 bg-render-gray/50 rounded-full hover:border-render-purple transition-colors">
              <span className="text-xl">🎫</span>
              <div className="flex flex-col">
                <span className="text-sm font-semibold text-white">Omnichannel Support Router</span>
                <span className="text-[10px] text-gray-400 uppercase tracking-widest font-mono">OpenClaw</span>
              </div>
            </div>

            <div className="flex items-center gap-3 px-4 py-2 border border-gray-800 bg-render-gray/50 rounded-full hover:border-render-green transition-colors">
              <span className="text-xl">✍️</span>
              <div className="flex flex-col">
                <span className="text-sm font-semibold text-white">Iterative SEO Content Engine</span>
                <span className="text-[10px] text-gray-400 uppercase tracking-widest font-mono">Hermes</span>
              </div>
            </div>

            <div className="flex items-center gap-3 px-4 py-2 border border-gray-800 bg-render-gray/50 rounded-full hover:border-[var(--brand-tan)] transition-colors">
              <span className="text-xl">🛒</span>
              <div className="flex flex-col">
                <span className="text-sm font-semibold text-white">Smart Cart Recovery</span>
                <span className="text-[10px] text-gray-400 uppercase tracking-widest font-mono">Stacked</span>
              </div>
            </div>
          </div>
          {/* Group 2 (Duplicate for seamless loop) */}
          <div className="flex items-center justify-around shrink-0 gap-8 px-4">
            <div className="flex items-center gap-3 px-4 py-2 border border-gray-800 bg-render-gray/50 rounded-full hover:border-render-purple transition-colors">
              <span className="text-xl">🤖</span>
              <div className="flex flex-col">
                <span className="text-sm font-semibold text-white">Multi-channel Sales Orchestrator</span>
                <span className="text-[10px] text-gray-400 uppercase tracking-widest font-mono">OpenClaw</span>
              </div>
            </div>

            <div className="flex items-center gap-3 px-4 py-2 border border-gray-800 bg-render-gray/50 rounded-full hover:border-render-green transition-colors">
              <span className="text-xl">🧠</span>
              <div className="flex flex-col">
                <span className="text-sm font-semibold text-white">Predictive Lead Researcher</span>
                <span className="text-[10px] text-gray-400 uppercase tracking-widest font-mono">Hermes</span>
              </div>
            </div>

            <div className="flex items-center gap-3 px-4 py-2 border border-gray-800 bg-render-gray/50 rounded-full hover:border-render-purple transition-colors">
              <span className="text-xl">🎫</span>
              <div className="flex flex-col">
                <span className="text-sm font-semibold text-white">Omnichannel Support Router</span>
                <span className="text-[10px] text-gray-400 uppercase tracking-widest font-mono">OpenClaw</span>
              </div>
            </div>

            <div className="flex items-center gap-3 px-4 py-2 border border-gray-800 bg-render-gray/50 rounded-full hover:border-render-green transition-colors">
              <span className="text-xl">✍️</span>
              <div className="flex flex-col">
                <span className="text-sm font-semibold text-white">Iterative SEO Content Engine</span>
                <span className="text-[10px] text-gray-400 uppercase tracking-widest font-mono">Hermes</span>
              </div>
            </div>

            <div className="flex items-center gap-3 px-4 py-2 border border-gray-800 bg-render-gray/50 rounded-full hover:border-[var(--brand-tan)] transition-colors">
              <span className="text-xl">🛒</span>
              <div className="flex flex-col">
                <span className="text-sm font-semibold text-white">Smart Cart Recovery</span>
                <span className="text-[10px] text-gray-400 uppercase tracking-widest font-mono">Stacked</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Agent Designer Views */}
      <section className="max-w-[1400px] mx-auto px-6 py-24 border-b border-gray-800">
        <div className="grid md:grid-cols-2 gap-16 lg:gap-24">

          {/* Left Column: Workflows as Code */}
          <div className="space-y-8">
            <div className="space-y-4">
              <h2 className="text-3xl lg:text-4xl font-semibold tracking-tight text-white">
                Durable, long-running agents as code
              </h2>
              <p className="text-gray-400 text-lg leading-relaxed max-w-lg">
                Build complex, stateful agentic workflows using our TypeScript SDK powered by OpenClaw and Hermes. No need to wire up queues or retry logic.
              </p>
              <Link href="/docs/sdk" className="inline-flex items-center text-render-purpleLight hover:text-white transition-colors font-medium text-sm gap-1 group">
                SDK docs <span className="group-hover:translate-x-1 transition-transform">&rarr;</span>
              </Link>
            </div>

            {/* Code Editor Mockup */}
            <div className="rounded-md border border-gray-800 bg-[#0a0a0a] overflow-hidden shadow-2xl relative">
              {/* macOS window dots */}
              <div className="px-4 py-3 border-b border-gray-800 bg-[#141414] flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-[#ED6A5E]" />
                <div className="w-3 h-3 rounded-full bg-[#F4BF4F]" />
                <div className="w-3 h-3 rounded-full bg-[#61C554]" />
              </div>
              <div className="p-6 font-mono text-sm leading-relaxed overflow-x-auto">
                <div className="text-render-purpleLight">@agent</div>
                <div><span className="text-render-purple">async function</span> <span className="text-[#61C554]">analyze_leads</span>(leads: <span className="text-gray-400">Lead[]</span>) {'{'}</div>
                <div className="pl-4">
                  <span className="text-render-purple">const</span> enriched <span className="text-render-purple">=</span> <span className="text-render-purple">await</span> <span className="text-[#61C554]">get_enrichment_data</span>(leads);<br />
                  <span className="text-render-purple">const</span> results <span className="text-render-purple">=</span> <span className="text-render-purple">await</span> Promise.<span className="text-[#61C554]">all</span>(<br />
                  <span className="pl-4">enriched.<span className="text-[#61C554]">map</span>(lead <span className="text-render-purple">=&gt;</span> <span className="text-[#61C554]">summarize_with_llm</span>(lead))</span><br />
                  );<br />
                  <span className="text-render-purple">return</span> results;
                </div>
                <div>{'}'}</div>
                <div className="text-render-purpleLight mt-4">@workflow</div>
                <div><span className="text-render-purple">export async function</span> <span className="text-[#61C554]">sales_pipeline</span>() {'{'}</div>
                <div className="pl-4">
                  <span className="text-gray-500">// Automatic retries & durable execution</span><br />
                  <span className="text-render-purple">await</span> <span className="text-[#61C554]">analyze_leads</span>(new_leads);
                </div>
                <div>{'}'}</div>
              </div>
            </div>
          </div>

          {/* Right Column: Visual Designer */}
          <div className="space-y-8">
            <div className="space-y-4">
              <h2 className="text-3xl lg:text-4xl font-semibold tracking-tight text-white">
                Enterprise-grade Visual Canvas
              </h2>
              <p className="text-gray-400 text-lg leading-relaxed max-w-lg">
                Drag and drop logic nodes, define prompts in plain English, and connect to your CRM without writing a single line of code.
              </p>
              <Link href="/design-studio" className="inline-flex items-center text-render-purpleLight hover:text-white transition-colors font-medium text-sm gap-1 group">
                Design Studio <span className="group-hover:translate-x-1 transition-transform">&rarr;</span>
              </Link>
            </div>

            {/* Visual Canvas Mockup */}
            <div className="rounded-md border border-gray-800 bg-[#0a0a0a] overflow-hidden shadow-2xl relative h-[380px]">
              {/* Background faint grid */}
              <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:20px_20px]" />

              <div className="relative p-6 h-full flex flex-col justify-center">
                {/* Node 1 */}
                <div className="bg-[#141414] border border-gray-700 rounded-sm p-3 w-48 relative z-10 ml-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-semibold text-white flex items-center gap-2">⚡ Webhook</span>
                    <span className="text-[10px] text-render-green">Active</span>
                  </div>
                  <div className="text-[10px] text-gray-500 font-mono">POST /api/leads</div>
                </div>

                {/* SVG connection line */}
                <svg className="absolute left-[13rem] top-[10rem] w-16 h-16 pointer-events-none z-0" style={{ overflow: 'visible' }}>
                  <path d="M 0 0 C 30 0, 30 40, 60 40" fill="none" stroke="var(--brand-rule)" strokeWidth="2" strokeDasharray="4 4" className="animate-pulse-glow" />
                </svg>

                {/* Node 2 */}
                <div className="bg-[#141414] border border-render-purple rounded-sm p-3 w-56 relative z-10 ml-32 mt-4 shadow-[0_0_15px_rgba(155,81,224,0.2)]">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-semibold text-white flex items-center gap-2">🧠 Hermes LLM</span>
                  </div>
                  <div className="text-[10px] text-gray-400 bg-black p-1.5 rounded-sm border border-gray-800">
                    &quot;Extract company name and budget from this payload...&quot;
                  </div>
                </div>

                {/* Mini chart overlay (mimicking the DB charts) */}
                <div className="absolute bottom-6 right-6 bg-[#141414] border border-gray-700 rounded-sm p-3 w-40 z-10">
                  <div className="text-[10px] text-gray-500 font-semibold mb-2">MEMORY USAGE</div>
                  <div className="h-8 relative w-full border-b border-gray-800">
                    <svg className="absolute inset-0 w-full h-full" preserveAspectRatio="none" viewBox="0 0 100 20">
                      <path d="M0,15 Q25,18 50,10 T100,12" fill="none" stroke="var(--brand-tan)" strokeWidth="1.5" />
                    </svg>
                  </div>
                </div>

              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 3 Step Flow Section */}
      <section className="max-w-[1400px] mx-auto px-6 py-24">
        <h2 className="text-5xl font-bold mb-16 text-center lg:text-left">The AI-native Agents Marketplace</h2>
        <div className="grid md:grid-cols-3 gap-12">
          {/* Step 1 */}
          <div className="space-y-4">
            <div className="w-8 h-8 bg-render-purple text-white flex items-center justify-center font-bold text-sm">1</div>
            <h3 className="text-2xl font-semibold">Select an agent</h3>
            <p className="text-gray-400 text-sm leading-relaxed">
              Choose what you need to run your pipelines, communications, databases, cron jobs, and data hygiene from the Agents Marketplace.
            </p>
            <div className="mt-6 border border-gray-800 rounded-sm bg-render-gray p-2 space-y-1 shadow-xl">
              <div className="p-2 text-xs text-gray-500 font-semibold uppercase flex items-center gap-2"><span className="text-lg">+</span> New agent</div>
              <div className="p-3 bg-black border border-gray-700 flex justify-between items-center rounded-sm text-sm">
                <span className="text-gray-300 flex items-center gap-2">🛒 Cart recovery</span>
                <span className="text-render-green">✓</span>
              </div>
              <div className="p-3 bg-render-green/10 border border-render-green text-render-green flex justify-between items-center rounded-sm text-sm">
                <span className="flex items-center gap-2">🎯 Lead qualification</span>
                <span>✓</span>
              </div>
              <div className="p-3 bg-black border border-gray-800 flex justify-between items-center rounded-sm text-sm">
                <span className="text-gray-400 flex items-center gap-2">📧 Welcome series</span>
                <span className="text-render-green">✓</span>
              </div>
            </div>
          </div>

          {/* Step 2 */}
          <div className="space-y-4">
            <div className="w-8 h-8 bg-render-purple text-white flex items-center justify-center font-bold text-sm">2</div>
            <h3 className="text-2xl font-semibold">Customize your workflow</h3>
            <p className="text-gray-400 text-sm leading-relaxed">
              Just connect your CRM data. OffsideStudio orchestrates the flow in the Agent Design Studio with a visual canvas and English prompts.
            </p>
            <div className="mt-6 border border-gray-800 rounded-sm bg-render-gray p-4 space-y-4 shadow-xl text-sm">
              <div className="grid grid-cols-[1fr_2fr] gap-4 items-center">
                <span className="text-gray-500 text-right text-xs">Trigger</span>
                <div className="bg-black border border-gray-700 p-2 text-gray-300 rounded-sm font-mono text-xs flex justify-between">
                  <span>On Lead Created</span> <span>▾</span>
                </div>
              </div>
              <div className="grid grid-cols-[1fr_2fr] gap-4 items-center">
                <span className="text-gray-500 text-right text-xs">Filter</span>
                <div className="bg-black border border-gray-700 p-2 text-gray-300 rounded-sm font-mono text-xs">
                  Score &gt; 70
                </div>
              </div>
              <div className="grid grid-cols-[1fr_2fr] gap-4 items-center mt-2">
                <span className="text-gray-500 text-right text-xs">Auto-Deploy</span>
                <div className="bg-white text-black p-2 rounded-sm flex justify-between font-semibold items-center">
                  Publish Version 1 <span className="text-gray-400 text-xs font-normal">v1</span>
                </div>
              </div>
            </div>
          </div>

          {/* Step 3 */}
          <div className="space-y-4">
            <div className="w-8 h-8 bg-render-purple text-white flex items-center justify-center font-bold text-sm">3</div>
            <h3 className="text-2xl font-semibold">OffsideStudio does the rest</h3>
            <p className="text-gray-400 text-sm leading-relaxed">
              Get instant execution, hitl-approvals, and CRM syncing. Install an agent, customize it in the Design Studio, watch it run against your CRM.
            </p>
            <div className="mt-6 font-mono text-xs text-gray-500 space-y-3 bg-black p-4 rounded-sm border border-gray-800">
              <div>$ agent publish 'final tweaks'</div>
              <div>[main 4f2c9ab] Final tweaks</div>
              <div className="text-render-purple">$ agent run</div>
              <div className="mt-4 space-y-3">
                <div className="flex gap-2 items-start">
                  <div className="w-4 h-4 rounded-full bg-render-green/20 flex items-center justify-center shrink-0 mt-0.5"><div className="w-2 h-2 rounded-full bg-render-green" /></div>
                  <div>
                    <div className="text-gray-300">Run success: Lead enriched</div>
                    <div className="text-gray-600 text-[10px]">1:20:58 PM</div>
                  </div>
                </div>
                <div className="flex gap-2 items-start">
                  <div className="w-4 h-4 rounded-full bg-render-green/20 flex items-center justify-center shrink-0 mt-0.5"><div className="w-2 h-2 rounded-full bg-render-green" /></div>
                  <div>
                    <div className="text-gray-300">Run success: Slack notified</div>
                    <div className="text-gray-600 text-[10px]">1:20:42 PM</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Wedge Section (MVP Features) */}
      <section className="bg-black py-24 relative overflow-hidden">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-4xl h-[1px] bg-gradient-to-r from-transparent via-render-purple to-transparent opacity-50" />
        <div className="max-w-[1400px] mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-5xl font-bold">Whatever your workflow,<br />you can automate it on OffsideStudio.</h2>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-render-gray border border-gray-800 rounded-sm p-8 hover:border-render-purple transition-colors group relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-1 bg-render-purple transform origin-left scale-x-0 group-hover:scale-x-100 transition-transform" />
              <span className="text-render-purpleLight mb-4 block text-xs font-bold tracking-widest uppercase">Wedge 01</span>
              <h3 className="text-2xl font-bold text-white mb-4">Agent Marketplace.</h3>
              <p className="text-gray-400 mb-6">
                A curated catalog of pre-built agents spanning the full ecommerce lifecycle — lead capture, cart recovery, fulfillment, payments. Install one with a click. Or describe one in English.
              </p>
              <StatusPill tone="info">Milestones M7–M9</StatusPill>
            </div>

            <div className="bg-render-gray border border-gray-800 rounded-sm p-8 hover:border-render-green transition-colors group relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-1 bg-render-green transform origin-left scale-x-0 group-hover:scale-x-100 transition-transform" />
              <span className="text-render-green mb-4 block text-xs font-bold tracking-widest uppercase">Wedge 02</span>
              <h3 className="text-2xl font-bold text-white mb-4">Conversational data.</h3>
              <p className="text-gray-400 mb-6">
                Natural-language queries across every record, every email, every note. Hybrid keyword + pgvector rerank. Schema-aware prompting.
              </p>
              <StatusPill tone="info">Milestone M12</StatusPill>
            </div>

            <div className="bg-render-gray border border-gray-800 rounded-sm p-8 hover:border-tan transition-colors group relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-1 bg-tan transform origin-left scale-x-0 group-hover:scale-x-100 transition-transform" />
              <span className="text-tan mb-4 block text-xs font-bold tracking-widest uppercase">Wedge 03</span>
              <h3 className="text-2xl font-bold text-white mb-4">Agent autonomy with HITL.</h3>
              <p className="text-gray-400 mb-6">
                Default-suggest, opt-in autonomous per action type. Human-in-the-loop approval via in-app inbox, email magic-link, or iOS push.
              </p>
              <StatusPill tone="info">Milestone M13</StatusPill>
            </div>
          </div>
        </div>
      </section>

      {/* Integrated Logs & Monitoring Section */}
      <section className="max-w-[1400px] mx-auto px-6 py-24 border-t border-gray-800">
        <div className="grid md:grid-cols-2 gap-16 lg:gap-24 items-center">

          {/* Left Column: Text */}
          <div className="space-y-4">
            <h2 className="text-3xl lg:text-4xl font-semibold tracking-tight text-white max-w-sm">
              Integrated logs and monitoring for agents and workflows
            </h2>
            <p className="text-gray-400 text-lg leading-relaxed max-w-md">
              See critical metrics for all of your Offside infrastructure from day zero, and stream telemetry to external tools.
            </p>
            <Link href="/docs/observability" className="inline-flex items-center text-render-purpleLight hover:text-white transition-colors font-medium text-sm gap-1 group pt-2">
              Observability docs <span className="group-hover:translate-x-1 transition-transform">&rarr;</span>
            </Link>
          </div>

          {/* Right Column: Log Graphic */}
          <div className="rounded-md border border-gray-800 bg-[#0a0a0a] overflow-hidden shadow-2xl relative">
            <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:20px_20px]" />

            <div className="relative p-6 h-full flex flex-col">
              {/* Top controls */}
              <div className="flex gap-4 mb-6">
                <div className="bg-[#141414] border border-gray-700 rounded-sm px-3 py-1.5 text-xs text-gray-300 flex items-center gap-2">
                  All logs <span className="text-gray-500">v</span>
                </div>
                <div className="bg-[#141414] border border-gray-700 rounded-sm px-3 py-1.5 text-xs text-gray-500 flex-grow flex items-center gap-2">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8" /><path d="M21 21l-4.35-4.35" /></svg>
                  Search
                </div>
              </div>

              {/* Log rows */}
              <div className="space-y-3 font-mono text-[10px] sm:text-xs">
                <div className="flex items-start gap-4 text-gray-400">
                  <span className="shrink-0 w-32">Sept 10 18:58:02 PM</span>
                  <span className="w-4 h-4 rounded-full bg-render-purple/20 flex items-center justify-center shrink-0 mt-0.5"><span className="w-1.5 h-1.5 rounded-full bg-render-purpleLight" /></span>
                  <span className="text-gray-300">INFO</span>
                  <span className="truncate">[Hermes] Re-prompting LLM for schema alignment</span>
                </div>
                <div className="flex items-start gap-4 text-gray-400">
                  <span className="shrink-0 w-32">Sept 10 18:58:03 PM</span>
                  <span className="w-4 h-4 rounded-full bg-render-green/20 flex items-center justify-center shrink-0 mt-0.5"><span className="w-1.5 h-1.5 rounded-full bg-render-green" /></span>
                  <span className="text-gray-300">EXEC</span>
                  <span className="truncate">[OpenClaw] Webhook triggered from Salesforce</span>
                </div>
                <div className="flex items-start gap-4 text-gray-400">
                  <span className="shrink-0 w-32">Sept 10 18:58:05 PM</span>
                  <span className="w-4 h-4 rounded-full bg-render-green/20 flex items-center justify-center shrink-0 mt-0.5"><span className="w-1.5 h-1.5 rounded-full bg-render-green" /></span>
                  <span className="text-gray-300">DONE</span>
                  <span className="truncate">[Agent] Workflow completed successfully</span>
                </div>
              </div>

              {/* Hover Graph Overlay */}
              <div className="absolute right-4 bottom-4 bg-[#141414] border border-gray-700 rounded-sm p-4 w-48 shadow-[0_10px_30px_rgba(0,0,0,0.5)] z-10">
                <div className="text-xs font-semibold text-gray-300 mb-4">Token Usage</div>
                <div className="flex justify-between items-end h-16 relative">
                  <svg className="absolute inset-0 w-full h-full" preserveAspectRatio="none" viewBox="0 0 100 40">
                    <path d="M0,35 L10,25 L20,30 L30,15 L40,20 L50,5 L60,15 L70,10 L80,25 L90,15 L100,5" fill="none" stroke="var(--brand-tan)" strokeWidth="1.5" />
                    <path d="M0,40 L15,30 L30,35 L45,20 L60,25 L75,10 L90,20 L100,10" fill="none" stroke="#9b51e0" strokeWidth="1.5" />
                    <path d="M0,25 L20,35 L40,15 L60,30 L80,10 L100,20" fill="none" stroke="#45E67A" strokeWidth="1.5" />
                  </svg>
                </div>
              </div>
            </div>
          </div>

        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-800 bg-[#0a0a0a] pt-20 pb-8 px-6 text-sm">
        <div className="max-w-[1400px] mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-12 lg:gap-8 mb-16">
            {/* Logo and Newsletter */}
            <div className="lg:col-span-2 space-y-6">
              <Link href="/" className="flex items-center gap-2 group mb-6">
                <svg className="h-6 w-auto text-white group-hover:text-render-purple transition-colors" viewBox="0 0 103.8 72.8" xmlns="http://www.w3.org/2000/svg">
                  <path fill="currentColor" d="M67.5.2c-3.1,0-6,.4-8.9,1.1-2.3.6-4.6,1.4-6.7,2.4-2.1-1-4.4-1.8-6.7-2.4-2.9-.7-5.8-1.1-8.9-1.1C16.3.2,0,16.5,0,36.5s16.3,36.3,36.3,36.3,6-.4,8.9-1.1c-4-2.5-7.6-5.7-10.5-9.5-13.5-.8-24.2-12.1-24.2-25.8s10.7-25,24.2-25.8h1.6c1.7,0,3.4.2,5.1.5,3.9.8,7.4,2.4,10.5,4.7,1.5,1.1,2.8,2.3,4,3.7.4.4.7.8,1,1.2.6.8,1.2,1.6,1.7,2.5.3.4.5.9.8,1.3.3.6.6,1.2.9,1.8.3.8.6,1.6.9,2.4.1.4.2.8.4,1.2.1.5.2,1,.4,1.6.2.8.3,1.6.4,2.4,0,.8.1,1.6.1,2.5s0,1.6-.1,2.5-.2,1.6-.4,2.4c-.1.5-.2,1.1-.4,1.6-.1.4-.2.8-.4,1.2-.2.8-.6,1.6-.9,2.4-.3.6-.6,1.2-.9,1.8-.2.4-.5.9-.8,1.3-.5.9-1.1,1.7-1.7,2.5-.3.4-.6.8-1,1.2-1.2,1.4-2.5,2.6-4,3.7-1.5-1.1-2.8-2.3-4-3.7-3.9-4.5-6.3-10.4-6.3-16.9s2.4-12.4,6.3-16.9c-3-2.1-6.6-3.4-10.5-3.6-4,5.8-6.3,12.9-6.3,20.5s2.3,14.6,6.3,20.5c1.2,1.7,2.5,3.4,4,4.9,3,3.1,6.5,5.6,10.5,7.5,2.1,1,4.3,1.8,6.7,2.4,2.9.7,5.8,1.1,8.9,1.1,7.7,0,15-2.4,21.2-6.9l-6.1-8.5c-4,2.9-8.6,4.5-13.5,4.8h-1.6c-1.7,0-3.4-.2-5.1-.5,1.5-1.5,2.8-3.1,4-4.9,4-5.8,6.3-12.9,6.3-20.5s-2.3-14.7-6.3-20.5c-1.2-1.7-2.5-3.4-4-4.8,1.6-.3,3.4-.5,5.1-.5s1.1,0,1.6,0c13.5.8,24.2,12.1,24.2,25.8v35.7h10.5v-35.7C103.8,16.3,87.5,0,67.5,0h0v.2Z"></path>
                </svg>
                <span className="font-bold text-xl tracking-tight text-white">OffsideStudio</span>
              </Link>

              <div className="flex items-center gap-4 text-gray-400">
                <a href="#" className="hover:text-white transition-colors" aria-label="X (Twitter)"><svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"></path></svg></a>
                <a href="#" className="hover:text-white transition-colors" aria-label="GitHub"><svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"></path></svg></a>
                <a href="#" className="hover:text-white transition-colors" aria-label="Discord"><svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028 14.09 14.09 0 0 0 1.226-1.994.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.028zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"></path></svg></a>
              </div>

              <div className="pt-4 max-w-[280px]">
                <p className="text-xs text-gray-400 mb-3">Get product updates and news from Offside.</p>
                <div className="flex flex-col gap-2">
                  <input type="email" placeholder="Your email" className="w-full bg-[#111] border border-gray-800 rounded-sm px-3 py-2 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-render-purple transition-colors" />
                  <button className="bg-render-purple hover:bg-[#853ee0] text-white font-semibold rounded-sm px-4 py-2 text-sm transition-colors self-start w-fit">
                    Subscribe
                  </button>
                </div>
              </div>
            </div>

            {/* Links Columns */}
            <div className="space-y-4">
              <h4 className="text-white font-medium mb-6">Product</h4>
              <ul className="space-y-3 text-gray-400">
                <li><Link href="/pricing" className="hover:text-white transition-colors">Pricing</Link></li>
                <li><Link href="/marketplace" className="hover:text-white transition-colors">Agent Marketplace</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Orchestration</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Memory & DB</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Workflow SDK</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Enterprise</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Changelog</Link></li>
              </ul>
            </div>

            <div className="space-y-4">
              <h4 className="text-white font-medium mb-6">Solutions</h4>
              <ul className="space-y-3 text-gray-400">
                <li><Link href="#" className="hover:text-white transition-colors">Sales Agents</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Support Agents</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Marketing Agents</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Data Analysts</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Custom Agents</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Startups</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Agencies</Link></li>
              </ul>
            </div>

            <div className="space-y-4">
              <h4 className="text-white font-medium mb-6">Resources</h4>
              <ul className="space-y-3 text-gray-400">
                <li><Link href="#" className="hover:text-white transition-colors">Blog</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Support</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">System Status</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Become a Partner</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Integrations</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Brand Assets</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Security & Compliance</Link></li>
              </ul>
            </div>

            <div className="space-y-4">
              <h4 className="text-white font-medium mb-6">Company</h4>
              <ul className="space-y-3 text-gray-400">
                <li><Link href="#" className="hover:text-white transition-colors">About Us</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Careers</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">General Availability</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Terms of Service</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Privacy Policy</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Privacy Settings</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Contact Us</Link></li>
              </ul>
            </div>
          </div>

          {/* Bottom Bar */}
          <div className="border-t border-gray-800 pt-8 flex items-center justify-between text-xs text-gray-500">
            <p>© {new Date().getFullYear()} Offside Labs Inc.</p>
            <button className="text-gray-400 hover:text-white transition-colors" aria-label="Toggle dark mode">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
}
