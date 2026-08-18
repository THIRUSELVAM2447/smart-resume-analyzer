from pprint import pprint
from app.services.resume_parser_service import ResumeParserService


text = """THIRUSELVAM J
ASPIRING JAVA FULL STACK DEVELOPER

+91 9342041363 | TAMIL NADU, INDIA | THIRUSELVAM.J.DEV@GAMIL.COM |
WWW.LINKEDIN.COM/IN/THIRUSELVAM-J

Objective
Motivated Information Technology student with strong foundations in Java, SQL,
JDBC, OOP, and Web Development. Seeking an entry-level software development
opportunity to apply problem-solving skills, contribute to real-world projects, and
grow as a Java Developer.

Skills & abilities
Java, Python, SQL, MySQL, HTML, CSS, JavaScript, OOP, Data Structures &
Algorithms, DBMS, Git, GitHub, Problem Solving, Debugging, ChatGPT, Google
Gemini, GitHub, Google Colab, Communication, Teamwork, Time Management,
Quick Learning.

Projects
Bus Reservation System | (Java, JDBC, MSQL)
• Developed a database-driven application for ticket booking, seat
reservation, and passenger management using Java, JDBC, MySQL, and
OOP principles

Portfolio | (HTML, CSS, JavaScript)
• Developed a responsive portfolio website to present personal
information, technical skills, and projects.

Education
SRI MUTHUKUMARAN INSTITUTE OF TECHNOLOGY
Affiliated with anna university | B. Tech in Information Technology
2023 – 2027 (Expected)
Earned a 7.62 CGPA and completed relevant coursework in web development,
database management, and software engineering.

Communication
Strong communication skills with the ability to collaborate effectively with team
members and stakeholders.

Workshops & Training
Artificial Intelligence and Machine Learning Workshop – DataMites
• Attended a workshop on AI tools, Machine Learning concepts, and real-
world applications.
• Acquired foundational knowledge of AI and Machine Learning
technologies.

Interests
Exploring Software Development Technologies | Building Programming projects |
Learning new Technical Skills | Cricket and Team Activities"""


parser = ResumeParserService()
result = parser.parse(text)

pprint(result)