import React, { useRef, useState, useCallback } from 'react';
import Webcam from 'react-webcam';
import { Camera, RefreshCw, CheckCircle2, AlertTriangle, Eye } from 'lucide-react';

const videoConstraints = {
  width: 640,
  height: 480,
  facingMode: "user"
};

export const WebcamCapture = ({ onCaptureConfirmed, isSubmitting }) => {
  const webcamRef = useRef(null);
  const [capturedImage, setCapturedImage] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);

  const capture = useCallback(() => {
    const imageSrc = webcamRef.current?.getScreenshot();
    if (imageSrc) {
      setCapturedImage(imageSrc);
      setErrorMsg(null);
    }
  }, [webcamRef]);

  const retake = () => {
    setCapturedImage(null);
    setErrorMsg(null);
  };

  const confirmImage = () => {
    if (capturedImage && onCaptureConfirmed) {
      // Convert base64 to Blob
      fetch(capturedImage)
        .then(res => res.blob())
        .then(blob => {
          onCaptureConfirmed(blob, capturedImage);
        })
        .catch(err => {
          setErrorMsg("Could not process image snapshot: " + err.message);
        });
    }
  };

  return (
    <div className="flex flex-col items-center bg-slate-900/90 border border-slate-800 rounded-xl p-4 shadow-xl">
      <div className="w-full flex items-center justify-between mb-3 px-1">
        <span className="text-sm font-semibold text-slate-300 flex items-center gap-2">
          <Camera className="w-4 h-4 text-cyan-400" />
          Live Student Photo Capture
        </span>
        <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          Camera Active
        </span>
      </div>

      <div className="relative w-full aspect-video bg-slate-950 rounded-lg overflow-hidden border border-slate-800 flex items-center justify-center">
        {!capturedImage ? (
          <>
            <Webcam
              audio={false}
              ref={webcamRef}
              screenshotFormat="image/jpeg"
              videoConstraints={videoConstraints}
              className="w-full h-full object-cover"
            />
            {/* Overlay framing guide box */}
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <div className="w-48 h-60 border-2 border-dashed border-cyan-400/70 rounded-full flex items-center justify-center">
                <span className="text-xs text-cyan-300 bg-slate-900/80 px-2 py-1 rounded">Position Face Here</span>
              </div>
            </div>
          </>
        ) : (
          <img src={capturedImage} alt="Captured Student Snapshot" className="w-full h-full object-cover" />
        )}
      </div>

      {errorMsg && (
        <div className="w-full mt-3 p-2.5 rounded bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      <div className="flex items-center gap-3 mt-4 w-full">
        {!capturedImage ? (
          <button
            type="button"
            onClick={capture}
            className="flex-1 py-2.5 px-4 bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-sm rounded-lg flex items-center justify-center gap-2 transition-all shadow-lg shadow-cyan-600/20"
          >
            <Camera className="w-4 h-4" />
            Capture Photo
          </button>
        ) : (
          <>
            <button
              type="button"
              onClick={retake}
              disabled={isSubmitting}
              className="flex-1 py-2 px-3 bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium text-sm rounded-lg flex items-center justify-center gap-1.5 transition border border-slate-700 disabled:opacity-50"
            >
              <RefreshCw className="w-4 h-4" />
              Retake Photo
            </button>
            <button
              type="button"
              onClick={confirmImage}
              disabled={isSubmitting}
              className="flex-1 py-2 px-3 bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-sm rounded-lg flex items-center justify-center gap-1.5 transition shadow-lg shadow-emerald-600/20 disabled:opacity-50"
            >
              <CheckCircle2 className="w-4 h-4" />
              {isSubmitting ? "Verifying Face..." : "Confirm & Save Photo"}
            </button>
          </>
        )}
      </div>
    </div>
  );
};
