# Run one task against the lineup, wait, and download.
#
#   .\scripts\run_lineup.ps1 world-clock-from-memory
#   .\scripts\run_lineup.ps1 world-clock-with-tzdata-tool
#
# The lineup mixes current frontier models with deliberately older ones (mid-2025), so the
# dating ladder has known-old clocks to prove itself on. gemini-3.7-flash is left out here
# because the push already ran it as the task's creation run.

param(
    [Parameter(Mandatory = $true)][string]$Task,
    [int]$WaitSeconds = 5400
)

$proj = Split-Path -Parent $PSScriptRoot
$kaggle = Join-Path $proj ".venv\Scripts\kaggle.exe"

$lineup = @(
    # Google
    "gemini-3.8-flash",
    "gemini-3.1-pro-preview",
    "gemini-2.5-pro",
    "gemini-3.5-flash-lite",
    # Anthropic
    "claude-opus-5-default",
    "claude-sonnet-5-default",
    "claude-haiku-4-5-20251001",
    "claude-opus-4-1-20250805",
    # OpenAI
    "gpt-6-astra",
    "gpt-5.6-terra",
    "gpt-5.5-2026-04-23",
    "gpt-5.4-mini-2026-03-17",
    "gpt-oss-120b",
    # xAI
    "grok-4.6",
    "grok-4.20-0309-reasoning",
    # others
    "deepseek-r1-0528",
    "glm-5",
    "qwen3-next-80b-a3b-thinking",
    "gemma-4-31b-it"
)

$args = @("benchmarks", "tasks", "run", $Task)
foreach ($m in $lineup) { $args += @("-m", $m) }
$args += @("--wait", "$WaitSeconds")

Write-Output "Running $Task on $($lineup.Count) models"
& $kaggle @args

Write-Output "Downloading"
& $kaggle benchmarks tasks download $Task -o (Join-Path $proj "results\raw")
& $kaggle benchmarks tasks status $Task
