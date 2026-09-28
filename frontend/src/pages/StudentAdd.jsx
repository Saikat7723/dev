import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { UserPlus, ArrowLeft, AlertTriangle, CheckCircle2 } from 'lucide-react';
import apiClient from '../api/axios';
import { WebcamCapture } from '../components/common/WebcamCapture';

export const StudentAdd = () => {
  const navigate = useNavigate();
  const [departments, setDepartments] = useState([]);
  const [courses, setCourses] = useState([]);
  
  const [formData, setFormData] = useState({
    student_id: '',
    full_name: '',
    email: '',
    phone: '',
    department_id: '',
    course_id: '',
    dob: '',
    gender: 'Male',
    date_of_joining: new Date().toISOString().split('T')[0],
    address: '',
    status: 'Active'
  });

  const [confirmedPhotoBlob, setConfirmedPhotoBlob] = useState(null);
  const [confirmedPhotoPreview, setConfirmedPhotoPreview] = useState(null);
  
  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  useEffect(() => {
    const loadAcademic = async () => {
      try {
        const [dRes, cRes] = await Promise.all([
          apiClient.get('/admin/departments'),
          apiClient.get('/admin/courses')
        ]);
        setDepartments(dRes.data);
        setCourses(cRes.data);
        if (dRes.data.length > 0) {
          setFormData(prev => ({ ...prev, department_id: dRes.data[0].id }));
        }
        if (cRes.data.length > 0) {
          setFormData(prev => ({ ...prev, course_id: cRes.data[0].id }));
        }
      } catch (e) {
        console.error(e);
      }
    };
    loadAcademic();
  }, []);

  const handlePhotoConfirmed = (blob, previewUrl) => {
    setConfirmedPhotoBlob(blob);
    setConfirmedPhotoPreview(previewUrl);
    setErrorMsg(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg(null);

    if (!confirmedPhotoBlob) {
      setErrorMsg("Please capture and confirm the student's live photo for face recognition enrollment.");
      return;
    }

    setSubmitting(true);

    try {
      // 1. Create Student record
      const studentRes = await apiClient.post('/students', {
        ...formData,
        department_id: formData.department_id ? parseInt(formData.department_id) : null,
        course_id: formData.course_id ? parseInt(formData.course_id) : null
      });

      const newStudent = studentRes.data;

      // 2. Upload photo & generate face embedding
      const photoFormData = new FormData();
      photoFormData.append('file', confirmedPhotoBlob, `${newStudent.student_id}.jpg`);

      await apiClient.post(`/students/${newStudent.id}/photo`, photoFormData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      navigate(`/students/${newStudent.id}`);
    } catch (err) {
      const msg = err.response?.data?.detail || 'Failed to register student. Please check input values.';
      setErrorMsg(msg);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-slate-200 transition"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Directory
        </button>
        <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
          <UserPlus className="w-5 h-5 text-cyan-400" />
          Register Student & Enrol Face Profile
        </h1>
      </div>

      {errorMsg && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-300 text-xs flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0" />
          <div>
            <p className="font-semibold">Registration / Face Enrollment Warning</p>
            <p className="mt-0.5">{errorMsg}</p>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column: Student Information Form */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-4 shadow-xl">
          <h2 className="text-sm font-bold text-slate-200 pb-2 border-b border-slate-800">
            Personal & Academic Information
          </h2>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Student ID / Roll No *</label>
              <input
                type="text"
                required
                value={formData.student_id}
                onChange={e => setFormData({ ...formData, student_id: e.target.value })}
                placeholder="STU005"
                className="w-full px-3 py-2 bg-slate-950/60 border border-slate-800 rounded-xl text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Full Name *</label>
              <input
                type="text"
                required
                value={formData.full_name}
                onChange={e => setFormData({ ...formData, full_name: e.target.value })}
                placeholder="John Doe"
                className="w-full px-3 py-2 bg-slate-950/60 border border-slate-800 rounded-xl text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Email Address *</label>
              <input
                type="email"
                required
                value={formData.email}
                onChange={e => setFormData({ ...formData, email: e.target.value })}
                placeholder="john.doe@student.edu"
                className="w-full px-3 py-2 bg-slate-950/60 border border-slate-800 rounded-xl text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Phone Number</label>
              <input
                type="text"
                value={formData.phone}
                onChange={e => setFormData({ ...formData, phone: e.target.value })}
                placeholder="9876543210"
                className="w-full px-3 py-2 bg-slate-950/60 border border-slate-800 rounded-xl text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Department</label>
              <select
                value={formData.department_id}
                onChange={e => setFormData({ ...formData, department_id: e.target.value })}
                className="w-full px-3 py-2 bg-slate-950/60 border border-slate-800 rounded-xl text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
              >
                {departments.map(d => (
                  <option key={d.id} value={d.id}>{d.name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Course</label>
              <select
                value={formData.course_id}
                onChange={e => setFormData({ ...formData, course_id: e.target.value })}
                className="w-full px-3 py-2 bg-slate-950/60 border border-slate-800 rounded-xl text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
              >
                {courses.map(c => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Date of Birth</label>
              <input
                type="date"
                value={formData.dob}
                onChange={e => setFormData({ ...formData, dob: e.target.value })}
                className="w-full px-3 py-2 bg-slate-950/60 border border-slate-800 rounded-xl text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Gender</label>
              <select
                value={formData.gender}
                onChange={e => setFormData({ ...formData, gender: e.target.value })}
                className="w-full px-3 py-2 bg-slate-950/60 border border-slate-800 rounded-xl text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
              >
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Residential Address</label>
            <textarea
              rows={2}
              value={formData.address}
              onChange={e => setFormData({ ...formData, address: e.target.value })}
              placeholder="Hostel address or permanent residential location"
              className="w-full px-3 py-2 bg-slate-950/60 border border-slate-800 rounded-xl text-xs text-slate-100 focus:outline-none focus:border-cyan-500 resize-none"
            />
          </div>

          <button
            type="submit"
            disabled={submitting || !confirmedPhotoBlob}
            className="w-full py-3 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-cyan-600/20 transition flex items-center justify-center gap-2 disabled:opacity-50 mt-4"
          >
            {submitting ? (
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <>
                <CheckCircle2 className="w-4 h-4" />
                Complete Student Registration & Face Enrolment
              </>
            )}
          </button>
        </div>

        {/* Right Column: Webcam Photo Capture */}
        <div className="space-y-4">
          <WebcamCapture
            onCaptureConfirmed={handlePhotoConfirmed}
            isSubmitting={submitting}
          />

          {confirmedPhotoPreview && (
            <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-xl flex items-center gap-3">
              <div className="w-12 h-12 rounded-lg overflow-hidden border border-emerald-500/40 shrink-0">
                <img src={confirmedPhotoPreview} alt="" className="w-full h-full object-cover" />
              </div>
              <div className="text-xs text-emerald-300">
                <p className="font-semibold flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Face Photo Confirmed
                </p>
                <p className="text-[11px] text-emerald-400/80">Ready to compute face embedding vector on submit.</p>
              </div>
            </div>
          )}
        </div>
      </form>
    </div>
  );
};
