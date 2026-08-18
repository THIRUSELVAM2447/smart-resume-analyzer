# backend/app/services/job_analysis_service.py

import re
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.job import Job
from app.models.job_analysis import JobAnalysis
from app.models.resume import Resume, ResumeVersion
from app.models.user import User


class JobAnalysisService:
    """
    Business logic for ATS-style job/resume analysis.

    The service:
    1. Verifies that the job belongs to the authenticated user.
    2. Verifies that the resume version belongs to the authenticated user.
    3. Extracts skills from the resume.
    4. Compares resume skills with the job description.
    5. Calculates an ATS-style score.
    6. Generates missing skills and recommendations.
    7. Stores the analysis result in JobAnalysis.
    8. Retrieves previously created analyses.

    No HTTP exceptions are raised from this service.
    """

    # ------------------------------------------------------------------
    # KNOWN TECHNICAL SKILLS
    # ------------------------------------------------------------------

    KNOWN_SKILLS = {
        "java",
        "python",
        "c",
        "c++",
        "c#",
        "javascript",
        "typescript",
        "html",
        "css",
        "react",
        "react.js",
        "angular",
        "vue",
        "node",
        "node.js",
        "express",
        "spring",
        "spring boot",
        "hibernate",
        "rest",
        "rest api",
        "rest apis",
        "api",
        "sql",
        "mysql",
        "postgresql",
        "mongodb",
        "oracle",
        "redis",
        "git",
        "github",
        "docker",
        "kubernetes",
        "aws",
        "azure",
        "gcp",
        "linux",
        "fastapi",
        "django",
        "flask",
        "pandas",
        "numpy",
        "scikit-learn",
        "tensorflow",
        "pytorch",
        "machine learning",
        "deep learning",
        "artificial intelligence",
        "data structures",
        "data structures and algorithms",
        "algorithms",
        "oop",
        "object oriented programming",
        "jdbc",
        "dbms",
        "database",
        "spring security",
        "microservices",
        "maven",
        "gradle",
        "junit",
        "tailwind",
        "bootstrap",
    }

    # ------------------------------------------------------------------
    # STOP WORDS
    # ------------------------------------------------------------------

    STOP_WORDS = {
        "the",
        "and",
        "or",
        "to",
        "of",
        "in",
        "for",
        "with",
        "on",
        "a",
        "an",
        "is",
        "are",
        "be",
        "as",
        "by",
        "from",
        "at",
        "this",
        "that",
        "we",
        "you",
        "your",
        "our",
        "will",
        "have",
        "has",
        "must",
        "should",
        "can",
        "work",
        "working",
        "experience",
        "years",
        "year",
        "job",
        "role",
        "candidate",
        "developer",
        "development",
        "team",
        "strong",
        "good",
        "knowledge",
        "skills",
        "skill",
        "ability",
        "required",
        "requirements",
        "responsibilities",
    }

    # ------------------------------------------------------------------
    # PUBLIC METHOD
    # ------------------------------------------------------------------

    def analyze_job(
        self,
        db: Session,
        user: User,
        job_id: int,
        resume_version_id: int,
    ) -> JobAnalysis | None:
        """
        Analyze a job against a specific resume version.

        Returns:
            JobAnalysis:
                When both resources belong to the authenticated user.

            None:
                When the job does not exist, belongs to another user,
                or the resume version does not belong to the user.
        """

        # --------------------------------------------------------------
        # 1. Get the authenticated user's job
        # --------------------------------------------------------------

        job = self._get_user_job(
            db=db,
            user=user,
            job_id=job_id,
        )

        if job is None:
            return None

        # --------------------------------------------------------------
        # 2. Get the authenticated user's resume version
        # --------------------------------------------------------------

        resume_version = self._get_user_resume_version(
            db=db,
            user=user,
            resume_version_id=resume_version_id,
        )

        if resume_version is None:
            return None

        # --------------------------------------------------------------
        # 3. Extract resume skills
        # --------------------------------------------------------------

        resume_skills = self._extract_resume_skills(
            resume_version.skills
        )

        # --------------------------------------------------------------
        # 4. Extract skills mentioned in job description
        # --------------------------------------------------------------

        job_description = job.description or ""

        job_skills = self._extract_job_skills(
            job_description
        )

        # --------------------------------------------------------------
        # 5. Compare skills
        # --------------------------------------------------------------

        matched_skills, missing_skills, extra_skills = (
            self._compare_skills(
                resume_skills=resume_skills,
                job_skills=job_skills,
            )
        )

        # --------------------------------------------------------------
        # 6. Calculate skill score
        # --------------------------------------------------------------

        skill_score = self._calculate_skill_score(
            matched_skills=matched_skills,
            job_skills=job_skills,
        )

        # --------------------------------------------------------------
        # 7. Calculate other ATS factors
        # --------------------------------------------------------------

        keyword_score = self._calculate_keyword_score(
            job_description=job_description,
            resume_text=resume_version.raw_text or "",
        )

        grammar_issues = self._find_basic_grammar_issues(
            resume_version.raw_text or ""
        )

        grammar_score = self._calculate_grammar_score(
            grammar_issues
        )

        # --------------------------------------------------------------
        # 8. Calculate overall score
        # --------------------------------------------------------------

        overall_score = self._calculate_overall_score(
            skill_score=skill_score,
            keyword_score=keyword_score,
            grammar_score=grammar_score,
        )

        # --------------------------------------------------------------
        # 9. Generate recommendations
        # --------------------------------------------------------------

        recommendations = self._generate_recommendations(
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            grammar_issues=grammar_issues,
            keyword_score=keyword_score,
            overall_score=overall_score,
        )

        # --------------------------------------------------------------
        # 10. Save analysis snapshot
        # --------------------------------------------------------------

        analysis_snapshot = {
            "job": {
                "id": job.id,
                "title": job.title,
                "company_name": job.company_name,
                "source_type": job.source_type,
            },
            "resume": {
                "resume_version_id": resume_version.id,
                "version_number": resume_version.version_number,
                "full_name": resume_version.full_name,
            },
            "scores": {
                "overall_score": overall_score,
                "skill_score": skill_score,
                "keyword_score": keyword_score,
                "grammar_score": grammar_score,
            },
            "skills": {
                "job_skills": job_skills,
                "resume_skills": resume_skills,
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "extra_skills": extra_skills,
            },
            "grammar_issues": grammar_issues,
            "recommendations": recommendations,
        }

        # --------------------------------------------------------------
        # 11. Create database record
        # --------------------------------------------------------------

        analysis = JobAnalysis(
            job_id=job.id,
            resume_version_id=resume_version.id,
            overall_score=overall_score,
            skill_score=skill_score,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            extra_skills=extra_skills,
            grammar_issues=grammar_issues,
            recommendations=recommendations,
            analysis_snapshot=analysis_snapshot,
        )

        db.add(analysis)

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise

        db.refresh(analysis)

        return analysis

    # ------------------------------------------------------------------
    # GET ONE ANALYSIS
    # ------------------------------------------------------------------

    def get_analysis(
        self,
        db: Session,
        user: User,
        analysis_id: int,
    ) -> JobAnalysis | None:
        """
        Return one ATS analysis only when the related Job
        belongs to the authenticated user.

        Returns None when:
        - the analysis does not exist
        - the related job does not belong to the user
        """

        stmt = (
            select(JobAnalysis)
            .join(
                Job,
                Job.id == JobAnalysis.job_id,
            )
            .where(
                JobAnalysis.id == analysis_id,
                Job.user_id == user.id,
            )
        )

        return db.scalar(stmt)

    # ------------------------------------------------------------------
    # GET ALL ANALYSES FOR A JOB
    # ------------------------------------------------------------------

    def get_job_analyses(
        self,
        db: Session,
        user: User,
        job_id: int,
    ) -> list[JobAnalysis] | None:
        """
        Return all ATS analyses for a job belonging to
        the authenticated user.

        Returns None when the job does not exist or does
        not belong to the authenticated user.

        Results are returned newest first.
        """

        # --------------------------------------------------------------
        # 1. Verify that the job belongs to the authenticated user
        # --------------------------------------------------------------

        job_stmt = select(Job).where(
            Job.id == job_id,
            Job.user_id == user.id,
        )

        job = db.scalar(job_stmt)

        if job is None:
            return None

        # --------------------------------------------------------------
        # 2. Retrieve all analyses for the job
        # --------------------------------------------------------------

        analysis_stmt = (
            select(JobAnalysis)
            .where(
                JobAnalysis.job_id == job_id,
            )
            .order_by(
                JobAnalysis.created_at.desc()
            )
        )

        return list(
            db.scalars(analysis_stmt).all()
        )

    # ------------------------------------------------------------------
    # DATABASE HELPERS
    # ------------------------------------------------------------------

    def _get_user_job(
        self,
        db: Session,
        user: User,
        job_id: int,
    ) -> Job | None:
        """
        Return a job only when it belongs to the authenticated user.
        """

        stmt = select(Job).where(
            Job.id == job_id,
            Job.user_id == user.id,
        )

        return db.scalar(stmt)

    def _get_user_resume_version(
        self,
        db: Session,
        user: User,
        resume_version_id: int,
    ) -> ResumeVersion | None:
        """
        Return a resume version only when the parent Resume belongs
        to the authenticated user.
        """

        stmt = (
            select(ResumeVersion)
            .join(
                Resume,
                Resume.id == ResumeVersion.resume_id,
            )
            .where(
                ResumeVersion.id == resume_version_id,
                Resume.user_id == user.id,
            )
        )

        return db.scalar(stmt)

    # ------------------------------------------------------------------
    # RESUME SKILLS
    # ------------------------------------------------------------------

    def _extract_resume_skills(
        self,
        skills: Any,
    ) -> list[str]:
        """
        Convert the ResumeVersion.skills JSON value into a clean
        list of strings.

        Supports:

            ["Java", "Python", "SQL"]

        and:

            {
                "programming": ["Java", "Python"],
                "database": ["MySQL"]
            }
        """

        collected: list[str] = []

        self._collect_skill_values(
            value=skills,
            output=collected,
        )

        normalized: dict[str, str] = {}

        for skill in collected:
            cleaned = self._clean_skill(skill)

            if not cleaned:
                continue

            key = self._normalize_skill(cleaned)

            if key not in normalized:
                normalized[key] = cleaned

        return sorted(
            normalized.values(),
            key=str.lower,
        )

    def _collect_skill_values(
        self,
        value: Any,
        output: list[str],
    ) -> None:
        """
        Recursively collect string values from JSON.
        """

        if value is None:
            return

        if isinstance(value, str):
            output.append(value)
            return

        if isinstance(value, list):
            for item in value:
                self._collect_skill_values(
                    value=item,
                    output=output,
                )
            return

        if isinstance(value, dict):
            for item in value.values():
                self._collect_skill_values(
                    value=item,
                    output=output,
                )

    # ------------------------------------------------------------------
    # JOB SKILLS
    # ------------------------------------------------------------------

    def _extract_job_skills(
        self,
        job_description: str,
    ) -> list[str]:
        """
        Detect known technical skills inside the job description.
        """

        normalized_description = self._normalize_text(
            job_description
        )

        detected: dict[str, str] = {}

        # Longest skills first so that phrases such as
        # "spring boot" are checked before "spring".
        sorted_skills = sorted(
            self.KNOWN_SKILLS,
            key=len,
            reverse=True,
        )

        for skill in sorted_skills:
            normalized_skill = self._normalize_text(skill)

            if not normalized_skill:
                continue

            pattern = (
                r"(?<![a-z0-9])"
                + re.escape(normalized_skill)
                + r"(?![a-z0-9])"
            )

            if re.search(
                pattern,
                normalized_description,
            ):
                detected[
                    self._normalize_skill(skill)
                ] = skill

        return sorted(
            detected.values(),
            key=str.lower,
        )

    # ------------------------------------------------------------------
    # SKILL COMPARISON
    # ------------------------------------------------------------------

    def _compare_skills(
        self,
        resume_skills: list[str],
        job_skills: list[str],
    ) -> tuple[list[str], list[str], list[str]]:
        """
        Compare resume skills against job skills.
        """

        resume_map = {
            self._normalize_skill(skill): skill
            for skill in resume_skills
        }

        job_map = {
            self._normalize_skill(skill): skill
            for skill in job_skills
        }

        matched = []
        missing = []
        extra = []

        for normalized_skill, original_skill in job_map.items():
            if normalized_skill in resume_map:
                matched.append(
                    resume_map[normalized_skill]
                )
            else:
                missing.append(original_skill)

        for normalized_skill, original_skill in resume_map.items():
            if normalized_skill not in job_map:
                extra.append(original_skill)

        matched.sort(key=str.lower)
        missing.sort(key=str.lower)
        extra.sort(key=str.lower)

        return matched, missing, extra

    # ------------------------------------------------------------------
    # SCORING
    # ------------------------------------------------------------------

    def _calculate_skill_score(
        self,
        matched_skills: list[str],
        job_skills: list[str],
    ) -> int:
        """
        Calculate skill match score from 0-100.
        """

        if not job_skills:
            # If no recognizable technical skills were found
            # in the job description, don't penalize the resume.
            return 70

        score = (
            len(matched_skills)
            / len(job_skills)
        ) * 100

        return self._clamp_score(score)

    def _calculate_keyword_score(
        self,
        job_description: str,
        resume_text: str,
    ) -> int:
        """
        Calculate a simple keyword overlap score.

        This looks at meaningful words in the job description and
        checks how many are present in the resume.
        """

        job_words = self._extract_meaningful_words(
            job_description
        )

        resume_words = self._extract_meaningful_words(
            resume_text
        )

        if not job_words:
            return 70

        matched_count = len(
            job_words.intersection(resume_words)
        )

        score = (
            matched_count
            / len(job_words)
        ) * 100

        return self._clamp_score(score)

    def _calculate_grammar_score(
        self,
        grammar_issues: list[str],
    ) -> int:
        """
        Calculate a simple grammar/readability score.
        """

        if not grammar_issues:
            return 100

        penalty = min(
            len(grammar_issues) * 5,
            50,
        )

        return max(
            0,
            100 - penalty,
        )

    def _calculate_overall_score(
        self,
        skill_score: int,
        keyword_score: int,
        grammar_score: int,
    ) -> int:
        """
        Weighted ATS score.

        Skills   = 60%
        Keywords = 30%
        Grammar  = 10%
        """

        score = (
            (skill_score * 0.60)
            + (keyword_score * 0.30)
            + (grammar_score * 0.10)
        )

        return self._clamp_score(score)

    # ------------------------------------------------------------------
    # GRAMMAR / QUALITY CHECK
    # ------------------------------------------------------------------

    def _find_basic_grammar_issues(
        self,
        resume_text: str,
    ) -> list[str]:
        """
        Perform lightweight resume text quality checks.

        This is intentionally conservative and does not claim to
        replace a dedicated grammar model.
        """

        issues: list[str] = []

        if not resume_text.strip():
            issues.append(
                "Resume does not contain readable text."
            )
            return issues

        lines = [
            line.strip()
            for line in resume_text.splitlines()
            if line.strip()
        ]

        # Detect repeated spaces.
        if re.search(r"[ \t]{3,}", resume_text):
            issues.append(
                "Multiple consecutive spaces were detected."
            )

        # Detect obvious repeated words.
        repeated_word_pattern = re.compile(
            r"\b([A-Za-z]+)\s+\1\b",
            flags=re.IGNORECASE,
        )

        if repeated_word_pattern.search(resume_text):
            issues.append(
                "Repeated words were detected in the resume text."
            )

        # Detect extremely long lines.
        long_lines = [
            line
            for line in lines
            if len(line) > 180
        ]

        if long_lines:
            issues.append(
                "Some resume lines are unusually long and may "
                "reduce readability."
            )

        # Detect common typo patterns.
        typo_patterns = {
            "teh": "Possible typo: 'teh'.",
            "recieve": "Possible typo: 'recieve'.",
            "seperate": "Possible typo: 'seperate'.",
            "occured": "Possible typo: 'occured'.",
            "enviroment": "Possible typo: 'enviroment'.",
        }

        lower_text = resume_text.lower()

        for typo, message in typo_patterns.items():
            if re.search(
                r"\b" + re.escape(typo) + r"\b",
                lower_text,
            ):
                issues.append(message)

        return issues

    # ------------------------------------------------------------------
    # RECOMMENDATIONS
    # ------------------------------------------------------------------

    def _generate_recommendations(
        self,
        matched_skills: list[str],
        missing_skills: list[str],
        grammar_issues: list[str],
        keyword_score: int,
        overall_score: int,
    ) -> list[str]:
        """
        Generate actionable recommendations based on the analysis.
        """

        recommendations: list[str] = []

        if missing_skills:
            displayed = ", ".join(
                missing_skills[:8]
            )

            recommendations.append(
                f"Consider adding relevant skills that you genuinely "
                f"possess but are missing from the resume: {displayed}."
            )

        if keyword_score < 60:
            recommendations.append(
                "Improve keyword alignment by using terminology "
                "from the job description where it accurately "
                "describes your experience."
            )

        if grammar_issues:
            recommendations.append(
                "Review the resume for grammar, spacing, spelling, "
                "and readability issues."
            )

        if not matched_skills:
            recommendations.append(
                "The resume has no detected technical skill matches "
                "with the job description. Review the skills section "
                "and tailor it to the target role."
            )

        elif len(matched_skills) >= 3:
            recommendations.append(
                "Your resume contains several skills relevant to "
                "the target job. Highlight those skills clearly "
                "in your summary and project descriptions."
            )

        if overall_score < 50:
            recommendations.append(
                "The resume currently has low alignment with this "
                "job. Tailor the summary, skills, and project "
                "descriptions to the role."
            )
        elif overall_score < 75:
            recommendations.append(
                "The resume has moderate alignment. Focus on the "
                "missing skills and job-specific keywords to "
                "improve the ATS score."
            )
        else:
            recommendations.append(
                "The resume has strong alignment with the target "
                "job. Continue emphasizing measurable achievements "
                "and relevant technical skills."
            )

        # Remove duplicates while preserving order.
        unique_recommendations = list(
            dict.fromkeys(recommendations)
        )

        return unique_recommendations

    # ------------------------------------------------------------------
    # TEXT HELPERS
    # ------------------------------------------------------------------

    def _extract_meaningful_words(
        self,
        text: str,
    ) -> set[str]:
        """
        Extract meaningful words for basic keyword comparison.
        """

        normalized = self._normalize_text(text)

        words = re.findall(
            r"\b[a-z0-9][a-z0-9+#.-]*\b",
            normalized,
        )

        return {
            word
            for word in words
            if len(word) > 2
            and word not in self.STOP_WORDS
        }

    def _normalize_text(
        self,
        value: str,
    ) -> str:
        """
        Normalize text for comparison.
        """

        value = value.lower()

        value = value.replace(
            "–",
            "-",
        ).replace(
            "—",
            "-",
        )

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return value.strip()

    def _normalize_skill(
        self,
        skill: str,
    ) -> str:
        """
        Normalize a skill name for comparison.
        """

        normalized = self._normalize_text(
            skill
        )

        aliases = {
            "react.js": "react",
            "node.js": "node",
            "rest apis": "rest api",
            "rest api": "rest api",
            "data structures & algorithms":
                "data structures and algorithms",
            "object oriented programming":
                "oop",
        }

        return aliases.get(
            normalized,
            normalized,
        )

    def _clean_skill(
        self,
        skill: str,
    ) -> str:
        """
        Clean an individual resume skill.
        """

        cleaned = skill.strip()

        cleaned = re.sub(
            r"\s+",
            " ",
            cleaned,
        )

        cleaned = cleaned.rstrip(
            ".,;:"
        )

        return cleaned

    def _clamp_score(
        self,
        score: float,
    ) -> int:
        """
        Keep score between 0 and 100.
        """

        return max(
            0,
            min(
                100,
                int(round(score)),
            ),
        )