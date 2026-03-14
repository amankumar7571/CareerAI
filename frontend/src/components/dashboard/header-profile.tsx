import { useState, useEffect } from "react"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Sparkles, Bell, Settings, LogOut, User, Shield, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"

interface HeaderProfileProps {
  userName: string
  role: string
  bio: string
  avatarUrl?: string
  user?: any
  onUpdateProfile?: (data: any) => Promise<{success: boolean, error?: string}>
}

export function HeaderProfile({ userName, role, bio, avatarUrl, user, onUpdateProfile }: HeaderProfileProps) {
  const [cgpa, setCgpa] = useState(user?.cgpa?.toString() || "")
  const [interests, setInterests] = useState(user?.interests || "")
  const [isUpdating, setIsUpdating] = useState(false)
  const [updateMsg, setUpdateMsg] = useState("")

  useEffect(() => {
    if (user) {
      setCgpa(user.cgpa?.toString() || "")
      setInterests(user.interests || "")
    }
  }, [user])

  const handleUpdate = async () => {
    if (!onUpdateProfile) return
    setIsUpdating(true)
    setUpdateMsg("")
    const res = await onUpdateProfile({
      cgpa: cgpa ? parseFloat(cgpa) : null,
      interests: interests || null
    })
    setIsUpdating(false)
    if (res.success) {
      setUpdateMsg("Profile updated successfully")
    } else {
      setUpdateMsg(res.error || "Failed to update profile")
    }
  }

  return (
    <div className="flex items-center justify-between rounded-2xl border border-border bg-card p-6 shadow-sm">
      <div className="flex items-center gap-5">
        <Avatar className="size-16 ring-2 ring-border">
          <AvatarImage src={avatarUrl} alt={userName} />
          <AvatarFallback className="bg-secondary text-foreground text-lg font-semibold">
            {userName.split(" ").map(n => n[0]).join("")}
          </AvatarFallback>
        </Avatar>
        <div className="flex flex-col gap-1.5">
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-semibold text-foreground">{userName}</h1>
            <Badge className="rounded-full bg-foreground text-background border-0 px-3 py-0.5 text-xs">
              <Sparkles className="size-3 mr-1" />
              AI Analyzed
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground font-medium">{role}</p>
          <p className="text-sm text-muted-foreground/80 max-w-md">{bio}</p>
        </div>
      </div>
      <div className="flex items-center gap-3">
        
        {/* Notifications Popover */}
        <Popover>
          <PopoverTrigger asChild>
            <Button variant="ghost" size="icon" className="relative text-muted-foreground hover:text-foreground">
              <Bell className="size-5" />
              <span className="absolute top-1.5 right-1.5 size-2 rounded-full bg-foreground"></span>
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-80 p-0" align="end">
            <div className="flex flex-col">
              <div className="bg-secondary/50 px-4 py-3 border-b border-border flex justify-between items-center">
                 <h3 className="font-semibold text-sm">Notifications</h3>
                 <span className="text-xs text-muted-foreground">2 New</span>
              </div>
              <div className="p-2 space-y-1">
                <div className="flex gap-3 items-start p-2 rounded-lg hover:bg-secondary/40 transition-colors">
                  <div className="size-8 rounded-full bg-foreground/10 flex items-center justify-center shrink-0">
                    <Sparkles className="size-4 text-foreground" />
                  </div>
                  <div>
                    <p className="text-sm font-medium">Deep Analysis Complete</p>
                    <p className="text-xs text-muted-foreground">Generated 3 optimal career trajectories with projected 2025 analytics.</p>
                  </div>
                </div>
                <div className="flex gap-3 items-start p-2 rounded-lg hover:bg-secondary/40 transition-colors">
                  <div className="size-8 rounded-full bg-foreground/10 flex items-center justify-center shrink-0">
                    <Bell className="size-4 text-foreground" />
                  </div>
                  <div>
                    <p className="text-sm font-medium">Credentials Parsed Successfully</p>
                    <p className="text-xs text-muted-foreground">NLP engine isolated 12 verified technical competencies.</p>
                  </div>
                </div>
              </div>
            </div>
          </PopoverContent>
        </Popover>

        {/* Settings Dialog */}
        <Dialog>
          <DialogTrigger asChild>
            <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground">
              <Settings className="size-5" />
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>Account Settings</DialogTitle>
              <DialogDescription>
                Manage your profile and application preferences.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="flex items-center gap-4 rounded-lg border p-4">
                 <User className="size-5 text-muted-foreground" />
                 <div className="flex-1 space-y-1">
                   <p className="text-sm font-medium leading-none">Profile Info</p>
                   <p className="text-sm text-muted-foreground">{userName}</p>
                 </div>
              </div>
              <div className="space-y-4 rounded-lg border p-4">
                <div className="flex items-center gap-4 mb-2">
                   <User className="size-5 text-muted-foreground" />
                   <div className="space-y-1">
                     <p className="text-sm font-medium leading-none">Career Profile Options</p>
                     <p className="text-sm text-muted-foreground">Improve AI matching accuracy</p>
                   </div>
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="cgpa">CGPA (0 - 10)</Label>
                  <Input 
                    id="cgpa" 
                    type="number" 
                    step="0.01" 
                    min="0" 
                    max="10" 
                    placeholder="e.g. 8.5" 
                    value={cgpa} 
                    onChange={(e: any) => setCgpa(e.target.value)} 
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="interests">Interests</Label>
                  <Input 
                    id="interests" 
                    placeholder="e.g. AI, Web Development" 
                    value={interests} 
                    onChange={(e: any) => setInterests(e.target.value)} 
                  />
                </div>
                <Button onClick={handleUpdate} disabled={isUpdating} className="w-full">
                  {isUpdating && <Loader2 className="mr-2 size-4 animate-spin" />}
                  Save Profile
                </Button>
                {updateMsg && <p className={`text-xs text-center mt-2 ${updateMsg.includes('Failed') ? 'text-red-500' : 'text-green-500'}`}>{updateMsg}</p>}
              </div>
              <Button variant="destructive" className="w-full mt-4" onClick={() => {
                localStorage.removeItem('token');
                window.location.reload();
              }}>
                <LogOut className="size-4 mr-2" />
                Sign Out
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  )
}
