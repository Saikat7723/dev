import React, { useState, useEffect, useRef } from 'react';
import Webcam from 'react-webcam';
import { Camera, CheckCircle2, ShieldCheck, Activity, Users, UserCheck, AlertCircle, RefreshCw } from 'lucide-react';
import apiClient from '../api/axios';

export const LiveAttendance = () => {
  const [cameraStatus, setCameraStatus] = useState({
    status: 'ONLINE',
    camera_id: 'CAM-MAIN-ENTRANCE-01',
    fps: 30.0,
    detected_faces_count: 1,
    last_recognized: null
  });

  const [lastRecognizedStudent, setLastRecognizedStudent] = useState({
    id: 1,
    student_id: 'STU001',
    full_name: 'Rahul Kumar',
    email: 'rahul.kumar@student.edu',
    profile_photo_path: null,
    confidence: 0.91,
    timestamp: new Date().toLocaleTimeString(),
    action: 'CHECK_IN'
  });

  const [recentEvents, setRecentEvents] = useState([]);
  const [isSimulating, setIsSimulating] = useState(false);
  const webcamRef = useRef(null);

  const fetchRecentEvents = async () => {
    try {
      const res = await apiClient.get('/attendance?limit=15');
      setRecentEvents(res.data);
      if (res.data.length > 0 && res.data[0].student) {
        const top = res.data[0];
        setLastRecognizedStudent({
          id: top.student.id,
          student_id: top.student.student_id,
          full_name: top.student.full_name,
          email: top.student.email,
          profile_photo_path: top.student.profile_photo_path,
          confidence: top.confidence || 0.92,
          timestamp: new Date(top.check_in_time).toLocaleTimeString(),
          action: top.check_out_time ? 'CHECK_OUT' : 'CHECK_IN'
        });
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchRecentEvents();
    const interval = setInterval(fetchRecentEvents, 4000);
    return () => clearInterval(interval);
  }, []);

  // Trigger test face recognition check-in simulation
  const handleSimulateCheckin = async () => {
    setIsSimulating(true);
    try {
      // Pick student 1 or 2
      const res = await apiClient.post('/attendance/events', {
        student_id: 1,
        confidence: 0.94,
        camera_id: 'CAM-MAIN-ENTRANCE-01'
      });
      fetchRecentEvents();
    } catch (err) {
      console.error(err);
    } finally {
      setIsSimulating(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/60 border border-slate-800 p-6 rounded-2xl">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Camera className="w-5 h-5 text-cyan-400" />
            Live Entrance Attendance Monitor
          </h1>
          <p className="text-xs text-slate-400 mt-1">Automatic real-time face recognition check-in & check-out monitoring</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleSimulateCheckin}
            disabled={isSimulating}
            className="px-4 py-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-emerald-600/20 transition flex items-center gap-2 disabled:opacity-50"
          >
            <UserCheck className="w-4 h-4" />
            Simulate Entrance Camera Match
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Columns: Live Camera Feed & Bounding Box Overlay */}
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 shadow-xl">
            <div className="flex items-center justify-between mb-3 px-1">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping"></span>
                <span className="text-xs font-bold text-slate-200">Main Library Entrance Stream</span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">
                  {cameraStatus.camera_id}
                </span>
              </div>
              <div className="flex items-center gap-3 text-xs">
                <span className="text-slate-400">FPS: <strong className="text-cyan-400">{cameraStatus.fps}</strong></span>
                <span className="text-slate-400">Faces: <strong className="text-emerald-400">1 Detected</strong></span>
              </div>
            </div>

            {/* Camera Frame Box */}
            <div className="relative w-full aspect-video bg-slate-950 rounded-xl overflow-hidden border border-slate-800 flex items-center justify-center">
              <Webcam
                audio={false}
                ref={webcamRef}
                screenshotFormat="image/jpeg"
                className="w-full h-full object-cover"
              />

              {/* Simulated Face Bounding Box & Target Label */}
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                <div className="w-52 h-64 border-2 border-emerald-400 rounded-2xl flex flex-col justify-between p-2 shadow-[0_0_20px_rgba(52,211,153,0.3)]">
                  <div className="flex items-center justify-between text-[10px] bg-slate-900/90 text-emerald-300 px-2 py-1 rounded font-mono border border-emerald-500/30">
                    <span>94% Confidence</span>
                    <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                  </div>
                  <div className="bg-slate-900/90 text-white text-[11px] p-2 rounded border border-emerald-500/30 font-semibold text-center">
                    Rahul Kumar (STU001)
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Last Recognized Student Card */}
        <div className="space-y-4">
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h2 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Last Recognized Student</h2>
              <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold">
                Match Verified
              </span>
            </div>

            {lastRecognizedStudent ? (
              <div className="space-y-4">
                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 rounded-xl bg-slate-800 border-2 border-cyan-500/50 overflow-hidden flex items-center justify-center text-cyan-400 font-bold text-xl shrink-0 shadow-lg">
                    {lastRecognizedStudent.profile_photo_path ? (
                      <img src={lastRecognizedStudent.profile_photo_path} alt="" className="w-full h-full object-cover" />
                    ) : (
                      lastRecognizedStudent.full_name?.charAt(0)
                    )}
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-slate-100">{lastRecognizedStudent.full_name}</h3>
                    <p className="text-xs font-mono text-cyan-400">{lastRecognizedStudent.student_id}</p>
                    <p className="text-[11px] text-slate-400 mt-0.5">{lastRecognizedStudent.email}</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3 pt-2">
                  <div className="bg-slate-950/60 border border-slate-800 p-3 rounded-xl">
                    <span className="text-[10px] text-slate-400 block">Time</span>
                    <span className="text-xs font-semibold text-slate-200">{lastRecognizedStudent.timestamp}</span>
                  </div>
                  <div className="bg-slate-950/60 border border-slate-800 p-3 rounded-xl">
                    <span className="text-[10px] text-slate-400 block">Confidence</span>
                    <span className="text-xs font-mono font-bold text-emerald-400">
                      {Math.round(lastRecognizedStudent.confidence * 100)}%
                    </span>
                  </div>
                </div>

                <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-xl flex items-center justify-between text-xs text-emerald-300">
                  <span className="font-semibold">Event Status:</span>
                  <span className="px-2.5 py-1 rounded bg-emerald-500/20 text-emerald-400 font-bold">
                    {lastRecognizedStudent.action === 'CHECK_IN' ? 'CHECKED IN' : 'CHECKED OUT'}
                  </span>
                </div>
              </div>
            ) : (
              <p className="text-xs text-slate-400 text-center py-6">No recognition match yet.</p>
            )}
          </div>
        </div>
      </div>

      {/* Recent Live Recognition Events Feed */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-4 shadow-xl">
        <h2 className="text-sm font-bold text-slate-200">Real-Time Attendance Event Feed</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950/60 text-slate-400 uppercase font-semibold text-[10px] tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-4 py-3">Student Name</th>
                <th className="px-4 py-3">Student ID</th>
                <th className="px-4 py-3">Time</th>
                <th className="px-4 py-3">Confidence</th>
                <th className="px-4 py-3">Camera</th>
                <th className="px-4 py-3">Event Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {recentEvents.map(event => (
                <tr key={event.id} className="hover:bg-slate-800/40">
                  <td className="px-4 py-3 font-semibold text-slate-200">{event.student?.full_name}</td>
                  <td className="px-4 py-3 font-mono text-cyan-400">{event.student?.student_id}</td>
                  <td className="px-4 py-3">{new Date(event.check_in_time).toLocaleTimeString()}</td>
                  <td className="px-4 py-3 font-mono">{event.confidence ? `${Math.round(event.confidence * 100)}%` : 'Manual'}</td>
                  <td className="px-4 py-3 text-slate-400">{event.camera_id || 'Entrance Cam 01'}</td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      {event.check_out_time ? 'CHECK_OUT' : 'CHECK_IN'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
