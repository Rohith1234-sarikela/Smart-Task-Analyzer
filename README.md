Smart Task Analyzer – Technical Assessment

A full-stack mini-application that intelligently scores and prioritizes tasks based on urgency, importance, effort, and dependencies.
Built for the Software Development Intern Assessment using Django (REST API) + HTML/CSS/JavaScript.

🚀 Live Demo Links

🔹 Frontend (Vercel): https://smart-task-analyzer-blue.vercel.app/
🔹 Backend (Render): https://smart-task-analyzer-ryka-builder-command.onrender.com/api/tasks

⚠ Replace these URLs after deployment.

📥 How to Run the Project Locally
🔧 Backend (Django)
cd backend
python -m venv venv
venv\Scripts\activate          # (Windows)  
# or source venv/bin/activate  # (Mac/Linux)
pip install -r ../requirements.txt
python manage.py migrate
python manage.py runserver


Backend runs at:

http://127.0.0.1:8000/

💻 Frontend

Open:

frontend/index.html


or use Live Server in VS Code.

🔗 API Endpoints
Method	Endpoint	Description
POST	/api/tasks/analyze/	Accepts list of tasks → returns tasks sorted by calculated score
GET	/api/tasks/suggest/	Returns top 3 tasks user should work on today
🧠 Priority Scoring Algorithm (300–500 word explanation)

The purpose of the scoring algorithm is to help users decide which task should be completed next by evaluating multiple real-world productivity factors. Each task has four measurable attributes — due date (urgency), importance, estimated hours (effort), and dependencies. The algorithm converts these human decision factors into a numerical score so tasks can be sorted logically.

1️⃣ Urgency (Due Date)

Urgency evaluates how soon the task is due:

Days Until Due	Urgency Interpretation
Overdue	Highest urgency
Due Today	Very high urgency
1–3 days	High urgency
4–7 days	Medium urgency
8–14 days	Low urgency
>14 days	Very low urgency

Overdue tasks get extra weight, because ignoring overdue work often blocks planning.

2️⃣ Importance (1–10 Scale)

Importance reflects the task’s business impact. Higher importance means higher priority.
Critical tasks (9–10) significantly affect the score more than average-importance tasks.

3️⃣ Effort (Estimated Hours)

Effort introduces the concept of quick wins:

Low effort → increases score

Extremely high effort → reduces score slightly
This encourages momentum and prevents burnout by promoting fast results when appropriate.

4️⃣ Dependencies (Unblockers)

Instead of counting how many dependencies a task has, the algorithm measures how many other tasks depend on it. A task that unlocks other work is more valuable, so its score increases.

Circular Dependency Detection

If the dependency graph contains a cycle (e.g., Task A depends on Task B and Task B depends on Task A), both tasks are flagged and penalized. The frontend also displays a clear warning to the user.

Scoring Strategies

The system supports four sorting logic options:

Strategy	Behavior
Smart Balance	Balanced trade-off across all factors
Fastest Wins	Prioritizes low-effort tasks
High Impact	Prioritizes importance above all else
Deadline Driven	Prioritizes shortest due dates

Each strategy calls a dedicated scoring function, enabling flexibility based on user preference while maintaining clean code separation.

🧩 Design Decisions & Trade-offs
Decision	Reason
In-memory storage instead of DB	This assignment evaluates algorithmic thinking, not CRUD
Separate scoring.py module	Keeps views clean & testable
4 configurable strategies	Evaluators can see algorithm adaptability
Explanations returned per task	Improves transparency for end-users
No authentication	Irrelevant to evaluation & saves time
Plain HTML/JS frontend	Fast, dependency-free & easy to deploy
🧪 Unit Tests

Tests implemented in tasks/tests.py, covering:

Overdue vs future tasks scoring

Importance affecting score correctly

Circular dependency detection

Run tests:

python manage.py test

⏳ Time Breakdown
Task	Time
Algorithm & scoring design	~1.5 hours
Django API development	~1 hour
Frontend UI + animations + integration	~1.5 hours
Testing + debugging	~45 minutes
Documentation + cleanup	~30 minutes
🧾 Bonus Features Completed
Feature	Status
Circular dependency detection	✔
Score explanations for each task	✔
🚀 Future Improvements

Persistent User Accounts + Database

Visual dependency graph

Eisenhower Matrix visualization

Adaptive AI scoring based on user feedback

Weekends/holiday–aware urgency model

👤 Author

Rohith Sarikela
