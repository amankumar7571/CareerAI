"use client"

import { Badge } from "@/components/ui/badge"
import { Check, Circle, BookOpen, ExternalLink, AlertTriangle, Clock } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface RoadmapStep {
  name: string
  completed: boolean
}

interface SkillGap {
  skill: string
  course: string
  platform: string
  url: string
  duration?: string
}

interface PersonalRoadmapProps {
  steps: RoadmapStep[]
  skillGap: SkillGap
}

export function PersonalRoadmap({ steps, skillGap }: PersonalRoadmapProps) {
  const completedCount = steps.filter(s => s.completed).length

  return (
    <div className="flex flex-col h-full rounded-2xl border border-border bg-card p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-secondary">
            <BookOpen className="size-5 text-foreground" />
          </div>
          <h2 className="text-lg font-semibold text-foreground">Personal Roadmap</h2>
        </div>
        <span className="text-xs font-medium text-muted-foreground">
          {completedCount}/{steps.length} Complete
        </span>
      </div>

      {/* Roadmap Pipeline */}
      <div className="flex-1 flex flex-col gap-2">
        <div className="relative flex flex-col gap-0">
          {steps.map((step, index) => (
            <div key={index} className="flex items-start gap-3">
              {/* Vertical line connector */}
              <div className="flex flex-col items-center">
                <div className={cn(
                  "flex items-center justify-center size-6 rounded-full shrink-0 transition-colors",
                  step.completed 
                    ? "bg-foreground text-background" 
                    : "bg-secondary text-muted-foreground border border-border"
                )}>
                  {step.completed ? (
                    <Check className="size-3.5" strokeWidth={3} />
                  ) : (
                    <Circle className="size-2.5 fill-current" />
                  )}
                </div>
                {index < steps.length - 1 && (
                  <div className={cn(
                    "w-0.5 h-8",
                    step.completed ? "bg-foreground/50" : "bg-border"
                  )} />
                )}
              </div>
              <div className="pt-0.5 pb-4">
                <span className={cn(
                  "text-sm font-medium transition-colors",
                  step.completed ? "text-foreground" : "text-muted-foreground"
                )}>
                  {step.name}
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Skill Gap Section */}
        <div className="mt-auto pt-4 border-t border-border">
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle className="size-4 text-foreground" />
            <span className="text-sm font-semibold text-foreground">Next Action Recommender</span>
          </div>
          
          <div className="rounded-xl bg-secondary/30 border border-border p-4 hover:bg-secondary/50 transition-colors">
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1">
                <Badge className="rounded-full bg-foreground text-background border-0 px-2 py-0.5 text-xs mb-2 shadow-sm">
                  {skillGap.skill}
                </Badge>
                <p className="text-sm font-semibold text-foreground mb-1 leading-tight">{skillGap.course}</p>
                
                <div className="flex flex-wrap items-center gap-3 mt-2">
                  <span className="text-xs font-medium text-muted-foreground px-2 py-1 bg-background rounded-md border border-border">
                    {skillGap.platform}
                  </span>
                  
                  {skillGap.duration && (
                    <span className="flex items-center text-xs text-muted-foreground">
                      <Clock className="size-3 mr-1" />
                      {skillGap.duration}
                    </span>
                  )}
                </div>
              </div>
              <Button 
                size="sm" 
                className="shrink-0 bg-foreground hover:bg-foreground/90 text-background shadow-md"
                asChild
              >
                <a href={skillGap.url} target="_blank" rel="noopener noreferrer">
                  Enroll
                  <ExternalLink className="size-3 ml-1" />
                </a>
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
