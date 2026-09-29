# Unattended: push both tasks, then run every model one at a time, then download.
#
#   powershell -File scripts\run_all.ps1            # push + run everything
#   powershell -File scripts\run_all.ps1 -NoPush    # runs only
#
# One model at a time, because the Model Proxy reserves quota per in-flight request and
# the account's daily allowance is small: 19 parallel runs drained it on 2026-09-27 and
# every later request was refused. Sequential runs finish in a few minutes each.
#
# Models are chosen so the dating ladder has known-old clocks (mid-2025) beside current
# ones. Slugs the proxy returns 404 for (claude-opus-4-1, grok-4.6, grok-4.5-0708) are
# left out. DeepSeek-R1 cannot call tools ("Tool calling is not supported by this
# model"), so it is skipped in the tool condition and reported as such.

param(
    [switch]$NoPush,
    [int]$WaitSeconds = 5400
)

$proj = Split-Path -Parent $PSScriptRoot
$kaggle = Join-Path $proj ".venv\Scripts\kaggle.exe"
$logDir = Join-Path $proj "results\raw\logs"
New-Item -ItemType Directory -Force $logDir | Out-Null
$log = Join-Path $logDir "run_all.log"

function Log($text) {
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  $text"
    Write-Output $line
    Add-Content -Path $log -Value $line
}

$memoryModels = @(
    "gpt-6-astra",
    "gpt-5.6-terra",
    "gpt-5.5-2026-04-23",
    "gpt-5.4-mini-2026-03-17",
    "claude-opus-4-5-20251101",
    "grok-4.20-0309-reasoning",
    "grok-4.20-0309-non-reasoning",
    "deepseek-r1-0528",
    "glm-5",
    "qwen3-next-80b-a3b-thinking",
    "gpt-oss-120b",
    "gemma-4-31b-it"
)

$toolModels = @(
    "gemini-3.8-flash",
    "gemini-3.1-pro-preview",
    "gemini-2.5-pro",
    "gemini-3.5-flash-lite",
    "claude-opus-5-default",
    "claude-sonnet-5-default",
    "claude-haiku-4-5-20251001",
    "claude-opus-4-5-20251101",
    "gpt-6-astra",
    "gpt-5.6-terra",
    "gpt-5.5-2026-04-23",
    "gpt-5.4-mini-2026-03-17",
    "grok-4.20-0309-reasoning",
    "grok-4.20-0309-non-reasoning",
    "glm-5",
    "qwen3-next-80b-a3b-thinking",
    "gpt-oss-120b",
    "gemma-4-31b-it"
)

# Models that already have a Completed run on the task's current version are skipped, so a
# restart after an interruption only runs what is missing. `status` reports the latest
# version's runs, one row per model.
function Get-DoneModels($task) {
    $done = @()
    $rows = & $kaggle benchmarks tasks status $task 2>&1
    foreach ($row in $rows) {
        if ("$row" -match '^(\S+)\s+Completed\s') { $done += $matches[1] }
    }
    return $done
}

Push-Location $proj
try {
    if (-not $NoPush) {
        Log "push world-clock-from-memory"
        & $kaggle benchmarks tasks push world-clock-from-memory -f tasks/world_clock_memory.py --wait 1800 2>&1 | ForEach-Object { Log "  $_" }
        Log "push world-clock-tool-v2"
        & $kaggle benchmarks tasks push world-clock-tool-v2 -f tasks/world_clock_tool.py --wait 1800 2>&1 | ForEach-Object { Log "  $_" }
    }

    $doneMemory = Get-DoneModels "world-clock-from-memory"
    foreach ($m in $memoryModels) {
        if ($doneMemory -contains $m) { Log "skip world-clock-from-memory on $m (already completed)"; continue }
        Log "run world-clock-from-memory on $m"
        & $kaggle benchmarks tasks run world-clock-from-memory -m $m --wait $WaitSeconds 2>&1 | ForEach-Object { Log "  $_" }
    }
    Log "download world-clock-from-memory"
    & $kaggle benchmarks tasks download world-clock-from-memory -o (Join-Path $proj "results\raw") 2>&1 | ForEach-Object { Log "  $_" }

    $doneTool = Get-DoneModels "world-clock-tool-v2"
    foreach ($m in $toolModels) {
        if ($doneTool -contains $m) { Log "skip world-clock-tool-v2 on $m (already completed)"; continue }
        Log "run world-clock-tool-v2 on $m"
        & $kaggle benchmarks tasks run world-clock-tool-v2 -m $m --wait $WaitSeconds 2>&1 | ForEach-Object { Log "  $_" }
    }
    Log "download world-clock-tool-v2"
    & $kaggle benchmarks tasks download world-clock-tool-v2 -o (Join-Path $proj "results\raw") 2>&1 | ForEach-Object { Log "  $_" }
    Log "done"
}
finally {
    Pop-Location
}
