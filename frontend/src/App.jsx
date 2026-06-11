import { useEffect, useState } from "react";
import API from "./api";
import "./App.css";

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(localStorage.getItem("loggedIn") === "true");
  const [activePage, setActivePage] = useState("dashboard");

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const [jobs, setJobs] = useState([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [editingJobId, setEditingJobId] = useState(null);

  const [selectedJob, setSelectedJob] = useState("");
  const [files, setFiles] = useState([]);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadedResumes, setUploadedResumes] = useState([]);

  const [rankings, setRankings] = useState([]);

  const login = async () => {
    try {
      const res = await API.post("/login/", {
        username,
        password,
      });

      if (res.data.success) {
        localStorage.setItem("loggedIn", "true");
        localStorage.setItem("username", res.data.username);
        setIsLoggedIn(true);
      }
    } catch (error) {
      alert("Invalid username or password");
    }
  };

  const logout = () => {
    localStorage.removeItem("loggedIn");
    localStorage.removeItem("username");
    setIsLoggedIn(false);
  };

  const loadJobs = async () => {
    const res = await API.get("/dashboard/");
    setJobs(res.data);
  };

  const loadResumesByJob = async (jobId) => {
    if (!jobId) return;
    const res = await API.get(`/jobs/${jobId}/resumes/`);
    setUploadedResumes(res.data);
  };

  useEffect(() => {
    if (isLoggedIn) {
      loadJobs();
    }
  }, [isLoggedIn]);

  const saveJob = async () => {
    if (!title || !description) {
      alert("Please enter job title and description");
      return;
    }

    if (editingJobId) {
      await API.put(`/jobs/${editingJobId}/`, { title, description });
      alert("Job updated successfully");
    } else {
      await API.post("/jobs/", { title, description });
      alert("Job created successfully");
    }

    setTitle("");
    setDescription("");
    setEditingJobId(null);
    loadJobs();
  };

  const editJob = async (job) => {
    const res = await API.get(`/jobs/${job.id}/`);
    setTitle(res.data.title);
    setDescription(res.data.description);
    setEditingJobId(job.id);
    setActivePage("crud");
  };

  const deleteJob = async (jobId) => {
    if (window.confirm("Are you sure you want to delete this job role?")) {
      await API.delete(`/jobs/${jobId}/`);
      alert("Job deleted successfully");
      loadJobs();
    }
  };

  const handleJobSelection = async (jobId) => {
    setSelectedJob(jobId);
    setRankings([]);
    await loadResumesByJob(jobId);
  };

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    const allowed = ["pdf", "docx", "jpg", "jpeg", "png"];

    const invalidFiles = selectedFiles.filter((file) => {
      const ext = file.name.split(".").pop().toLowerCase();
      return !allowed.includes(ext);
    });

    if (invalidFiles.length > 0) {
      alert("Unsupported file detected. Only PDF, DOCX, JPG, JPEG and PNG are allowed.");
      e.target.value = "";
      setFiles([]);
      return;
    }

    setFiles(selectedFiles);
  };

  const uploadResumes = async () => {
    if (!selectedJob) {
      alert("Please select a job role first");
      return;
    }

    if (!files || files.length === 0) {
      alert("Please choose one or more resume files");
      return;
    }

    try {
      setUploadProgress(0);

      const formData = new FormData();
      formData.append("job_role", selectedJob);

      files.forEach((file) => {
        formData.append("files", file);
      });

      const res = await API.post("/upload-resume/", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
        onUploadProgress: (progressEvent) => {
          const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percent);
        },
      });

      setUploadedResumes(res.data);
      alert("Bulk resume upload completed");
      loadJobs();
      loadResumesByJob(selectedJob);
    } catch (error) {
      console.log(error);
      alert("Upload failed. Check backend terminal.");
    }
  };

  const rankCandidates = async () => {
    if (!selectedJob) {
      alert("Please select a job role first");
      return;
    }

    try {
      const res = await API.post(`/jobs/${selectedJob}/rank/`);
      setRankings(res.data);
      loadJobs();
    } catch (error) {
      console.log(error);
      alert("Ranking failed. Check backend terminal.");
    }
  };

  if (!isLoggedIn) {
    return (
      <div className="login-page">
        <div className="login-card">
          <h1>Smart Talent Selection Engine</h1>
          <h2>Recruiter Login</h2>

          <input
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />

          <input
            placeholder="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <button onClick={login}>Login</button>

          <p className="hint">Use your registered recruiter username and password</p>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <h2>Smart Talent</h2>

        <button onClick={() => setActivePage("dashboard")}>Dashboard</button>
        <button onClick={() => setActivePage("crud")}>Job CRUD</button>
        <button onClick={() => setActivePage("upload")}>Upload Resumes</button>
        <button onClick={() => setActivePage("ranking")}>GenAI Ranking</button>
        <button onClick={logout}>Logout</button>
      </aside>

      <main className="main">
        {activePage === "dashboard" && (
          <section className="card">
            <h1>Recruiter Dashboard</h1>

            <div className="stats">
              <div>
                <h3>Total Job Roles</h3>
                <p>{jobs.length}</p>
              </div>

              <div>
                <h3>Total Resumes</h3>
                <p>{jobs.reduce((sum, job) => sum + job.resume_count, 0)}</p>
              </div>

              <div>
                <h3>GenAI Feature</h3>
                <p>Semantic Ranking</p>
              </div>
            </div>

            <table>
              <thead>
                <tr>
                  <th>Job Role</th>
                  <th>Resumes Uploaded</th>
                  <th>Top Talent</th>
                  <th>Top Score</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {jobs.map((job) => (
                  <tr key={job.id}>
                    <td>{job.title}</td>
                    <td>{job.resume_count}</td>
                    <td>{job.top_candidate}</td>
                    <td>{job.top_score || "-"}</td>
                    <td>
                      <button onClick={() => editJob(job)}>Edit</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        )}

        {activePage === "crud" && (
          <section className="card">
            <h1>Job Role CRUD Operations</h1>

            <input
              placeholder="Job title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />

            <textarea
              placeholder="Paste job description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />

            <button onClick={saveJob}>
              {editingJobId ? "Update Job" : "Create Job"}
            </button>

            {editingJobId && (
              <button
                onClick={() => {
                  setEditingJobId(null);
                  setTitle("");
                  setDescription("");
                }}
              >
                Cancel Edit
              </button>
            )}

            <table>
              <thead>
                <tr>
                  <th>Job Role</th>
                  <th>Resumes</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {jobs.map((job) => (
                  <tr key={job.id}>
                    <td>{job.title}</td>
                    <td>{job.resume_count}</td>
                    <td>
                      <button onClick={() => editJob(job)}>Edit</button>
                      <button className="danger" onClick={() => deleteJob(job.id)}>
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        )}

        {activePage === "upload" && (
          <section className="card">
            <h1>Multi-Format Resume Ingestion Portal</h1>

            <select value={selectedJob} onChange={(e) => handleJobSelection(e.target.value)}>
              <option value="">Select Job Role</option>
              {jobs.map((job) => (
                <option key={job.id} value={job.id}>
                  {job.title}
                </option>
              ))}
            </select>

            <input
              type="file"
              multiple
              accept=".pdf,.docx,.jpg,.jpeg,.png"
              onChange={handleFileChange}
            />

            <p className="hint">
              Selected files: {files.length}
            </p>

            {files.length > 0 && (
              <ul>
                {files.map((file, index) => (
                  <li key={index}>{file.name}</li>
                ))}
              </ul>
            )}

            <button onClick={uploadResumes}>Bulk Upload and Parse with GenAI</button>

            {uploadProgress > 0 && (
              <div className="progress-box">
                <div className="progress-bar" style={{ width: `${uploadProgress}%` }}>
                  {uploadProgress}%
                </div>
              </div>
            )}

            <h2>Uploaded Resumes by Job Role / Batch Date</h2>

            <table>
              <thead>
                <tr>
                  <th>Candidate</th>
                  <th>Email</th>
                  <th>Batch Date</th>
                  <th>Status</th>
                  <th>Error</th>
                  <th>Experience</th>
<th>Top Skills</th>
<th>AI Summary</th>
                </tr>
              </thead>

              <tbody>
                {uploadedResumes.map((resume) => (
                  <tr key={resume.id}>
                    <td>{resume.candidate_name || "-"}</td>
                    <td>{resume.email || "-"}</td>
                    <td>{resume.batch_date}</td>
                    <td>{resume.upload_status}</td>
                    <td>{resume.error_message || "-"}</td>
                    <td>{resume.parsed_profile?.years_experience || 0} years</td>

<td>
  {Array.isArray(resume.parsed_profile?.top_skills)
    ? resume.parsed_profile.top_skills.join(", ")
    : "-"}
</td>

<td>{resume.parsed_profile?.summary || "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        )}

        {activePage === "ranking" && (
          <section className="card">
            <h1>GenAI JD-to-Candidate Ranking Dashboard</h1>

            <select value={selectedJob} onChange={(e) => handleJobSelection(e.target.value)}>
              <option value="">Select Job Role</option>
              {jobs.map((job) => (
                <option key={job.id} value={job.id}>
                  {job.title}
                </option>
              ))}
            </select>

            <button onClick={rankCandidates}>Rank Candidates Using Semantic AI</button>

            <table>
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Candidate</th>
                  <th>Email</th>
                  <th>Years</th>
                  <th>Top Skills</th>
                  <th>Score</th>
                  <th>AI Justification</th>
                </tr>
              </thead>

              <tbody>
                {rankings.map((item, index) => (
                  <tr key={item.id}>
                    <td>{index + 1}</td>
                    <td>{item.resume.candidate_name}</td>
                    <td>{item.resume.email}</td>
                    <td>{item.resume.parsed_profile.years_experience}</td>
                    <td>
                      {Array.isArray(item.resume.parsed_profile.top_skills)
                        ? item.resume.parsed_profile.top_skills.join(", ")
                        : "-"}
                    </td>
                    <td>{item.score}%</td>
                    <td>{item.justification}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;