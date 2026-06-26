#!/usr/bin/env bash
# grade-foundry.sh — house-standard linter for Foundry (and any) skills.
# Checks: SKILL.md exists · frontmatter name+description · router <=150 lines
# (target <100) · MCP-never · referenced sub-docs resolve · connection contract
# (4 headings) when the skill looks like an auth/connection skill.
#
#   bash scripts/grade-foundry.sh skills/foundry/*
#
set -uo pipefail
fail=0; n=0; sumlines=0; maxlines=0; over150=0
if [ -t 1 ]; then G=$'\033[32m'; R=$'\033[31m'; Y=$'\033[33m'; D=$'\033[2m'; X=$'\033[0m'; else G=""; R=""; Y=""; D=""; X=""; fi
ok(){ printf "  ${G}✓${X} %s\n" "$1"; }
no(){ printf "  ${R}✗ %s${X}\n" "$1"; fail=$((fail+1)); }
warn(){ printf "  ${Y}! %s${X}\n" "$1"; }

for dir in "$@"; do
  [ -d "$dir" ] || continue
  name="$(basename "$dir")"; md="$dir/SKILL.md"
  printf "${D}— %s${X}\n" "$name"
  if [ ! -f "$md" ]; then no "no SKILL.md"; continue; fi
  n=$((n+1))

  # frontmatter
  head -1 "$md" | grep -q '^---' || no "missing frontmatter open"
  grep -qE '^name:[[:space:]]*' "$md"        || no "frontmatter missing name:"
  grep -qE '^description:[[:space:]]*' "$md"  || no "frontmatter missing description:"

  # router size
  lines=$(grep -c '' "$md")
  sumlines=$((sumlines+lines)); [ "$lines" -gt "$maxlines" ] && maxlines=$lines
  if [ "$lines" -gt 150 ]; then no "router $lines lines (> 150 hard cap)"; over150=$((over150+1));
  elif [ "$lines" -gt 100 ]; then warn "router $lines lines (> 100 target)";
  else ok "router $lines lines"; fi

  # MCP-never: flag any 'mcp' that is not an explicit negation/disclaimer
  if grep -i 'mcp' "$md" | grep -ivqE 'no mcp|without mcp|not an mcp|optional convenience|no .* mcp|mcp[- ]never|never depend'; then
    no "MCP referenced without negation (CLI-first/MCP-never)"
  else ok "MCP-never"; fi

  # referenced sub-docs resolve
  missing=0
  for ref in $(grep -oE 'references/[A-Za-z0-9._/-]+\.md' "$md" | sort -u); do
    [ -f "$dir/$ref" ] || { no "broken ref: $ref"; missing=1; }
  done
  [ "$missing" = 0 ] && ok "references resolve"

  # connection contract — only enforce for config/connection-type skills
  # only genuine connection/config skills (not e.g. "authoring")
  if echo "$name" | grep -qiE 'config$|connection|-connect$'; then
    for h in 'Interactive' 'Service principal' 'Verify' 'Troubleshoot'; do
      grep -qiE "^#{1,4}[[:space:]]+$h" "$md" || no "connection contract missing heading: $h"
    done
  fi
done

echo
if [ "$n" -gt 0 ]; then
  avg=$(awk "BEGIN{printf \"%.1f\", $sumlines/$n}")
  printf "Skills: %s · avg router %s lines · max %s · over-150 %s\n" "$n" "$avg" "$maxlines" "$over150"
fi
if [ "$fail" -gt 0 ]; then printf "${R}FAIL: %s issue(s)${X}\n" "$fail"; exit 1; fi
printf "${G}PASS${X}\n"; exit 0
