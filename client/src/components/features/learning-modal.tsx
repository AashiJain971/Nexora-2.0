import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { 
  Play, 
  Pause, 
  SkipBack, 
  SkipForward,
  Star,
  Bookmark,
  Share2,
  Trophy,
  Medal,
  GraduationCap,
  CheckCircle,
  Lock,
  PlayCircle,
  Clock,
  TrendingUp,
  Users
} from 'lucide-react';
import { useDummyData } from '@/hooks/use-dummy-data';

interface LearningModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function LearningModal({ open, onOpenChange }: LearningModalProps) {
  const [selectedModuleId, setSelectedModuleId] = useState(3);
  const [currentProgress, setCurrentProgress] = useState(60);
  
  const { learningCourses, learningProgress } = useDummyData();
  
  const courseModules = [
    {
      id: 1,
      title: "Introduction to Digital Marketing",
      status: "completed",
      duration: "8:30",
      videoId: "dQw4w9WgXcQ", // Working dummy video
      description: "Learn the basics of digital marketing for small businesses"
    },
    {
      id: 2,
      title: "Social Media Marketing",
      status: "completed", 
      duration: "12:15",
      videoId: "Ks-_Mh1QhMc", // Working business marketing video
      description: "Master social media strategies to grow your audience"
    },
    {
      id: 3,
      title: "Search Engine Optimization (SEO)",
      status: "in-progress",
      duration: "15:45",
      videoId: "JkBV3kPH5jo", // Working SEO basics video
      description: "Improve your website's visibility on search engines"
    },
    {
      id: 4,
      title: "Email Marketing Strategies",
      status: "locked",
      duration: "10:20",
      videoId: "YQiRG5BdPSo", // Working email marketing video
      description: "Build effective email campaigns for your business"
    },
    {
      id: 5,
      title: "Analytics and Measurement",
      status: "locked",
      duration: "18:30",
      videoId: "N6BghzuFLIg", // Working analytics video
      description: "Track and measure your marketing performance"
    }
  ];

  const selectedModule = courseModules.find(m => m.id === selectedModuleId) || courseModules[2];

  const selectModule = (moduleId: number) => {
    const module = courseModules.find(m => m.id === moduleId);
    if (module && module.status !== 'locked') {
      setSelectedModuleId(moduleId);
    }
  };

  const previousLesson = () => {
    const currentIndex = courseModules.findIndex(m => m.id === selectedModuleId);
    if (currentIndex > 0) {
      const prevModule = courseModules[currentIndex - 1];
      if (prevModule.status !== 'locked') {
        setSelectedModuleId(prevModule.id);
      }
    }
  };

