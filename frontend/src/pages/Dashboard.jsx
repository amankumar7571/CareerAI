import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '@/lib/api';
import { Sparkles, LogOut, Cpu } from 'lucide-react';
import { Button } from '@/components/ui/button';

import { HeaderProfile } from "@/components/dashboard/header-profile"
import { ResumeUpload } from "@/components/dashboard/resume-upload"
import { RecommendedCareer } from "@/components/dashboard/recommended-career"
import { PersonalRoadmap } from "@/components/dashboard/personal-roadmap"

export default function Dashboard() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  
  // Profile messages
  const [error, setError] = useState('');
  
  // Resume upload states
  const [uploadingResume, setUploadingResume] = useState(false);
  const [resumeError, setResumeError] = useState('');
  const [resumeSuccess, setResumeSuccess] = useState('');
  const [extractedSkills, setExtractedSkills] = useState([]);

  // Prediction stats
  const [predicting, setPredicting] = useState(false);
  const [predictionResult, setPredictionResult] = useState(null);
  
  // Roadmap stats
  const [generatingRoadmap, setGeneratingRoadmap] = useState(false);
  const [roadmap, setRoadmap] = useState(null);
  const [activeRoadmapRole, setActiveRoadmapRole] = useState(null);

  const navigate = useNavigate();

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          navigate('/login');
          return;
        }
        const response = await api.get('/api/auth/me', {
          headers: { Authorization: `Bearer ${token}` }
        });
        setUser(response.data);
      } catch (err) {
        if (err.response?.status === 401) {
          localStorage.removeItem('token');
          navigate('/login');
        }
        setError('Failed to load profile');
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [navigate]);

  const handleUpdateProfile = async (profileData) => {
    try {
      const token = localStorage.getItem('token');
      const response = await api.put('/api/profile/update', profileData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser(response.data);
      return { success: true };
    } catch (err) {
      return { success: false, error: err.response?.data?.detail || 'Failed to update profile' };
    }
  };

  const handleResumeUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.pdf') && !file.name.endsWith('.docx')) {
      setResumeError('Please upload a PDF or DOCX file.');
      return;
    }

    setResumeError('');
    setResumeSuccess('');
    setUploadingResume(true);
    setExtractedSkills([]);
    setPredictionResult(null);
    setRoadmap(null);

    const token = localStorage.getItem('token');
    const uploadForm = new FormData();
    uploadForm.append('file', file);

    try {
      const response = await api.post('/api/resume/upload', uploadForm, {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });
      setResumeSuccess(response.data.message);
      setExtractedSkills(response.data.extracted_skills || []);
    } catch (err) {
      setResumeError(err.response?.data?.detail || 'Failed to upload resume.');
    } finally {
      setUploadingResume(false);
    }
  };

  const handlePredictCareer = async () => {
    if (extractedSkills.length === 0) return;
    setPredicting(true);
    setRoadmap(null);
    try {
      const token = localStorage.getItem('token');
      const response = await api.post('/api/prediction/predict', extractedSkills, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPredictionResult(response.data);
    } catch (err) {
      setResumeError(err.response?.data?.detail || 'Failed to predict career.');
    } finally {
      setPredicting(false);
    }
  };

  const handleGenerateRoadmap = async (roleOverride) => {
    const roleToGenerate = roleOverride || predictionResult?.top_prediction;
    if (!predictionResult || extractedSkills.length === 0 || !roleToGenerate) return;
    
    setGeneratingRoadmap(true);
    setActiveRoadmapRole(roleToGenerate);
    
    try {
      const token = localStorage.getItem('token');
      const response = await api.post(
        `/api/roadmap/generate?predicted_role=${encodeURIComponent(roleToGenerate)}`,
        extractedSkills,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      setRoadmap(response.data);
      setTimeout(() => {
        window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
      }, 100);
    } catch (err) {
      setResumeError(err.response?.data?.detail || 'Failed to generate roadmap.');
    } finally {
      setGeneratingRoadmap(false);
      setActiveRoadmapRole(null);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="w-16 h-16 border-4 border-foreground border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  // Transform backend roadmap data to UI format
  const roadmapSteps = roadmap ? [
    ...roadmap.existing_skills.map(s => ({ name: s, completed: true })),
    ...roadmap.recommended_courses.map(r => ({ name: r.skill, completed: false }))
  ] : [];

  const firstSkillGap = roadmap?.recommended_courses[0] || {
    skill: "Analysis Required",
    course: "Pending further analysis",
    platform: "-",
    url: "#"
  };

  return (
    <div className="min-h-screen bg-background pb-12">
      {/* Navigation Bar */}
      <nav className="sticky top-0 z-50 border-b border-border bg-background/80 backdrop-blur-md mb-8">
        <div className="mx-auto max-w-7xl px-6 py-4">
          <div className="flex items-center justify-between">
            <Link to="/" className="flex items-center gap-2">
              <div className="p-1.5 rounded-md bg-foreground">
                <Sparkles className="size-4 text-background" />
              </div>
              <span className="text-lg font-semibold text-foreground">CareerAI</span>
            </Link>
            <div className="hidden md:flex items-center gap-8">
              <Link to="/dashboard" className="text-sm font-medium text-foreground">Dashboard</Link>
            </div>
            <Button variant="ghost" size="sm" onClick={handleLogout} className="text-muted-foreground hover:text-foreground gap-2">
              <LogOut className="size-4" />
              Sign out
            </Button>
          </div>
        </div>
      </nav>

      <main className="mx-auto max-w-7xl px-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Header Profile Section */}
          <div className="lg:col-span-12">
            <HeaderProfile
              userName={user?.name || "User"}
              role={user?.email || "No email"}
              bio={error || "Welcome to CareerAI. Upload a resume to extract skills, predict roles, and generate a roadmap."}
              avatarUrl={`https://ui-avatars.com/api/?name=${user?.name || 'U'}&background=random`}
              user={user}
              onUpdateProfile={handleUpdateProfile}
            />
          </div>

          {/* Resume Upload Section */}
          <div className="lg:col-span-12">
            <ResumeUpload 
              extractedSkills={extractedSkills} 
              onFileUpload={handleResumeUpload}
              uploadingResume={uploadingResume}
              resumeError={resumeError}
              resumeSuccess={resumeSuccess}
            />
            {extractedSkills.length > 0 && !predicting && !predictionResult && (
              <Button 
                onClick={handlePredictCareer}
                className="w-full mt-4 bg-foreground text-background hover:bg-foreground/90 h-12"
              >
                <Cpu className="size-4 mr-2" />
                Predict Career Matches
              </Button>
            )}
            {predicting && (
                <Button disabled className="w-full mt-4 bg-foreground py-6 text-background">
                  <div className="w-5 h-5 border-2 border-background border-t-transparent rounded-full animate-spin mr-2"></div>
                  Running career prediction model...
                </Button>
            )}
          </div>

          {/* Results Sections */}
          {predictionResult && predictionResult.enriched_roles && (
            <div className="lg:col-span-12">
              <div className="flex items-center justify-between mb-4 mt-6">
                 <h2 className="text-xl font-bold text-foreground">Recommended Career Roles</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {predictionResult.enriched_roles.map((roleData, idx) => (
                  <RecommendedCareer
                    key={idx}
                    title={roleData.role}
                    confidence={roleData.display_match_score ?? Math.round(roleData.confidence_score * 100)}
                    description={roleData.description}
                    salaryRange={roleData.salaryRange}
                    growth={roleData.growth}
                    isTopMatch={idx === 0}
                    isActiveLoading={generatingRoadmap && activeRoadmapRole === roleData.role}
                    onViewDetails={() => handleGenerateRoadmap(roleData.role)}
                  />
                ))}
              </div>
            </div>
          )}

          {roadmap && (
            <div className="lg:col-span-6 animate-in fade-in zoom-in duration-500">
              <PersonalRoadmap
                steps={roadmapSteps}
                skillGap={firstSkillGap}
              />
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
