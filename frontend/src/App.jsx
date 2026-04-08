import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import { GameProvider } from './context/GameContext';
import Navbar from './components/Navbar';
import MobileNav from './components/MobileNav';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import LessonPage from './pages/LessonPage';
import MyLessonsPage from './pages/MyLessonsPage';
import ResultsPage from './pages/ResultsPage';
import AdminDashboard from './pages/admin/AdminDashboard';
import AdminStudents from './pages/admin/AdminStudents';
import AdminStudentDetail from './pages/admin/AdminStudentDetail';
import AdminLessons from './pages/admin/AdminLessons';
import LeaderboardPage from './pages/LeaderboardPage';
import { Loader2 } from 'lucide-react';

function PrivateRoute({ children, adminOnly = false }) {
  const { user, loading } = useAuth();
  if (loading) return (
    <div className="flex items-center justify-center min-h-screen">
      <Loader2 className="animate-spin text-blue-600" size={40} />
    </div>
  );
  if (!user) return <Navigate to="/login" replace />;
  if (adminOnly && user.role !== 'admin') return <Navigate to="/dashboard" replace />;
  return children;
}

function PublicRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return (
    <div className="flex items-center justify-center min-h-screen">
      <Loader2 className="animate-spin text-blue-600" size={40} />
    </div>
  );
  if (user) return <Navigate to={user.role === 'admin' ? '/admin' : '/dashboard'} replace />;
  return children;
}

function Layout({ children }) {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="pb-16 sm:pb-0">{children}</main>
      <MobileNav />
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <ThemeProvider>
      <AuthProvider>
      <GameProvider>
        <Routes>
          <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />

          {/* Student routes */}
          <Route path="/dashboard" element={
            <PrivateRoute><Layout><DashboardPage /></Layout></PrivateRoute>
          } />
          <Route path="/lessons/:id" element={
            <PrivateRoute><Layout><LessonPage /></Layout></PrivateRoute>
          } />
          <Route path="/my-lessons" element={
            <PrivateRoute><Layout><MyLessonsPage /></Layout></PrivateRoute>
          } />
          <Route path="/results" element={
            <PrivateRoute><Layout><ResultsPage /></Layout></PrivateRoute>
          } />
          <Route path="/leaderboard" element={
            <PrivateRoute><Layout><LeaderboardPage /></Layout></PrivateRoute>
          } />

          {/* Admin routes */}
          <Route path="/admin" element={
            <PrivateRoute adminOnly><Layout><AdminDashboard /></Layout></PrivateRoute>
          } />
          <Route path="/admin/students" element={
            <PrivateRoute adminOnly><Layout><AdminStudents /></Layout></PrivateRoute>
          } />
          <Route path="/admin/students/:id" element={
            <PrivateRoute adminOnly><Layout><AdminStudentDetail /></Layout></PrivateRoute>
          } />
          <Route path="/admin/lessons" element={
            <PrivateRoute adminOnly><Layout><AdminLessons /></Layout></PrivateRoute>
          } />

          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </GameProvider>
      </AuthProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
}
