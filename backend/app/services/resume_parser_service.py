import re


class ResumeParserService:
    """
    Rule-based resume parser.

    Converts raw resume text into structured fields without using
    an external AI/LLM service.

    This service:
    - does not access the database
    - does not create database sessions
    - does not modify ResumeVersion objects
    - does not raise HTTPException
    """

    EMAIL_PATTERN = re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    )

    PHONE_PATTERN = re.compile(
        r"(?<!\d)(?:\+?\d{1,3}[\s.-]?)?"
        r"(?:\(?\d{2,5}\)?[\s.-]?)?"
        r"\d{3,5}[\s.-]?\d{3,5}(?!\d)"
    )

    LINKEDIN_PATTERN = re.compile(
        r"(?:https?://)?(?:www\.)?linkedin\.com/in/[A-Za-z0-9._%-]+",
        re.IGNORECASE,
    )

    GITHUB_PATTERN = re.compile(
        r"(?:https?://)?(?:www\.)?github\.com/[A-Za-z0-9._-]+",
        re.IGNORECASE,
    )

    LOCATION_PREFIX_PATTERN = re.compile(
        r"^(?:location|based in|address)\s*[:\-]\s*(.+)$",
        re.IGNORECASE,
    )

    LOCATION_KEYWORD_PATTERNS = [
        re.compile(
            r"\b(?:Tamil Nadu|Karnataka|Kerala|"
            r"Andhra Pradesh|Telangana|Maharashtra|"
            r"Delhi)\b",
            re.IGNORECASE,
        ),
        re.compile(
            r"\b(?:India|United States|USA|UK|"
            r"United Kingdom)\b",
            re.IGNORECASE,
        ),
    ]

    # Used to reject degree/education text when detecting a person's name.
    DEGREE_KEYWORDS = {
        "bachelor",
        "master",
        "diploma",
        "phd",
        "btech",
        "mtech",
        "bsc",
        "msc",
        "be",
        "me",
        "bca",
        "mca",
        "bcom",
        "mcom",
        "university",
        "institute",
        "college",
        "technology",
        "engineering",
        "education",
    }

    # Used to reject job titles when detecting a person's name and
    # to identify stray OCR layout noise.
    JOB_TITLE_KEYWORDS = {
        "developer",
        "engineer",
        "designer",
        "manager",
        "intern",
        "analyst",
        "consultant",
        "specialist",
        "architect",
        "administrator",
        "executive",
        "officer",
        "programmer",
        "technician",
    }

    SECTION_ALIASES = {
        "summary": {
            "summary",
            "objective",
            "profile",
            "professional summary",
            "career objective",
            "about me",
        },
        "skills": {
            "skills",
            "skill",
            "technical skills",
            "skills & abilities",
            "technical skills & abilities",
        },
        "experience": {
            "experience",
            "work experience",
            "professional experience",
            "employment history",
            "work history",
            "work flow",
        },
        "education": {
            "education",
            "academic background",
            "academic qualification",
            "qualifications",
        },
        "projects": {
            "projects",
            "project",
            "academic projects",
            "personal projects",
            "key projects",
        },
        "certifications": {
            "certifications",
            "certificates",
            "certification",
            "training & certifications",
            "training and certifications",
        },
        "achievements": {
            "achievements",
            "accomplishments",
            "awards",
            "honors",
        },
    }

    # Valid resume sections that currently have no dedicated fields.
    # They still act as boundaries.
    NON_STORED_SECTIONS = {
        "communication",
        "workshops",
        "workshops & training",
        "training",
        "interests",
        "hobbies",
        "languages",
        "language",
    }

    def parse(self, raw_text: str) -> dict:
        """
        Parse raw resume text into structured fields.
        """
        if not raw_text or not raw_text.strip():
            return self._empty_result()

        text = self._normalize_text(raw_text)

        raw_lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        lines = self._merge_wrapped_lines(raw_lines)

        full_name = self._extract_full_name(lines)
        sections = self._extract_sections(lines, full_name)

        return {
            "full_name": full_name,
            "email": self._extract_email(text),
            "phone": self._extract_phone(text),
            "location": self._extract_location(lines),
            "linkedin_url": self._extract_linkedin(text),
            "github_url": self._extract_github(text),
            "summary": sections.get("summary"),
            "skills": self._extract_skills(
                sections.get("skills")
            ),
            "experience": self._extract_list_section(
                sections.get("experience")
            ),
            "education": self._extract_list_section(
                sections.get("education")
            ),
            "projects": self._extract_list_section(
                sections.get("projects")
            ),
            "certifications": self._extract_list_section(
                sections.get("certifications")
            ),
            "achievements": self._extract_list_section(
                sections.get("achievements")
            ),
        }

    def _normalize_text(self, raw_text: str) -> str:
        """
        Normalize line endings and whitespace while preserving
        meaningful line structure.
        """
        text = raw_text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        normalized_lines = []

        for line in text.splitlines():
            line = re.sub(r"[ \t]+", " ", line).strip()
            normalized_lines.append(line)

        return "\n".join(normalized_lines)

    def _normalize_heading(self, line: str) -> str:
        """
        Normalize OCR/PDF heading decoration.

        Examples:

        # WORK FLOW
        ## WORK FLOW
        WORK FLOW:
        WORK FLOW -

        all become:

        work flow
        """
        cleaned = line.strip().lower()

        # Remove common Markdown-style heading decoration.
        cleaned = re.sub(r"^\s*#{1,6}\s*", "", cleaned)

        # Remove decorative bullets before headings.
        cleaned = re.sub(
            r"^[\-\*\u2022]+\s*",
            "",
            cleaned,
        )

        # Remove trailing heading punctuation.
        cleaned = re.sub(
            r"[:\-]+$",
            "",
            cleaned,
        )

        # Normalize whitespace.
        cleaned = re.sub(
            r"\s+",
            " ",
            cleaned,
        ).strip()

        return cleaned

    def _merge_wrapped_lines(
        self,
        lines: list[str],
    ) -> list[str]:
        """
        Merge lines that are clearly continuations of the previous
        line without merging into or across section headings.
        """
        merged: list[str] = []

        for line in lines:
            current_is_heading = (
                self._identify_section(line) is not None
                or self._is_non_stored_section(line)
            )

            if current_is_heading or not merged:
                merged.append(line)
                continue

            previous_is_heading = (
                self._identify_section(merged[-1]) is not None
                or self._is_non_stored_section(merged[-1])
            )

            if (
                not previous_is_heading
                and self._looks_like_continuation(
                    merged[-1],
                    line,
                )
            ):
                merged[-1] = f"{merged[-1]} {line}"
            else:
                merged.append(line)

        return merged

    def _extract_full_name(
        self,
        lines: list[str],
    ) -> str | None:
        """
        Extract the most likely candidate name.

        The OCR version of a resume may place the name later in the
        extracted text because of multi-column reading order, so this
        scans more than just the first few lines.

        Education headings, degree text, section headings, contact
        information and job titles are rejected.
        """
        ignored = {
            "resume",
            "curriculum vitae",
            "cv",
        }

        for aliases in self.SECTION_ALIASES.values():
            ignored.update(aliases)

        ignored.update(self.NON_STORED_SECTIONS)

        candidates: list[tuple[int, str]] = []

        # OCR can reorder columns, so inspect a reasonable portion of
        # the document rather than assuming the name is always first.
        for index, line in enumerate(lines):
            cleaned = line.strip()
            normalized = self._normalize_heading(cleaned)

            if not cleaned:
                continue

            if normalized in ignored:
                continue

            if self.EMAIL_PATTERN.search(cleaned):
                continue

            if self.LINKEDIN_PATTERN.search(cleaned):
                continue

            if self.GITHUB_PATTERN.search(cleaned):
                continue

            if self.PHONE_PATTERN.search(cleaned):
                continue

            if "|" in cleaned:
                continue

            if "," in cleaned:
                continue

            if any(char.isdigit() for char in cleaned):
                continue

            if len(cleaned) > 60:
                continue

            words = cleaned.split()

            if not 2 <= len(words) <= 4:
                continue

            # Normalize punctuation before keyword checking.
            word_tokens = [
                re.sub(
                    r"[^a-z]",
                    "",
                    word.lower(),
                )
                for word in words
            ]

            if any(
                token in self.DEGREE_KEYWORDS
                or token in self.JOB_TITLE_KEYWORDS
                for token in word_tokens
            ):
                continue

            # A person's name normally consists mostly of alphabetic
            # tokens. Reject obvious prose sentences.
            alpha_words = [
                word
                for word in word_tokens
                if word
            ]

            if len(alpha_words) < 2:
                continue

            # Prefer uppercase/title-case short candidates.
            score = 0

            if cleaned.isupper():
                score += 5

            if all(
                word[:1].isupper()
                for word in cleaned.split()
                if word
            ):
                score += 3

            # Names near contact information are strong candidates.
            nearby_start = max(0, index - 2)
            nearby_end = min(
                len(lines),
                index + 3,
            )

            nearby_text = " ".join(
                lines[nearby_start:nearby_end]
            )

            if self.EMAIL_PATTERN.search(nearby_text):
                score += 5

            if self.PHONE_PATTERN.search(nearby_text):
                score += 4

            candidates.append((score, cleaned))

        if not candidates:
            return None

        # Highest score wins. Python's max preserves the first item
        # when scores are equal, which is useful for normal resumes.
        candidates.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        return candidates[0][1]

    def _extract_email(
        self,
        text: str,
    ) -> str | None:
        """
        Extract the first email address.
        """
        match = self.EMAIL_PATTERN.search(text)

        if match is None:
            return None

        return match.group(0).strip()

    def _extract_phone(
        self,
        text: str,
    ) -> str | None:
        """
        Extract the most likely phone number.
        """
        matches = self.PHONE_PATTERN.findall(text)

        if not matches:
            return None

        for match in matches:
            phone = re.sub(
                r"\s+",
                " ",
                match,
            ).strip()

            digits = re.sub(
                r"\D",
                "",
                phone,
            )

            if 10 <= len(digits) <= 13:
                return phone

        return None

    def _extract_linkedin(
        self,
        text: str,
    ) -> str | None:
        """
        Extract and normalize a LinkedIn profile URL.
        """
        match = self.LINKEDIN_PATTERN.search(text)

        if match is None:
            return None

        url = match.group(0).strip()

        if not url.lower().startswith(
            ("http://", "https://")
        ):
            url = f"https://{url}"

        url = re.sub(
            r"^(https?://)www\.linkedin\.com",
            r"\1www.linkedin.com",
            url,
            flags=re.IGNORECASE,
        )

        url = re.sub(
            r"/IN/",
            "/in/",
            url,
            flags=re.IGNORECASE,
        )

        return url

    def _extract_github(
        self,
        text: str,
    ) -> str | None:
        """
        Extract and normalize a GitHub profile URL.
        """
        match = self.GITHUB_PATTERN.search(text)

        if match is None:
            return None

        url = match.group(0).strip()

        if not url.lower().startswith(
            ("http://", "https://")
        ):
            url = f"https://{url}"

        url = re.sub(
            r"^(https?://)www\.github\.com",
            r"\1www.github.com",
            url,
            flags=re.IGNORECASE,
        )

        return url

    def _extract_location(
        self,
        lines: list[str],
    ) -> str | None:
        """
        Extract location using prioritized strategies:

        1. Explicit Location:/Based in:/Address:
        2. Contact line containing phone/email + location
        3. Lines immediately surrounding contact information
        4. Pipe-delimited contact line
        5. Plain comma-separated location line near the header

        This avoids selecting an education location such as:

        Sri Muthukumaran Institute of Technology,
        Tamil Nadu, India

        when the actual contact location is:

        Chennai, india 600074
        """
        location = self._extract_location_with_prefix(lines)

        if location:
            return location

        location = self._extract_location_near_contact(lines)

        if location:
            return location

        location = self._extract_location_from_pipe_line(lines)

        if location:
            return location

        return self._extract_location_from_plain_line(lines)

    def _extract_location_with_prefix(
        self,
        lines: list[str],
    ) -> str | None:
        """
        Extract location from an explicit prefix.
        """
        for line in lines[:40]:
            match = self.LOCATION_PREFIX_PATTERN.match(
                line.strip()
            )

            if match is None:
                continue

            value = match.group(1).strip()

            if value:
                return value

        return None

    def _extract_location_near_contact(
        self,
        lines: list[str],
    ) -> str | None:
        """
        Find location near email/phone contact information.

        This is especially important for OCR resumes where columns
        may be reordered.
        """
        contact_indexes: list[int] = []

        for index, line in enumerate(lines):
            if (
                self.EMAIL_PATTERN.search(line)
                or self.PHONE_PATTERN.search(line)
                or self.LINKEDIN_PATTERN.search(line)
                or self.GITHUB_PATTERN.search(line)
            ):
                contact_indexes.append(index)

        for contact_index in contact_indexes:
            start = max(
                0,
                contact_index - 3,
            )
            end = min(
                len(lines),
                contact_index + 4,
            )

            for index in range(start, end):
                candidate = lines[index].strip()

                if self._is_location_candidate(
                    candidate,
                    lines,
                    index,
                ):
                    return candidate

        return None

    def _is_location_candidate(
        self,
        candidate: str,
        lines: list[str],
        index: int,
    ) -> bool:
        """
        Decide whether a line is likely a contact location.
        """
        if not candidate:
            return False

        if self.EMAIL_PATTERN.search(candidate):
            return False

        if self.LINKEDIN_PATTERN.search(candidate):
            return False

        if self.GITHUB_PATTERN.search(candidate):
            return False

        # A phone-only line is not a location. OCR may prefix it
        # with a decorative/contact symbol such as "@".
        contact_candidate = re.sub(
            r"^[\s@#•:]+",
            "",
            candidate.strip(),
        )

        if self.PHONE_PATTERN.fullmatch(contact_candidate):
            return False

        normalized = self._normalize_heading(candidate)

        if (
            self._identify_section(candidate) is not None
            or self._is_non_stored_section(candidate)
        ):
            return False

        # Education/institution lines should not win location
        # detection merely because they contain "Tamil Nadu, India".
        education_words = {
            "university",
            "institute",
            "college",
            "technology",
            "bachelor",
            "master",
            "btech",
            "mtech",
            "education",
            "graduation",
        }

        tokens = set(
            re.findall(
                r"[a-z]+",
                normalized.lower(),
            )
        )

        if tokens.intersection(education_words):
            return False

        # A location normally contains a recognized state/country
        # keyword or a city followed by a postal code.
        has_location_keyword = any(
            pattern.search(candidate)
            for pattern in self.LOCATION_KEYWORD_PATTERNS
        )

        has_postal_code = bool(
            re.search(
                r"\b\d{5,6}\b",
                candidate,
            )
        )

        has_comma = "," in candidate

        common_city_names = {
            "chennai",
            "bengaluru",
            "bangalore",
            "hyderabad",
            "mumbai",
            "delhi",
            "coimbatore",
            "madurai",
            "trichy",
            "tiruchirappalli",
            "salem",
            "pondicherry",
            "puducherry",
        }

        has_city_keyword = any(
            re.search(
                rf"\b{re.escape(city)}\b",
                normalized,
                re.IGNORECASE,
            )
            for city in common_city_names
        )

        # OCR contact lines may contain a leading symbol such as "@"
        # and a postal code without a state/country.
        if (has_location_keyword or has_city_keyword) and (
            has_comma or has_postal_code
        ):
            return True

        if has_postal_code and (
            candidate.lstrip().startswith(("@", "#"))
            or index < 15
        ):
            return True

        return False

    def _extract_location_from_pipe_line(
        self,
        lines: list[str],
    ) -> str | None:
        """
        Extract location from a pipe-delimited contact line.
        """
        for line in lines[:30]:
            if "|" not in line:
                continue

            parts = [
                part.strip()
                for part in line.split("|")
                if part.strip()
            ]

            for part in parts:
                if self.EMAIL_PATTERN.search(part):
                    continue

                if self.PHONE_PATTERN.search(part):
                    continue

                if self.LINKEDIN_PATTERN.search(part):
                    continue

                if self.GITHUB_PATTERN.search(part):
                    continue

                for pattern in self.LOCATION_KEYWORD_PATTERNS:
                    if pattern.search(part):
                        return part

        return None

    def _extract_location_from_plain_line(
        self,
        lines: list[str],
    ) -> str | None:
        """
        Extract a location from a plain comma-separated line.

        Avoid education/institution content.
        """
        for index, line in enumerate(lines[:30]):
            if "," not in line:
                continue

            if self._is_location_candidate(
                line,
                lines,
                index,
            ):
                return line.strip()

        return None

    def _extract_sections(
        self,
        lines: list[str],
        full_name: str | None = None,
    ) -> dict[str, str | None]:
        """
        Detect section headings and collect their contents until
        the next recognized section.

        Also stops on layout noise such as the candidate's name
        reappearing in another OCR column or a stray job title.
        """
        sections: dict[str, list[str]] = {}

        current_section: str | None = None

        normalized_name = (
            self._normalize_heading(full_name)
            if full_name
            else None
        )

        for line in lines:
            section_name = self._identify_section(line)

            if section_name is not None:
                current_section = section_name

                if current_section not in sections:
                    sections[current_section] = []

                continue

            if self._is_non_stored_section(line):
                current_section = None
                continue

            if current_section is not None:
                if (
                    normalized_name
                    and self._normalize_heading(line)
                    == normalized_name
                ):
                    current_section = None
                    continue

                if (
                    current_section != "experience"
                    and self._looks_like_stray_job_title(line)
                ):
                    current_section = None
                    continue

                sections[current_section].append(line)

        result: dict[str, str | None] = {}

        for section_name, section_lines in sections.items():
            cleaned_lines = [
                line.strip()
                for line in section_lines
                if line.strip()
            ]

            result[section_name] = (
                "\n".join(cleaned_lines)
                if cleaned_lines
                else None
            )

        return result

    def _looks_like_stray_job_title(
        self,
        line: str,
    ) -> bool:
        """
        Detect a short line that looks like a stray job title.
        """
        words = re.findall(
            r"[A-Za-z']+",
            line.lower(),
        )

        if not words or len(words) > 4:
            return False

        return any(
            word in self.JOB_TITLE_KEYWORDS
            for word in words
        )

    def _identify_section(
        self,
        line: str,
    ) -> str | None:
        """
        Match a line against known section headings after
        normalizing OCR heading decoration.
        """
        cleaned = self._normalize_heading(line)

        for section_name, aliases in self.SECTION_ALIASES.items():
            if cleaned in aliases:
                return section_name

        return None

    def _is_non_stored_section(
        self,
        line: str,
    ) -> bool:
        """
        Detect valid resume sections that currently have no
        dedicated ResumeVersion field.
        """
        cleaned = self._normalize_heading(line)

        return cleaned in self.NON_STORED_SECTIONS

    def _extract_skills(
        self,
        section_text: str | None,
    ) -> list[str] | None:
        """
        Extract skills while joining PDF/OCR-wrapped lines.
        """
        if not section_text:
            return None

        text = re.sub(
            r"\bGoogle\s*\n\s*Gemini\b",
            "Google Gemini",
            section_text,
            flags=re.IGNORECASE,
        )

        text = text.replace(
            "â€¢",
            "\n",
        )

        text = text.replace(
            "|",
            "\n",
        )

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        merged_lines: list[str] = []

        for line in lines:
            if (
                merged_lines
                and self._looks_like_continuation(
                    merged_lines[-1],
                    line,
                )
            ):
                merged_lines[-1] = (
                    f"{merged_lines[-1]} {line}"
                )
            else:
                merged_lines.append(line)

        skills: list[str] = []

        for line in merged_lines:
            parts = re.split(
                r",\s*",
                line,
            )

            for part in parts:
                value = part.strip()

                value = re.sub(
                    r"^[\-\*\u2022]+\s*",
                    "",
                    value,
                )

                if value and value not in skills:
                    skills.append(value)

        return skills or None

    def _looks_like_continuation(
        self,
        previous: str,
        current: str,
    ) -> bool:
        """
        Detect common PDF/OCR line wrapping.
        """
        if previous.endswith(
            ("&", "-", "/", "and")
        ):
            return True

        if current and current[0].islower():
            return True

        if previous.lower() in {
            "google",
            "data structures",
            "machine",
            "artificial",
        }:
            return True

        return False

    def _extract_list_section(
        self,
        section_text: str | None,
    ) -> list[str] | None:
        """
        Preserve section content as meaningful lines.
        """
        if not section_text:
            return None

        values: list[str] = []

        for line in section_text.splitlines():
            value = line.strip()

            if not value:
                continue

            value = re.sub(
                r"^[\-\*\u2022]+\s*",
                "",
                value,
            )

            if value:
                values.append(value)

        return values or None

    def _empty_result(self) -> dict:
        """
        Return the complete structured result for empty input.
        """
        return {
            "full_name": None,
            "email": None,
            "phone": None,
            "location": None,
            "linkedin_url": None,
            "github_url": None,
            "summary": None,
            "skills": None,
            "experience": None,
            "education": None,
            "projects": None,
            "certifications": None,
            "achievements": None,
        }