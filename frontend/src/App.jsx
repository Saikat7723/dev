import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { MainLayout } from './components/layout/MainLayout';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { StudentList } from './pages/StudentList';
import { StudentAdd } from './pages/StudentAdd';
import { StudentDetails } from './pages/StudentDetails';
import { LiveAttendance } from './pages/LiveAttendance';
import { AttendanceList } from './pages/AttendanceList';
import { AttendanceReports } from './pages/AttendanceReports';
import { BookList } from './pages/BookList';
import { IssueReturn } from './pages/IssueReturn';
import { OverdueBooks } from './pages/OverdueBooks';
import { AdminSettings } from './pages/AdminSettings';

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          
          <Route path="/" element={<MainLayout />}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            
            <Route path="students" element={<StudentList />} />
            <Route path="students/new" element={<StudentAdd />} />
            <Route path="students/:id" element={<StudentDetails />} />
            <Route path="students/:id/edit" element={<StudentAdd />} />

            <Route path="attendance/live" element={<LiveAttendance />} />
            <Route path="attendance/list" element={<AttendanceList />} />
            <Route path="attendance/reports" element={<AttendanceReports />} />

            <Route path="books" element={<BookList />} />
            <Route path="books/issue-return" element={<IssueReturn />} />
            <Route path="books/overdue" element={<OverdueBooks />} />

            <Route path="admin/settings" element={<AdminSettings />} />
          </Route>

          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
