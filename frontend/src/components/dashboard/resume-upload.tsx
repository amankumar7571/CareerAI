import { useState, useCallback, useRef } from "react"
import { Upload, FileText, CheckCircle2, X } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

export function ResumeUpload({ 
  extractedSkills, 
  onFileUpload, 
  uploadingResume, 
  resumeError, 
  resumeSuccess 
}) {
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef(null)

  const handleDragOver = useCallback((e) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) {
      triggerUpload(file)
    }
  }, [])

  const handleFileSelect = useCallback((e) => {
    const file = e.target.files?.[0]
    if (file) {
      triggerUpload(file)
    }
  }, [])

  const triggerUpload = (file) => {
    if (onFileUpload) {
      const e = { target: { files: [file] } }
      onFileUpload(e)
    }
  }

  return (
    <div className="rounded-2xl border border-border bg-card p-6">
      <div className="flex items-center gap-2 mb-4">
        <FileText className="size-5 text-foreground" />
        <h2 className="text-lg font-semibold text-foreground">Resume Upload</h2>
      </div>
      
      {/* Upload Area */}
      <label
        className={cn(
          "relative flex flex-col items-center justify-center w-full h-40 rounded-xl border-2 border-dashed cursor-pointer transition-all duration-200",
          isDragging 
            ? "border-accent bg-accent/5" 
            : "border-border hover:border-accent/50 hover:bg-secondary/50",
          uploadingResume && "opacity-50 pointer-events-none"
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          type="file"
          className="sr-only"
          accept=".pdf,.doc,.docx"
          onChange={handleFileSelect}
          ref={fileInputRef}
          disabled={uploadingResume}
        />
        
        {uploadingResume ? (
          <div className="flex flex-col items-center gap-2">
            <div className="w-10 h-10 border-4 border-foreground border-t-transparent rounded-full animate-spin"></div>
            <span className="text-sm font-medium text-foreground">Processing document...</span>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2">
            <div className={cn(
              "p-3 rounded-full transition-colors",
              isDragging ? "bg-accent/10" : "bg-secondary"
            )}>
              <Upload className={cn(
                "size-6 transition-colors",
                isDragging ? "text-accent" : "text-muted-foreground"
              )} />
            </div>
            <div className="text-center">
              <span className="text-sm font-medium text-foreground">Securely upload credentials</span>
              <p className="text-xs text-muted-foreground mt-1">PDF or DOCX (Max 5MB). NLP processing is strictly confidential.</p>
            </div>
          </div>
        )}
      </label>

      {resumeError && (
        <div className="mt-4 p-3 bg-destructive/10 border border-destructive/50 rounded-lg text-destructive text-sm text-center">
          {resumeError}
        </div>
      )}

      {resumeSuccess && (
        <div className="mt-4 flex items-center gap-2 text-emerald-500">
          <CheckCircle2 className="size-5" />
          <span className="font-semibold text-sm">{resumeSuccess}</span>
        </div>
      )}

      {/* Extracted Skills */}
      {extractedSkills.length > 0 && (
        <div className="mt-6">
          <div className="flex items-center gap-2 mb-3">
            <div className="h-px flex-1 bg-border" />
            <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">NLP Extracted Skills</span>
            <div className="h-px flex-1 bg-border" />
          </div>
          <div className="flex flex-wrap gap-2">
            {extractedSkills.map((skill, index) => (
              <Badge 
                key={index}
                className="rounded-full px-4 py-1.5 text-sm font-medium border border-border bg-secondary text-foreground transition-transform hover:scale-105 hover:bg-foreground hover:text-background"
              >
                {skill}
              </Badge>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
