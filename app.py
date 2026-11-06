from flask import Flask, render_template, request, jsonify
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

app = Flask(__name__)

# Illustrative career profiles. Replace/expand these with validated data
# before making real-world claims about recommendation accuracy.
FEATURES = [
    "python", "java", "web", "maths", "problem_solving",
    "creativity", "communication", "data_interest", "ai_interest",
    "security_interest", "design_interest"
]

CAREERS = {
    "AI / ML Engineer": {
        "vector": [5, 2, 1, 5, 5, 3, 2, 4, 5, 1, 1],
        "skills": ["Python", "Mathematics", "Statistics", "Machine Learning", "Deep Learning"],
        "roadmap": ["Strengthen Python and problem-solving", "Learn statistics, probability and linear algebra",
                    "Study machine learning with scikit-learn", "Build prediction and recommendation projects",
                    "Create a GitHub portfolio and apply for internships"],
        "description": "Builds intelligent systems that learn from data and make predictions."
    },
    "Data Analyst": {
        "vector": [3, 1, 2, 4, 3, 2, 4, 5, 1, 1, 1],
        "skills": ["Excel", "SQL", "Python", "Statistics", "Power BI or Tableau"],
        "roadmap": ["Learn Excel and data cleaning", "Learn SQL queries and joins",
                    "Practice Python with Pandas", "Create dashboards using Power BI",
                    "Complete two real-world data analysis projects"],
        "description": "Finds patterns in data and communicates insights to support decisions."
    },
    "Python Developer": {
        "vector": [5, 2, 2, 3, 5, 2, 2, 2, 3, 1, 1],
        "skills": ["Python", "OOP", "Data Structures", "APIs", "SQL and Git"],
        "roadmap": ["Master Python fundamentals and OOP", "Practice data structures and algorithms",
                    "Build REST APIs using Flask", "Connect applications to databases",
                    "Publish projects and prepare for coding interviews"],
        "description": "Develops applications, automation tools, APIs and backend services using Python."
    },
    "Full Stack Developer": {
        "vector": [3, 3, 5, 2, 4, 4, 3, 1, 1, 1, 3],
        "skills": ["HTML", "CSS", "JavaScript", "React", "Backend and databases"],
        "roadmap": ["Learn HTML, CSS and JavaScript", "Build responsive web pages",
                    "Learn React and component-based development", "Learn Flask/Node and SQL",
                    "Deploy a complete full-stack application"],
        "description": "Builds both the user-facing interface and the server-side logic of websites."
    },
    "Cybersecurity Analyst": {
        "vector": [2, 2, 1, 3, 4, 1, 3, 1, 1, 5, 1],
        "skills": ["Networking", "Linux", "Security fundamentals", "Python", "Incident analysis"],
        "roadmap": ["Understand computer networks and operating systems", "Learn Linux and command-line tools",
                    "Study security fundamentals and common vulnerabilities", "Practice in legal lab environments",
                    "Build a security learning portfolio and pursue entry-level roles"],
        "description": "Helps protect systems, networks and information from security threats."
    },
    "UI/UX Designer": {
        "vector": [1, 1, 2, 1, 2, 5, 4, 1, 1, 1, 5],
        "skills": ["Design principles", "Figma", "Wireframing", "Prototyping", "User research"],
        "roadmap": ["Study design principles and accessibility", "Learn Figma",
                    "Create wireframes and interactive prototypes", "Conduct basic user testing",
                    "Publish three case studies in a design portfolio"],
        "description": "Designs clear, accessible and useful digital experiences for people."
    },
    "Java Developer": {
        "vector": [1, 5, 2, 3, 4, 2, 2, 1, 1, 1, 1],
        "skills": ["Java", "OOP", "Data Structures", "SQL", "Spring Boot"],
        "roadmap": ["Learn Java syntax and object-oriented programming", "Practice collections and data structures",
                    "Learn SQL and database connectivity", "Build REST APIs using Spring Boot",
                    "Create and document a portfolio project"],
        "description": "Develops software applications and backend services using Java."
    }
}

