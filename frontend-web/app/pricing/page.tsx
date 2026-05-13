import Link from "next/link";
import { Hairline } from "@offside/ui";

export default function PricingPage() {
  return (
    <div className="bg-render-dark text-white min-h-screen overflow-hidden font-sans relative">
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
            <Link href="/#product" className="hover:text-white transition-colors">Product</Link>
            <Link href="/pricing" className="text-white font-semibold relative after:absolute after:bottom-[-22px] after:left-0 after:w-full after:h-[2px] after:bg-white transition-colors">Pricing</Link>
            <Link href="/#customers" className="hover:text-white transition-colors">Customers</Link>
            <Link href="/#docs" className="hover:text-white transition-colors">Docs</Link>
            <Link href="/#templates" className="hover:text-white transition-colors">Templates</Link>
            <Link href="/#company" className="hover:text-white transition-colors">Company</Link>
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
      <div className="relative pt-24 pb-12 px-6 max-w-[1200px] mx-auto z-10">
        <h1 className="text-4xl md:text-6xl font-bold tracking-tight text-white mb-6 text-center">
          Simple, predictable pricing
        </h1>
        <p className="text-gray-400 max-w-2xl text-center mx-auto text-lg leading-relaxed">
          Whether you're a solo developer or a Fortune 500 company, we have a plan that scales with your infrastructure.
        </p>
      </div>

      {/* Grid Background Wrapper */}
      <div className="relative">
        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.05)_1px,transparent_1px)] bg-[size:60px_60px] [mask-image:linear-gradient(to_bottom,black_40%,transparent_100%)] pointer-events-none" />
        
        <div className="max-w-[1200px] mx-auto px-6 pb-32 relative z-10">
          
          {/* Render-style subtitle links */}
          <div className="mb-12 text-sm text-gray-300 hidden md:block">
            <p>Jump to <a href="#" className="underline hover:text-white transition-colors">workspace plans</a>, <a href="#" className="underline hover:text-white transition-colors">compute pricing</a>, and <a href="#" className="underline hover:text-white transition-colors">FAQs</a>.</p>
            <p className="mt-1">Are you a VC-funded startup? Get up to $100K in credits with <a href="#" className="underline hover:text-white transition-colors">Offside for Startups ↗</a></p>
          </div>

          {/* Pricing Grid */}
          <div className="grid md:grid-cols-3 gap-0 border-t border-l border-gray-800">
            
            {/* Pro Tier */}
            <div className="border-r border-b border-gray-800 bg-[#0a0a0a]/80 backdrop-blur-sm flex flex-col group transition-colors">
              <div className="bg-[#123E1E] p-8 h-40">
                <h3 className="text-2xl font-semibold mb-3">Pro</h3>
                <p className="text-gray-300 text-sm leading-relaxed pr-4">For individuals and small teams exploring open models.</p>
              </div>
              <div className="p-8 flex-grow">
                <div className="flex items-baseline gap-1 mb-8">
                  <span className="text-4xl font-semibold">$250</span>
                  <span className="text-gray-400 text-sm">/mo</span>
                </div>
                <Link href="/signup?plan=pro" className="block w-full text-center bg-render-green hover:bg-[#5cff8f] text-black font-semibold py-3 px-4 rounded-sm transition-colors mb-10 flex items-center justify-between">
                  <span>Get Started Free</span>
                  <span>&rarr;</span>
                </Link>
                <ul className="space-y-4 text-sm text-gray-300">
                  <li className="flex items-start gap-3">
                    <span className="text-render-green mt-0.5">✓</span>
                    <span>Access to 50+ open-source models</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-render-green mt-0.5">✓</span>
                    <span>1,000 requests per month</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-render-green mt-0.5">✓</span>
                    <span>Community Discord support</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-render-green mt-0.5">✓</span>
                    <span>Standard latency SLA</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-render-green mt-0.5">✓</span>
                    <span>1 GB Vector Storage</span>
                  </li>
                </ul>
              </div>
            </div>

            {/* Ultra Tier */}
            <div className="border-r border-b border-gray-800 bg-[#0a0a0a]/80 backdrop-blur-sm flex flex-col group transition-colors relative">
              <div className="absolute top-0 right-0 bg-render-purple text-white text-[10px] font-bold px-3 py-1 uppercase tracking-widest rounded-bl-sm z-10">
                Most Popular
              </div>
              <div className="bg-[#3D1466] p-8 h-40">
                <h3 className="text-2xl font-semibold mb-3">Ultra</h3>
                <p className="text-gray-300 text-sm leading-relaxed pr-4">For growing startups and production deployments.</p>
              </div>
              <div className="p-8 flex-grow">
                <div className="flex items-baseline gap-1 mb-8">
                  <span className="text-4xl font-semibold">$2500</span>
                  <span className="text-gray-400 text-sm">/mo</span>
                </div>
                <Link href="/signup?plan=ultra" className="block w-full text-center bg-[#b870f4] hover:bg-[#c991f6] text-black font-semibold py-3 px-4 rounded-sm transition-colors mb-10 flex items-center justify-between">
                  <span>Start 14-Day Trial</span>
                  <span>&rarr;</span>
                </Link>
                <ul className="space-y-4 text-sm text-gray-300">
                  <li className="flex items-start gap-3">
                    <span className="text-[#b870f4] mt-0.5">✓</span>
                    <span>Uncapped model requests</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-[#b870f4] mt-0.5">✓</span>
                    <span>Sub-50ms latency globally</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-[#b870f4] mt-0.5">✓</span>
                    <span>Priority email support</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-[#b870f4] mt-0.5">✓</span>
                    <span>Custom domain integration</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-[#b870f4] mt-0.5">✓</span>
                    <span>100 GB Vector Storage</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-[#b870f4] mt-0.5">✓</span>
                    <span>Visual Pipeline Builder</span>
                  </li>
                </ul>
              </div>
            </div>

            {/* Enterprise Tier */}
            <div className="border-r border-b border-gray-800 bg-[#0a0a0a]/80 backdrop-blur-sm flex flex-col group transition-colors">
              <div className="bg-[#2A2A2A] p-8 h-40">
                <h3 className="text-2xl font-semibold mb-3">Enterprise</h3>
                <p className="text-gray-300 text-sm leading-relaxed pr-4">For large organizations with strict compliance and scale needs.</p>
              </div>
              <div className="p-8 flex-grow">
                <div className="flex items-baseline gap-1 mb-8">
                  <span className="text-4xl font-semibold">Custom pricing</span>
                </div>
                <Link href="/contact" className="block w-full text-center bg-gray-300 hover:bg-white text-black font-semibold py-3 px-4 rounded-sm transition-colors mb-10 flex items-center justify-between">
                  <span>Contact Sales</span>
                  <span>&rarr;</span>
                </Link>
                <ul className="space-y-4 text-sm text-gray-300">
                  <li className="flex items-start gap-3">
                    <span className="text-gray-400 mt-0.5">✓</span>
                    <span>VPC Peering & Single-Tenant deployments</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-gray-400 mt-0.5">✓</span>
                    <span>SOC2 / HIPAA / GDPR compliance</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-gray-400 mt-0.5">✓</span>
                    <span>Dedicated Account Manager</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-gray-400 mt-0.5">✓</span>
                    <span>99.99% Uptime SLA</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-gray-400 mt-0.5">✓</span>
                    <span>Unlimited Vector Storage</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-gray-400 mt-0.5">✓</span>
                    <span>SSO / SAML integration</span>
                  </li>
                </ul>
              </div>
            </div>

          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-gray-800 py-12 text-center text-gray-500 text-sm">
        <p>
          Part of the <a href="https://platform.offside.ai" className="text-white hover:text-render-purple transition-colors">Offside Studio Suite</a>. Engineer-to-engineer.
        </p>
        <p className="mt-2">
          See <Link href="/brand" className="text-white hover:text-render-purple transition-colors">brand tokens</Link> and <code>PLAN.md</code>.
        </p>
      </footer>
    </div>
  );
}
