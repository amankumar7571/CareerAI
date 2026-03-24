import { Link } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { ArrowRight, Sparkles, Target, BookOpen, TrendingUp, ChevronRight, Check } from "lucide-react"

const features = [
  {
    icon: Sparkles,
    title: "Resume Skill Extraction",
    description: "Upload a PDF or DOCX resume and extract structured skills with Gemini, spaCy, and keyword fallback logic.",
  },
  {
    icon: Target,
    title: "ML Career Matching",
    description: "Compare your profile against six modeled career paths using the trained scikit-learn predictor.",
  },
  {
    icon: BookOpen,
    title: "Personal Roadmaps",
    description: "Turn missing skills into a clear learning plan with recommended courses and next-step guidance.",
  },
  {
    icon: TrendingUp,
    title: "Profile-Aware Guidance",
    description: "Combine resume skills, CGPA, interests, and project context to support better career planning.",
  },
]

const stats = [
  { value: "6", label: "Career roles modeled" },
  { value: "57", label: "Skills recognized" },
  { value: "3", label: "Skill extraction layers" },
  { value: "2", label: "Core app layers" },
]

const testimonials = [
  {
    quote: "Upload a resume in PDF or DOCX and generate a structured skill snapshot in seconds.",
    author: "Step 1",
    role: "Resume parsing and NLP extraction",
  },
  {
    quote: "Review the top predicted roles with model confidence and AI-enriched role summaries.",
    author: "Step 2",
    role: "Machine learning prediction",
  },
  {
    quote: "Generate a personalized roadmap to see missing skills, recommended courses, and what to learn next.",
    author: "Step 3",
    role: "Roadmap planning",
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
              <a href="#workflow" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                Workflow
              </a>
              <a href="#architecture" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                Architecture
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
            <span className="text-xs font-medium text-muted-foreground">Resume intelligence for career planning</span>
          </div>
          <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold text-foreground tracking-tight mb-6 text-balance">
            Upload your resume. Discover your next role.
          </h1>
          <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto mb-10 text-pretty">
            CareerAI extracts your skills, predicts the strongest-fit career roles, and builds a personalized roadmap for what to learn next.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/register">
              <Button size="lg" className="bg-foreground text-background hover:bg-foreground/90 gap-2 px-8">
                Start Career Analysis
                <ArrowRight className="size-4" />
              </Button>
            </Link>
            <a href="#workflow">
              <Button variant="outline" size="lg" className="gap-2">
                See How It Works
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
              Built around the actual career guidance workflow
            </h2>
            <p className="text-muted-foreground max-w-xl mx-auto">
              Every major screen maps to the product pipeline documented in the walkthrough: upload, extract, predict, and plan.
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
      <section id="workflow" className="py-24 px-6 bg-secondary/20">
        <div className="mx-auto max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
              Three steps from resume to roadmap
            </h2>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { step: "01", title: "Upload Resume", desc: "Submit a PDF or DOCX file for parsing, secure storage, and skill extraction." },
              { step: "02", title: "Review Role Matches", desc: "See the top predicted career paths with model confidence and enriched role summaries." },
              { step: "03", title: "Build Your Roadmap", desc: "Generate missing-skill recommendations and suggested courses for the role you want to pursue." },
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
      <section className="py-24 px-6">
        <div className="mx-auto max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
              The guided user flow
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
      <section id="architecture" className="py-24 px-6 bg-secondary/20">
        <div className="mx-auto max-w-4xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
              Full-stack architecture
            </h2>
          </div>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="p-8 rounded-xl border border-border bg-card">
              <div className="text-sm font-semibold text-muted-foreground mb-2">Frontend</div>
              <div className="text-4xl font-bold text-foreground mb-4">React 19</div>
              <p className="text-sm text-muted-foreground mb-6">Vite-powered pages for landing, authentication, and dashboard workflows.</p>
              <ul className="space-y-3 mb-8">
                {["React 19 + Vite 5", "Tailwind CSS v4 + shadcn/ui", "React Router v7 navigation", "Axios API integration"].map((item) => (
                  <li key={item} className="flex items-center gap-2 text-sm text-muted-foreground">
                     <Check className="size-4 text-accent" />
                     {item}
                  </li>
                ))}
              </ul>
              <a href="#features">
                <Button variant="outline" className="w-full">Review Features</Button>
              </a>
            </div>
            <div className="p-8 rounded-xl border border-foreground bg-card shadow-lg">
              <div className="text-sm font-semibold text-accent mb-2">Backend + AI</div>
              <div className="text-4xl font-bold text-foreground mb-4">FastAPI</div>
              <p className="text-sm text-muted-foreground mb-6">API, authentication, ML inference, roadmap generation, and upload orchestration.</p>
              <ul className="space-y-3 mb-8">
                {["FastAPI + SQLAlchemy 2.0", "SQLite dev / PostgreSQL prod", "scikit-learn role prediction", "Gemini + spaCy skill extraction", "Local or S3-ready file storage"].map((item) => (
                  <li key={item} className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Check className="size-4 text-accent" />
                    {item}
                  </li>
                ))}
              </ul>
              <Link to="/register">
                <Button className="w-full bg-foreground text-background hover:bg-foreground/90 shadow-md">Create Account</Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 px-6">
        <div className="mx-auto max-w-3xl text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
             Ready to plan your next move?
          </h2>
          <p className="text-muted-foreground mb-8 text-lg">
             Create an account, upload your resume, and let CareerAI turn your current skills into a clearer career direction.
          </p>
          <Link to="/register">
            <Button size="lg" className="bg-foreground text-background hover:bg-foreground/90 gap-2 px-8">
              Start with CareerAI
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