# Several illustrative examples around each career profile make KNN usable
# for a small demonstration dataset. This is a teaching prototype, not validated data.
X, y = [], []
for label, info in CAREERS.items():
    center = np.array(info["vector"], dtype=float)
    X.append(center)
    y.append(label)
    for delta in (-0.35, -0.15, 0.15, 0.35):
        X.append(np.clip(center + delta, 0, 5))
        y.append(label)

model = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=3, weights="distance"))
model.fit(np.array(X), np.array(y))

def normalize_profile(payload):
    values = []
    for key in FEATURES:
        try:
            value = float(payload.get(key, 0))
        except (TypeError, ValueError):
            value = 0
        values.append(min(5, max(0, value)))
    return np.array(values, dtype=float).reshape(1, -1)

@app.route("/")
def home():
    return render_template("index.html", features=FEATURES)

@app.route("/recommend", methods=["POST"])
def recommend():
    payload = request.get_json(silent=True) or {}
    profile = normalize_profile(payload)
    distances, indices = model.named_steps["kneighborsclassifier"].kneighbors(
        model.named_steps["standardscaler"].transform(profile), n_neighbors=3
    )
    # Aggregate inverse-distance votes by career, then convert to a relative match score.
    votes = {}
    for distance, idx in zip(distances[0], indices[0]):
        career = y[idx]
        votes[career] = votes.get(career, 0) + 1 / (float(distance) + 0.15)
    # Similarity to each career prototype provides a useful ranking signal.
    scaler = model.named_steps["standardscaler"]
    q = scaler.transform(profile)[0]
    ranked = []
    for name, info in CAREERS.items():
        c = scaler.transform(np.array(info["vector"], dtype=float).reshape(1, -1))[0]
        dist = float(np.linalg.norm(q - c))
        ranked.append((name, dist, votes.get(name, 0)))
    ranked.sort(key=lambda item: (item[2], -item[1]), reverse=True)
    # Relative score based on distance; explicitly a demo compatibility indicator.
    results = []
    for name, dist, vote in ranked[:4]:
        score = round(100 / (1 + dist), 1)
        info = CAREERS[name]
        # Skill gaps are based on low self-ratings in relevant feature areas.
        gaps = []
        if name == "AI / ML Engineer":
            checks = [("python", "Python"), ("maths", "Mathematics"), ("problem_solving", "Problem-solving")]
        elif name == "Data Analyst":
            checks = [("data_interest", "Data analysis"), ("maths", "Statistics"), ("python", "Python")]
        elif name == "Python Developer":
            checks = [("python", "Python"), ("problem_solving", "Problem-solving")]
        elif name == "Full Stack Developer":
            checks = [("web", "Web development"), ("problem_solving", "Problem-solving")]
        elif name == "Cybersecurity Analyst":
            checks = [("security_interest", "Cybersecurity"), ("problem_solving", "Problem-solving")]
        elif name == "UI/UX Designer":
            checks = [("design_interest", "UI/UX design"), ("creativity", "Creativity")]
        else:
            checks = [("java", "Java"), ("problem_solving", "Problem-solving")]
        for key, label in checks:
            if payload.get(key, 0) < 3:
                gaps.append(label)
        results.append({
            "career": name, "score": score, "description": info["description"],
            "skills": info["skills"], "roadmap": info["roadmap"],
            "gaps": gaps or ["Keep practising and build portfolio projects"]
        })
    return jsonify({
        "student": payload.get("student_name", "Student"),
        "education": payload.get("education", "Not specified"),
        "results": results,
        "note": "Demo compatibility scores based on illustrative career profiles. They are guidance indicators, not guarantees or validated aptitude-test results."
    })

if __name__ == "__main__":
    app.run(debug=True)
