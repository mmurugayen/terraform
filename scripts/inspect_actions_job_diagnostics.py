#!/usr/bin/env python3
"""Read-only triage for GitHub Actions jobs that fail without step diagnostics.

Uses the GitHub REST API. Never downloads logs, modifies workflow runs, or prints
the token. Exit code 2 indicates that one or more API responses were unavailable.
"""
import argparse
import json
import logging
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

TARGETS = (
    ("terraform", 114799205150),
    ("terraformautomation", 114799176936),
    ("test-project", 114799166102),
    ("testrepo", 114799179543),
)
API = "https://api.github.com/repos/mmurugayen/{repo}/actions/jobs/{job_id}"


def inspect_job(repo, job_id, token="", opener=urlopen):
    if not repo or not repo.replace("-", "").replace("_", "").isalnum():
        raise ValueError("invalid repository")
    if type(job_id) is not int or job_id <= 0:
        raise ValueError("invalid job id")
    headers = {"Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": "2022-11-28",
               "User-Agent": "gysam-ci-diagnostics/1"}
    if token:
        headers["Authorization"] = "Bearer " + token
    request = Request(API.format(repo=repo, job_id=job_id), headers=headers)
    with opener(request, timeout=15) as response:
        raw = response.read(65537)
    if len(raw) > 65536:
        raise ValueError("job_metadata_limit_exceeded")
    job = json.loads(raw)
    if not isinstance(job, dict):
        raise ValueError("invalid_job_metadata")
    steps = job.get("steps")
    if not isinstance(steps, list):
        steps = []
    logger.info("Inspected Actions job metadata for %s job %d", repo, job_id)
    return {
        "repository": repo,
        "job_id": job_id,
        "name": job.get("name"),
        "status": job.get("status"),
        "conclusion": job.get("conclusion"),
        "runner_name": job.get("runner_name"),
        "runner_group_name": job.get("runner_group_name"),
        "started_at": job.get("started_at"),
        "completed_at": job.get("completed_at"),
        "steps_reported": len(steps),
        "steps": [{"name": s.get("name"), "status": s.get("status"),
                   "conclusion": s.get("conclusion")} for s in steps],
        "diagnostic": ("missing_job_steps" if not steps else "steps_available"),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", help="Single repository (default: all four issue #20 repositories)")
    parser.add_argument("--job-id", type=int, help="Job ID; required with --repo")
    args = parser.parse_args(argv)
    if bool(args.repo) != (args.job_id is not None):
        parser.error("--repo and --job-id must be provided together")
    targets = [(args.repo, args.job_id)] if args.repo else TARGETS
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN", "")
    results = []
    failed = False
    for repo, job_id in targets:
        try:
            results.append(inspect_job(repo, job_id, token))
        except (HTTPError, URLError, OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
            failed = True
            results.append({"repository": repo, "job_id": job_id,
                            "diagnostic": "api_unavailable",
                            "error_type": type(exc).__name__})
    logger.info("Actions job diagnostic batch finished: %d jobs, api_failures=%s", len(results), failed)
    print(json.dumps({"schema_version": 1, "read_only": True, "jobs": results}, indent=2))
    return 2 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