  const nextLesson = () => {
    const currentIndex = courseModules.findIndex(m => m.id === selectedModuleId);
    if (currentIndex < courseModules.length - 1) {
      const nextModule = courseModules[currentIndex + 1];
      if (nextModule.status !== 'locked') {
        setSelectedModuleId(nextModule.id);
      }
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const achievements = [
    { name: "First Course Started", icon: Medal, earned: true },
    { name: "Module Master", icon: Trophy, earned: true },
    { name: "Course Completion", icon: Star, earned: false },
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-accent" />;
      case 'in-progress':
        return <PlayCircle className="w-5 h-5 text-orange-accent" />;
      case 'locked':
        return <Lock className="w-5 h-5 text-muted-foreground" />;
      default:
        return <Clock className="w-5 h-5 text-muted-foreground" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'border-green-accent';
      case 'in-progress':
        return 'border-orange-accent';
      case 'locked':
        return 'border-border';
      default:
        return 'border-border';
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold">MSME Learning Platform</DialogTitle>
        </DialogHeader>
        
        <div className="space-y-6">
          {/* Video Player */}
          <Card className="overflow-hidden">
            <div className="relative">
              <div className="w-full aspect-video bg-gradient-to-br from-slate-900 to-slate-700 flex items-center justify-center relative overflow-hidden rounded-t-lg">
                <img 
                  src="https://images.unsplash.com/photo-1553877522-43269d4ea984?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&h=675"
                  alt="Business Learning"
                  className="w-full h-full object-cover opacity-60"
                />
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="bg-black/70 backdrop-blur-sm rounded-full p-6">
                    <PlayCircle className="w-16 h-16 text-white" />
                  </div>
                </div>
                <div className="absolute bottom-4 left-4 right-4">
                  <div className="bg-black/80 backdrop-blur-sm rounded-lg p-3">
                    <div className="text-white font-semibold">{selectedModule.title}</div>
                    <div className="text-white/70 text-sm">{selectedModule.duration} • Business Learning</div>
                  </div>
                </div>
              </div>

            </div>
            
            <div className="p-6">
              {/* Video Controls */}
              <div className="flex items-center space-x-4 mb-4">
                <div className="flex items-center space-x-2">
                  <Button size="sm" variant="outline" onClick={previousLesson} disabled={selectedModuleId === 1}>
                    <SkipBack className="w-4 h-4" />
                  </Button>
                  <Button size="sm" variant="outline" onClick={nextLesson} disabled={selectedModuleId === courseModules.length}>
                    <SkipForward className="w-4 h-4" />
                  </Button>
                </div>
                
                <div className="flex-1">
                  <div className="flex justify-between text-sm mb-1">
                    <span>Module {selectedModuleId} of {courseModules.length}</span>
                    <span>Duration: {selectedModule.duration}</span>
                  </div>
                  <Progress value={(selectedModuleId / courseModules.length) * 100} className="w-full" />
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                  <Badge variant="outline" className={selectedModule.status === 'completed' ? 'border-green-accent text-green-accent' : selectedModule.status === 'in-progress' ? 'border-orange-accent text-orange-accent' : 'border-muted-foreground'}>
                    {selectedModule.status}
                  </Badge>
                  <div className="flex items-center space-x-1">
                    <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                    <span>4.8/5 (234 reviews)</span>
                  </div>
                </div>
                <div className="flex space-x-2">
                  <Button size="sm" variant="outline">
                    <Bookmark className="w-4 h-4 mr-1" />
                    Save
                  </Button>
                  <Button size="sm" variant="outline">
                    <Share2 className="w-4 h-4 mr-1" />
                    Share
                  </Button>
                </div>
              </div>
            </div>
          </Card>

          {/* Course Content */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <h4 className="text-lg font-semibold mb-4">Course Modules</h4>
              <div className="space-y-3">
                {courseModules.map((module) => (
                  <Card 
                    key={module.id}
                    onClick={() => selectModule(module.id)}
                    className={`p-4 border-l-4 ${getStatusColor(module.status)} ${
                      selectedModuleId === module.id ? 'ring-2 ring-teal-accent bg-teal-accent/5' : ''
                    } ${
                      module.status !== 'locked' ? 'cursor-pointer hover:bg-muted/50 hover:scale-[1.01]' : 'opacity-60 cursor-not-allowed'
                    } transition-all duration-200`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        {getStatusIcon(module.status)}
                        <div>
                          <div className="font-medium">{module.title}</div>
                          <div className="text-sm text-muted-foreground">{module.description}</div>
                          <div className="flex items-center space-x-2 mt-1">
                            <Clock className="w-3 h-3 text-muted-foreground" />
                            <span className="text-xs text-muted-foreground">{module.duration}</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex flex-col items-end space-y-1">
                        <Badge className={
                          module.status === 'completed' ? 'bg-green-accent/20 text-green-accent' :
                          module.status === 'in-progress' ? 'bg-orange-accent/20 text-orange-accent' :
                          'bg-muted text-muted-foreground'
                        }>
                          {module.status === 'completed' ? 'Completed' :
                           module.status === 'in-progress' ? 'In Progress' :
                           'Locked'}
                        </Badge>
                        {selectedModuleId === module.id && (
                          <Badge variant="outline" className="text-xs border-teal-accent text-teal-accent">
                            Playing
                          </Badge>
                        )}
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
            
            <div className="space-y-6">
              {/* Progress Overview */}
              <Card className="p-6">
                <h4 className="text-lg font-semibold mb-4">Your Progress</h4>
                <div className="text-center mb-4">
                  <div className="text-3xl font-bold text-teal-accent">{currentProgress}%</div>
                  <div className="text-muted-foreground">Course Completion</div>
                </div>
                <Progress value={currentProgress} className="w-full mb-4" />
                <div className="text-sm text-muted-foreground text-center">
                  3 of 5 modules completed
                </div>
              </Card>
              
              {/* Achievements */}
              <Card className="p-6">
                <h5 className="font-semibold mb-3">Achievements</h5>
                <div className="space-y-2">
                  {achievements.map((achievement, index) => {
                    const IconComponent = achievement.icon;
                    return (
                      <div key={index} className="flex items-center space-x-2">
                        <IconComponent className={`w-4 h-4 ${
                          achievement.earned ? 'text-orange-accent' : 'text-muted-foreground'
                        }`} />
                        <span className={`text-sm ${
                          achievement.earned ? 'text-foreground' : 'text-muted-foreground'
                        }`}>
                          {achievement.name}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </Card>

              {/* Learning Progress */}
              <Card className="p-6">
                <h5 className="font-semibold mb-3">All Courses Progress</h5>
                <div className="space-y-3">
                  {learningProgress.map((item) => (
                    <div key={item.course}>
                      <div className="flex justify-between text-sm mb-1">
                        <span>{item.course}</span>
                        <span>{item.progress}%</span>
                      </div>
                      <Progress value={item.progress} className="w-full" />
                    </div>
                  ))}
                </div>
              </Card>

              {/* Related Courses */}
              <Card className="p-6">
                <h5 className="font-semibold mb-3">Related Courses</h5>
                <div className="space-y-3">
                  <div className="flex space-x-3 p-2 hover:bg-muted/50 rounded-lg transition-colors cursor-pointer">
                    <div className="w-12 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded flex items-center justify-center">
                      <GraduationCap className="w-4 h-4 text-white" />
                    </div>
                    <div className="flex-1">
                      <div className="font-medium text-sm">Financial Management</div>
                      <div className="text-xs text-muted-foreground">
                        25:30 • Intermediate
                      </div>
                    </div>
                  </div>
                  <div className="flex space-x-3 p-2 hover:bg-muted/50 rounded-lg transition-colors cursor-pointer">
                    <div className="w-12 h-8 bg-gradient-to-r from-green-500 to-teal-600 rounded flex items-center justify-center">
                      <TrendingUp className="w-4 h-4 text-white" />
                    </div>
                    <div className="flex-1">
                      <div className="font-medium text-sm">Business Growth Strategies</div>
                      <div className="text-xs text-muted-foreground">
                        18:45 • Advanced
                      </div>
                    </div>
                  </div>
                  <div className="flex space-x-3 p-2 hover:bg-muted/50 rounded-lg transition-colors cursor-pointer">
                    <div className="w-12 h-8 bg-gradient-to-r from-orange-500 to-red-600 rounded flex items-center justify-center">
                      <Users className="w-4 h-4 text-white" />
                    </div>
                    <div className="flex-1">
                      <div className="font-medium text-sm">Customer Relationship Management</div>
                      <div className="text-xs text-muted-foreground">
                        22:15 • Beginner
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
