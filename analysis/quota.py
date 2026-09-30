"""Print the account's Kaggle model-proxy quota.

Usage:
    python analysis/quota.py

The CLI has no command for this, but the SDK it is built on has the call. Run it before
launching a lineup; analysis/run_costs.py says what each run is likely to cost.
"""

from __future__ import annotations

import sys

from kaggle.api.kaggle_api_extended import KaggleApi
from kagglesdk.benchmarks.types.benchmark_tasks_api_service import ApiGetBenchmarkTaskQuotaRequest


def main() -> int:
    api = KaggleApi()
    api.authenticate()
    with api.build_kaggle_client() as kaggle:
        resp = kaggle.benchmarks.benchmark_tasks_api_client.get_benchmark_task_quota(ApiGetBenchmarkTaskQuotaRequest())
    used, allowed = resp.daily_quota_used, resp.total_daily_quota_allowed
    print(f"daily quota: ${used:.4f} used of ${allowed:.2f} (${allowed - used:.4f} left)")
    extra = {k: v for k, v in vars(resp).items() if k not in ("_daily_quota_used", "_total_daily_quota_allowed", "_freeze")}
    if extra:
        print(f"other fields: {extra}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
