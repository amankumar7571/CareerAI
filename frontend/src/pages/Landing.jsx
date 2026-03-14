import { Link } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { ArrowRight, Sparkles, Target, BookOpen, TrendingUp, ChevronRight, Check } from "lucide-react"

const features = [
  {
    icon: Sparkles,
    title: "AI-Powered Analysis",
    description: "Advanced NLP extracts your skills and matches them with ideal career paths.",
  },
  {
    icon: Target,
    title: "Career Matching",
    description: "Get personalized job recommendations with confidence scores up to 99%.",
  },
  {
    icon: BookOpen,
    title: "Learning Roadmaps",
    description: "Curated courses and certifications to fill your skill gaps.",
  },
  {
    icon: TrendingUp,
    title: "Growth Insights",
    description: "Real-time salary data and industry trends to guide your decisions.",
  },
]

const stats = [
  { value: "50K+", label: "Career paths analyzed" },
  { value: "98%", label: "Match accuracy" },
  { value: "10K+", label: "Users guided" },
  { value: "500+", label: "Partner courses" },
]

const testimonials = [
  {
    quote: "CareerAI helped me transition from marketing to product management in just 6 months.",
    author: "Sarah Chen",
    role: "Product Manager at Stripe",
  },
  {
    quote: "The skill gap analysis was spot-on. I knew exactly what to learn next.",
    author: "Marcus Johnson",
    role: "Software Engineer at Google",
  },
  {
    quote: "Finally, a career tool that actually understands the tech landscape.",
    author: "Elena Rodriguez",
    role: "Data Scientist at Meta",
  },
]

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 border-b border-border bg-background/80 backdrop-blur-md">
        <div className="mx-auto max-w-6xl px-6 py-4">
          <div className="flex items-center justify-between">
            <Link to="/" className="flex items-center gap-2">
              <div className="p-1.5 rounded-md bg-foreground">
                <Sparkles className="size-4 text-background" />
              </div>
              <span className="text-lg font-semibold text-foreground">CareerAI</span>
            </Link>
            <div className="hidden md:flex items-center gap-8">
              <a href="#features" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                Features
              </a>
              <a href="#testimonials" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                Testimonials
              </a>
              <a href="#pricing" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                Pricing
              </a>
            </div>
            <div className="flex items-center gap-3">
              <Link to="/login">
                <Button variant="ghost" size="sm" className="text-muted-foreground hover:text-foreground">
                  Log in
                </Button>
              </Link>
              <Link to="/register">
                <Button size="sm" className="bg-foreground text-background hover:bg-foreground/90">
                  Get Started
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6">
        <div className="mx-auto max-w-4xl text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-border bg-secondary/50 mb-8">
            <span className="size-1.5 rounded-full bg-accent animate-pulse" />
            <span className="text-xs font-medium text-muted-foreground">Next-Generation Career Intelligence</span>
          </div>
          <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold text-foreground tracking-tight mb-6 text-balance">
            Accelerate your tech career with AI precision
          </h1>
          <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto mb-10 text-pretty">
            Upload your professional resume and let our proprietary AI models deeply analyze your skill set, map optimal career trajectories, and generate a competitive learning roadmap.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/register">
              <Button size="lg" className="bg-foreground text-background hover:bg-foreground/90 gap-2 px-8">
                Start Free Analysis
                <ArrowRight className="size-4" />
              </Button>
            </Link>
            <a href="#features">
              <Button variant="outline" size="lg" className="gap-2">
                Explore the Technology
                <ChevronRight className="size-4" />
              </Button>
            </a>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 px-6 border-y border-border">
        <div className="mx-auto max-w-6xl">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat) => (
              <div key={stat.label} className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-foreground mb-1">{stat.value}</div>
                <div className="text-sm text-muted-foreground">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 px-6">
        <div className="mx-auto max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
              Enterprise-grade tools for personal career growth
            </h2>
            <p className="text-muted-foreground max-w-xl mx-auto">
              Our advanced machine learning platform leverages the latest generation of LLMs to provide comprehensive insights and actionable strategy for ambitious professionals.
            </p>
          </div>
          <div className="grid md:grid-cols-2 gap-6">
            {features.map((feature) => (
              <div
                key={feature.title}
                className="p-6 rounded-xl border border-border bg-card hover:bg-secondary/30 transition-colors"
              >
                <div className="p-2 rounded-lg bg-secondary w-fit mb-4">
                  <feature.icon className="size-5 text-foreground" />
                </div>
                <h3 className="text-lg font-semibold text-foreground mb-2">{feature.title}</h3>
                <p className="text-sm text-muted-foreground">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-24 px-6 bg-secondary/20">
        <div className="mx-auto max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
              Three steps to competitive advantage
            </h2>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { step: "01", title: "Upload Credentials", desc: "Submit your resume for an instant, deep NLP assessment." },
              { step: "02", title: "Review Insights", desc: "Navigate your top 3 machine-predicted career trajectories with salary forecasts." },
              { step: "03", title: "Execute Strategy", desc: "Follow dynamically generated cert/course roadmaps to bridge crucial skill gaps." },
            ].map((item) => (
              <div key={item.step} className="text-center">
                <div className="text-5xl font-bold text-border mb-4">{item.step}</div>
                <h3 className="text-xl font-semibold text-foreground mb-2">{item.title}</h3>
                <p className="text-sm text-muted-foreground">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section id="testimonials" className="py-24 px-6">
        <div className="mx-auto max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
              Trusted by professionals worldwide
            </h2>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            {testimonials.map((t) => (
              <div key={t.author} className="p-6 rounded-xl border border-border bg-card">
                <p className="text-foreground mb-6 font-medium leading-relaxed">{`"${t.quote}"`}</p>
                <div>
                  <div className="font-semibold text-foreground">{t.author}</div>
                  <div className="text-sm text-muted-foreground">{t.role}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="py-24 px-6 bg-secondary/20">
        <div className="mx-auto max-w-4xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
              Transparent investment
            </h2>
          </div>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="p-8 rounded-xl border border-border bg-card">
              <div className="text-sm font-semibold text-muted-foreground mb-2">Essential</div>
              <div className="text-4xl font-bold text-foreground mb-4">$0</div>
              <p className="text-sm text-muted-foreground mb-6">Evaluate the platform risk-free.</p>
              <ul className="space-y-3 mb-8">
                {["1 deep resume analysis", "Top 3 optimal career matches", "Static keyword extraction"].map((item) => (
                  <li key={item} className="flex items-center gap-2 text-sm text-muted-foreground">
                     <Check className="size-4 text-accent" />
                     {item}
                  </li>
                ))}
              </ul>
              <Link to="/register">
                <Button variant="outline" className="w-full">Get Started</Button>
              </Link>
            </div>
            <div className="p-8 rounded-xl border border-foreground bg-card shadow-lg relative">
              <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-foreground text-background text-xs font-medium">
                Professional
              </div>
              <div className="text-sm font-semibold text-accent mb-2">Pro</div>
              <div className="text-4xl font-bold text-foreground mb-4">$19<span className="text-lg font-normal text-muted-foreground">/mo</span></div>
              <p className="text-sm text-muted-foreground mb-6">Designed for ambitious career advancement.</p>
              <ul className="space-y-3 mb-8">
                {["Unlimited AI analyses", "Gemini 1.5 Flash parsing", "Dynamic deep-learning roadmaps", "Direct enrollment routing", "High-priority prediction cues"].map((item) => (
                  <li key={item} className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Check className="size-4 text-accent" />
                    {item}
                  </li>
                ))}
              </ul>
              <Link to="/register">
                <Button className="w-full bg-foreground text-background hover:bg-foreground/90 shadow-md">Start 14-Day Free Trial</Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 px-6">
        <div className="mx-auto max-w-3xl text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
             Ready to secure your future?
          </h2>
          <p className="text-muted-foreground mb-8 text-lg">
             Leverage military-grade machine learning to outmaneuver the competition.
          </p>
          <Link to="/register">
            <Button size="lg" className="bg-foreground text-background hover:bg-foreground/90 gap-2 px-8">
              Get Started Free
              <ArrowRight className="size-4" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-12 px-6">
        <div className="mx-auto max-w-6xl">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-2">
              <div className="p-1.5 rounded-md bg-foreground">
                <Sparkles className="size-4 text-background" />
              </div>
              <span className="text-lg font-semibold text-foreground">CareerAI</span>
            </div>
            <div className="flex items-center gap-6 text-sm text-muted-foreground">
              <Link to="#" className="hover:text-foreground transition-colors">Privacy</Link>
              <Link to="#" className="hover:text-foreground transition-colors">Terms</Link>
              <Link to="#" className="hover:text-foreground transition-colors">Contact</Link>
            </div>
            <p className="text-sm text-muted-foreground">
              2026 CareerAI. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
