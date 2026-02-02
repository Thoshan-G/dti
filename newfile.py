import React, { useState, useEffect, useRef } from "react";
import { initializeApp } from "firebase/app";
import {
  getAuth,
  signInAnonymously,
  onAuthStateChanged
} from "firebase/auth";
import {
  getFirestore,
  collection,
  addDoc,
  onSnapshot,
  updateDoc,
  doc,
  serverTimestamp
} from "firebase/firestore";
import {
  MapPin,
  Camera,
  ChevronLeft,
  Menu,
  Eye,
  AlertCircle,
  CheckCircle2,
  ShieldCheck,
  Activity,
  Navigation
} from "lucide-react";

/* ---------------- FIREBASE CONFIG ---------------- */
/* 🔴 Replace with your real config */
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_PROJECT.firebaseapp.com",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_PROJECT.appspot.com",
  messagingSenderId: "XXXX",
  appId: "XXXX"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

/* ---------------- APP ---------------- */
export default function App() {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState("home");
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [role, setRole] = useState("citizen");

  const [formData, setFormData] = useState({
    description: "",
    location: "",
    category: "Infrastructure"
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const timeoutRef = useRef(null);

  /* ---------------- AUTH ---------------- */
  useEffect(() => {
    signInAnonymously(auth).catch(console.error);

    const unsub = onAuthStateChanged(auth, (u) => {
      setUser(u);
      setLoading(false);
    });

    return () => unsub();
  }, []);

  /* ---------------- REALTIME FIRESTORE ---------------- */
  useEffect(() => {
    if (!user) return;

    const reportsRef = collection(db, "reports");

    const unsub = onSnapshot(reportsRef, (snap) => {
      const data = snap.docs.map((d) => ({
        id: d.id,
        ...d.data()
      }));

      data.sort(
        (a, b) =>
          (b.createdAt?.toMillis?.() || 0) -
          (a.createdAt?.toMillis?.() || 0)
      );

      setReports(data);
    });

    return () => unsub();
  }, [user]);

  /* ---------------- SUBMIT REPORT ---------------- */
  const handleReportSubmit = async (e) => {
    e.preventDefault();
    if (!formData.description || !formData.location) return;

    setIsSubmitting(true);

    try {
      await addDoc(collection(db, "reports"), {
        ...formData,
        status: "Pending",
        createdAt: serverTimestamp()
      });

      setShowSuccess(true);
      setFormData({
        description: "",
        location: "",
        category: "Infrastructure"
      });

      timeoutRef.current = setTimeout(() => {
        setShowSuccess(false);
        setActiveTab("view");
        setIsSubmitting(false);
      }, 2000);
    } catch (err) {
      console.error(err);
      setIsSubmitting(false);
    }
  };

  useEffect(() => {
    return () => timeoutRef.current && clearTimeout(timeoutRef.current);
  }, []);

  /* ---------------- RESOLVE ISSUE ---------------- */
  const solveIssue = async (id) => {
    try {
      await updateDoc(doc(db, "reports", id), {
        status: "Resolved",
        resolvedAt: serverTimestamp()
      });
    } catch (err) {
      console.error(err);
    }
  };

  /* ---------------- LOADING ---------------- */
  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="animate-spin w-10 h-10 border-4 border-emerald-300 border-t-emerald-600 rounded-full" />
      </div>
    );
  }

  /* ---------------- UI ---------------- */
  return (
    <div className="min-h-screen max-w-md mx-auto bg-slate-50 flex flex-col">

      {/* HEADER */}
      <header className="bg-emerald-600 p-5 text-white flex justify-between">
        <div className="flex items-center gap-2">
          <Navigation className="rotate-45" />
          <h1 className="font-black">CivicEye</h1>
        </div>

        <select
          value={role}
          onChange={(e) => setRole(e.target.value)}
          className="bg-emerald-700 text-xs rounded-full px-3"
        >
          <option value="citizen">CITIZEN</option>
          <option value="official">OFFICIAL</option>
        </select>
      </header>

      {/* CONTENT */}
      <main className="flex-1 overflow-y-auto p-4">

        {/* HOME */}
        {activeTab === "home" && (
          <div className="space-y-6 text-center">
            <MapPin size={60} className="mx-auto text-red-500" />
            <h2 className="text-2xl font-black">
              {role === "citizen" ? "Report Problems" : "Manage Issues"}
            </h2>

            <button
              onClick={() => setActiveTab("report")}
              className="w-full bg-emerald-600 text-white py-4 rounded-xl"
            >
              Report Issue
            </button>

            <button
              onClick={() => setActiveTab("view")}
              className="w-full bg-white border py-4 rounded-xl"
            >
              View Reports
            </button>
          </div>
        )}

        {/* REPORT */}
        {activeTab === "report" && (
          <form onSubmit={handleReportSubmit} className="space-y-4">
            <button onClick={() => setActiveTab("home")}>
              <ChevronLeft />
            </button>

            {showSuccess ? (
              <div className="text-center text-emerald-600 font-bold">
                <CheckCircle2 size={48} className="mx-auto" />
                Report Submitted
              </div>
            ) : (
              <>
                <textarea
                  required
                  placeholder="Describe problem"
                  value={formData.description}
                  onChange={(e) =>
                    setFormData({ ...formData, description: e.target.value })
                  }
                  className="w-full p-4 border rounded-xl"
                />

                <input
                  required
                  placeholder="Location"
                  value={formData.location}
                  onChange={(e) =>
                    setFormData({ ...formData, location: e.target.value })
                  }
                  className="w-full p-4 border rounded-xl"
                />

                <button
                  disabled={isSubmitting}
                  className="w-full bg-emerald-600 text-white py-4 rounded-xl"
                >
                  {isSubmitting ? "Submitting..." : "Submit"}
                </button>
              </>
            )}
          </form>
        )}

        {/* FEED */}
        {activeTab === "view" && (
          <div className="space-y-4">
            {reports.map((r) => (
              <div
                key={r.id}
                className="bg-white p-4 rounded-xl border"
              >
                <div className="flex justify-between">
                  <span className="text-xs font-bold">{r.status}</span>
                  <span className="text-xs">{r.category}</span>
                </div>

                <p className="font-bold mt-2">{r.description}</p>
                <p className="text-sm text-slate-500">{r.location}</p>

                {role === "official" && r.status === "Pending" && (
                  <button
                    onClick={() => solveIssue(r.id)}
                    className="mt-3 w-full bg-slate-900 text-white py-2 rounded-lg"
                  >
                    Mark Resolved
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </main>

      {/* NAV */}
      <nav className="flex justify-around border-t p-3 bg-white">
        <button onClick={() => setActiveTab("home")}>
          <Menu />
        </button>
        <button onClick={() => setActiveTab("report")}>
          <AlertCircle />
        </button>
        <button onClick={() => setActiveTab("view")}>
          <Eye />
        </button>
      </nav>
    </div>
  );
}
