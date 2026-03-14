"use client"

import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { Briefcase, TrendingUp, ArrowUpRight, Map as MapIcon } from "lucide-react"
import { Button } from "@/components/ui/button"

interface RecommendedCareerProps {
  title: string
  confidence: number
  description: string
  salaryRange: string
  growth: string
  isTopMatch?: boolean
  onViewDetails?: () => void
  isActiveLoading?: boolean
}

export function RecommendedCareer({ 
  title, 
  confidence, 
  description, 
  salaryRange,
  growth,
  isTopMatch = false,
  onViewDetails,
  isActiveLoading = false
}: RecommendedCareerProps) {
  return (
    <div className="flex flex-col h-full rounded-2xl border border-border bg-card p-6 hover:border-foreground/20 transition-colors">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-secondary">
            <Briefcase className="size-5 text-foreground" />
          </div>
          <h2 className="text-lg font-semibold text-foreground truncate max-w-[160px]" title={title}>{title}</h2>
        </div>
        {isTopMatch && (
            <Badge className="rounded-full bg-foreground text-background border-0 px-3 py-1 whitespace-nowrap">
            Top Match
            </Badge>
        )}
      </div>

      <div className="flex-1 flex flex-col gap-4">
        <div>
          <p className="text-sm text-muted-foreground leading-relaxed line-clamp-3" title={description}>{description}</p>
        </div>

        {/* Confidence Level */}
        <div className="space-y-2 mt-auto">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground font-medium">AI Match</span>
            <span className="text-foreground font-bold text-lg">{confidence}%</span>
          </div>
          <Progress value={confidence} className="h-2 bg-secondary [&>div]:bg-foreground" />
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 gap-3 mt-2">
          <div className="rounded-xl bg-secondary/50 p-3">
            <span className="text-xs text-muted-foreground block mb-1">Avg. Salary</span>
            <span className="text-sm font-semibold text-foreground">{salaryRange}</span>
          </div>
          <div className="rounded-xl bg-secondary/50 p-3">
            <div className="flex items-center gap-1">
              <TrendingUp className="size-3 text-foreground" />
              <span className="text-xs text-muted-foreground">Job Growth</span>
            </div>
            <span className="text-sm font-semibold text-foreground">{growth}</span>
          </div>
        </div>

        <Button 
            disabled={isActiveLoading}
            onClick={onViewDetails}
            className="w-full mt-2 bg-foreground hover:bg-foreground/90 text-background"
        >
          {isActiveLoading ? (
             <>
               <div className="w-4 h-4 border-2 border-background border-t-transparent rounded-full animate-spin mr-2"></div>
               Analyzing Gaps...
             </>
          ) : (
             <>
                Generate Roadmap
                <MapIcon className="size-4 ml-2" />
             </>
          )}
        </Button>
      </div>
    </div>
  )
}
