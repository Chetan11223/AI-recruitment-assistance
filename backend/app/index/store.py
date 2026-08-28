import json
import os
from typing import Dict, List, Optional
from app.config import INDEX_STORE_DIR, JOBS_DIR
from app.index.schema import CandidateProfile, JobDescription, CandidateScorecard, RankingResult

class IndexStore:
    def __init__(self):
        self.candidates: Dict[str, CandidateProfile] = {}
        self.jobs: Dict[str, JobDescription] = {}
        self.scorecards: Dict[str, CandidateScorecard] = {}  # key: f"{candidate_id}_{job_id}"
        self.rankings: Dict[str, RankingResult] = {}  # key: job_id
        self._load_from_disk()

    def add_candidate(self, candidate: CandidateProfile) -> None:
        self.candidates[candidate.candidate_id] = candidate
        self._persist_candidate(candidate)

    def get_candidate(self, candidate_id: str) -> Optional[CandidateProfile]:
        return self.candidates.get(candidate_id)

    def list_candidates(self) -> List[CandidateProfile]:
        return list(self.candidates.values())

    def delete_candidate(self, candidate_id: str) -> bool:
        if candidate_id in self.candidates:
            del self.candidates[candidate_id]
            try:
                file_path = INDEX_STORE_DIR / f"{candidate_id}.json"
                if file_path.exists():
                    file_path.unlink()
            except Exception:
                pass
            return True
        return False

    def add_job(self, job: JobDescription) -> None:
        self.jobs[job.job_id] = job
        self._persist_job(job)

    def get_job(self, job_id: str) -> Optional[JobDescription]:
        return self.jobs.get(job_id)

    def list_jobs(self) -> List[JobDescription]:
        return list(self.jobs.values())

    def delete_job(self, job_id: str) -> bool:
        if job_id in self.jobs:
            del self.jobs[job_id]
            try:
                file_path = JOBS_DIR / f"{job_id}.json"
                if file_path.exists():
                    file_path.unlink()
            except Exception:
                pass
            return True
        return False

    def save_scorecard(self, scorecard: CandidateScorecard) -> None:
        key = f"{scorecard.candidate_id}_{scorecard.job_id}"
        self.scorecards[key] = scorecard

    def get_scorecard(self, candidate_id: str, job_id: str) -> Optional[CandidateScorecard]:
        return self.scorecards.get(f"{candidate_id}_{job_id}")

    def save_ranking(self, ranking: RankingResult) -> None:
        self.rankings[ranking.job_id] = ranking

    def get_ranking(self, job_id: str) -> Optional[RankingResult]:
        return self.rankings.get(job_id)

    def _persist_candidate(self, candidate: CandidateProfile) -> None:
        try:
            file_path = INDEX_STORE_DIR / f"{candidate.candidate_id}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(candidate.model_dump_json(indent=2))
        except Exception as e:
            print(f"Non-fatal persistence error for candidate {candidate.candidate_id}: {e}")

    def _persist_job(self, job: JobDescription) -> None:
        try:
            file_path = JOBS_DIR / f"{job.job_id}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(job.model_dump_json(indent=2))
        except Exception as e:
            print(f"Non-fatal persistence error for job {job.job_id}: {e}")

    def _load_from_disk(self) -> None:
        try:
            if INDEX_STORE_DIR.exists():
                for file in INDEX_STORE_DIR.glob("*.json"):
                    try:
                        with open(file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            cand = CandidateProfile.model_validate(data)
                            self.candidates[cand.candidate_id] = cand
                    except Exception as e:
                        print(f"Error loading candidate from {file}: {e}")

            if JOBS_DIR.exists():
                for file in JOBS_DIR.glob("*.json"):
                    try:
                        with open(file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            job = JobDescription.model_validate(data)
                            self.jobs[job.job_id] = job
                    except Exception as e:
                        print(f"Error loading job from {file}: {e}")
        except Exception as e:
            print(f"Error in _load_from_disk: {e}")

store = IndexStore()
