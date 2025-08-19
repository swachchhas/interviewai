// app/static/js/app.js
document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("resume-form");
  const loading = document.getElementById("loading");
  const questionsSection = document.getElementById("questions-section");
  const detailsSection = document.getElementById("details-section");
  const generateFinalBtn = document.getElementById("generate-final-btn");
  const fileInput = document.getElementById("resume_file");
const fileBtn = document.getElementById("file-btn");
const fileName = document.getElementById("file-name");

fileBtn.addEventListener("click", () => fileInput.click());

fileInput.addEventListener("change", () => {
  if (fileInput.files.length > 0) {
    fileName.textContent = fileInput.files[0].name;
  } else {
    fileName.textContent = "No file chosen";
  }
});



  const MAX_RESUME_LENGTH = 1500;

  if (!form) {
    console.error("⚠️ resume-form not found in DOM.");
    return;
  }

  // --- Step 1: Upload Resume ---
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const fileInput = document.getElementById("resume_file");
    if (!fileInput || !fileInput.files.length) {
      alert("Please upload a file!");
      return;
    }

    const formData = new FormData();
    formData.append("resume_file", fileInput.files[0]);

    loading.style.display = "block";
    questionsSection.innerHTML = "";
    detailsSection.style.display = "none";

    try {
      const response = await fetch("/upload", {
        method: "POST",
        body: formData
      });

      const data = await response.json();
      loading.style.display = "none";

      if (data.error) {
        alert(data.error);
        return;
      }

      // Show details section
      detailsSection.style.display = "flex";

      // Truncate resume if too long
      let resumeText = data.resume_text || "";
      if (resumeText.length > MAX_RESUME_LENGTH) {
        resumeText = resumeText.slice(0, MAX_RESUME_LENGTH) + "\n\n[Truncated resume]";
      }

      // Store in dataset for step 2
      detailsSection.dataset.resumeText = resumeText;
    } catch (err) {
      loading.style.display = "none";
      alert("Error uploading resume.");
      console.error("Upload error:", err);
    }
  });

  // --- Step 2: Generate AI Questions ---
  if (generateFinalBtn) {
    generateFinalBtn.addEventListener("click", async () => {
      const resumeText = detailsSection.dataset.resumeText;
      const role = document.getElementById("role").value || "";
      const skills = document.getElementById("skills").value || "";
      const years = document.getElementById("years").value || "";

      if (!resumeText) {
        alert("Please upload a resume first!");
        return;
      }

      loading.style.display = "block";
      questionsSection.innerHTML = "";

      try {
        const response = await fetch("/generate_questions", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ resume: resumeText, role, skills, years })
        });

        const data = await response.json();
        loading.style.display = "none";

        if (data.error) {
          alert(data.error);
          return;
        }

        if (data.questions && data.questions.length) {
          questionsSection.innerHTML = ""; // Clear previous
          data.questions.forEach((q) => {
            const card = document.createElement("div");
            card.className = "question-card fade-in";
            card.textContent = q;
            questionsSection.appendChild(card);
          });
        } else {
          questionsSection.innerHTML = "<p>No questions generated.</p>";
        }
      } catch (err) {
        loading.style.display = "none";
        alert("Error generating questions.");
        console.error("Question generation error:", err);
      }
    });
  } else {
    console.error("⚠️ generate-final-btn not found in DOM.");
  }
});
