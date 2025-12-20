# Implementation Details: Social RV Comparative Judging

## Overview

This repository now uses the **exact TypeScript implementation** from Social RV's production system, ensuring 100% identical logic for research validation.

## Architecture

### Two-Part System

1. **Python Layer** (`src/comparative_judging/`)

   - API client for fetching sessions from Social RV
   - Wrapper functions that call the TypeScript implementation
   - Utility functions for data preparation

2. **TypeScript Layer** (`nodejs_wrapper/`)
   - Exact copy of `comparative-judging.server.ts` from Social RV
   - CLI wrapper that accepts JSON via stdin
   - Returns results as JSON to stdout

### Why This Approach?

We chose to invoke the TypeScript code directly rather than rewriting it in Python because:

1. **Guaranteed Identical Logic**: No risk of translation errors
2. **Easy to Update**: Just copy the file when Social RV updates
3. **Single Source of Truth**: The TypeScript file is the authoritative implementation
4. **Validation**: Researchers can verify they're using the same code as production

## How It Works

### Data Flow

```
Python Code
    ↓
create SessionFile/Target objects with URLs
    ↓
perform_comparative_judging()
    ↓
Convert to JSON
    ↓
subprocess: npx tsx cli.ts < input.json
    ↓
TypeScript: performComparativeJudging()
    ↓
Multi-pass elimination algorithm
    ↓
Return JSON result
    ↓
Python: parse and return ComparativeJudgingResult
```

### Multi-Pass Elimination Algorithm

The algorithm (from Social RV) works as follows:

#### Initial Setup

- Combine 1 correct target + 9 decoys = 10 total targets
- Shuffle all targets randomly
- Initialize empty results array

#### Pass 1: 10 → Top 3

- Show AI all 10 targets
- AI selects top 3 matches (ranks 1-3)
- If correct target found → **STOP** and return results
- Otherwise, remove selected 3 from pool

#### Pass 2: 7 → Top 3

- Show AI remaining 7 targets
- AI selects top 3 matches (ranks 4-6)
- If correct target found → **STOP** and return results
- Otherwise, remove selected 3 from pool

#### Pass 3: 4 → Top 3

- Show AI remaining 4 targets
- AI selects top 3 matches (ranks 7-9)
- If correct target found → **STOP** and return results
- Otherwise, 1 target remains

#### Final: Rank 10

- Last remaining target automatically gets rank 10

### Key Features

1. **Early Stopping**: System stops as soon as correct target is found
2. **Efficiency**: Avoids ranking all 10 targets if not necessary
3. **Randomization**: Targets shuffled before each run
4. **Structured Output**: Uses OpenAI's JSON schema for reliable parsing

## File Mapping

### From Social RV → Comparative Judging

| Social RV                                       | Comparative Judging                            | Purpose                     |
| ----------------------------------------------- | ---------------------------------------------- | --------------------------- |
| `app/services/ai/comparative-judging.server.ts` | `nodejs_wrapper/comparative-judging.server.ts` | Core judging logic          |
| `app/services/ai/types.ts`                      | `nodejs_wrapper/types.ts`                      | TypeScript types            |
| `app/utils/comparative-analysis.server.ts`      | `src/comparative_judging/judging.py`           | Data preparation & DB logic |

### New Files Created

| File                                 | Purpose                                    |
| ------------------------------------ | ------------------------------------------ |
| `nodejs_wrapper/cli.ts`              | Command-line interface for TypeScript code |
| `nodejs_wrapper/package.json`        | Node.js dependencies                       |
| `src/comparative_judging/judging.py` | Python wrapper for TypeScript              |
| `test_wrapper.py`                    | Test script to verify setup                |

## Key Differences from Social RV

### What's the Same

- ✅ Multi-pass elimination algorithm
- ✅ Early stopping logic
- ✅ Target shuffling
- ✅ OpenAI API calls and prompts
- ✅ JSON schema for structured output

### What's Different

- ❌ No direct database access (uses API instead)
- ❌ No automatic decoy selection (must be provided)
- ❌ No result storage (returns results only)
- ❌ Subprocess overhead (Python → Node.js)

## Data Structures

### Python → TypeScript

```python
# Python input
SessionFile(url="...", mime_type="...", file_name="...")
Target(id="...", description="...", url="...")

# Converted to JSON
{
  "sessionFiles": [{"url": "...", "mimeType": "...", "fileName": "..."}],
  "currentTarget": {"id": "...", "description": "...", "url": "..."},
  "historicalTargets": [{"id": "...", "description": "...", "url": "..."}, ...]
}
```

### TypeScript → Python

```typescript
// TypeScript output
{
  overallReasoning: string,
  topMatches: [{rank: number, targetId: string, reasoning: string}],
  correctTargetRank?: number,
  totalTargetsRanked: number
}

// Converted to Python
ComparativeJudgingResult(
    overall_reasoning="...",
    top_matches=[RankedMatch(rank=1, target_id="...", reasoning="...")],
    correct_target_rank=1,
    total_targets_ranked=3
)
```

## Updating from Social RV

To sync with Social RV's latest code:

```bash
# 1. Copy the TypeScript file
cp /path/to/social-rv/app/services/ai/comparative-judging.server.ts \
   nodejs_wrapper/comparative-judging.server.ts

# 2. Check for new dependencies
diff /path/to/social-rv/package.json nodejs_wrapper/package.json

# 3. Update types if needed
cp /path/to/social-rv/app/services/ai/types.ts \
   nodejs_wrapper/types.ts

# 4. Test the wrapper
python test_wrapper.py
```

## Performance Considerations

### API Calls

- **Minimum**: 1 call (if correct target in top 3)
- **Maximum**: 3 calls (if correct target is rank 10)
- **Average**: ~2 calls (based on random distribution)

### Cost Estimate (GPT-4o)

- ~$0.02-0.06 per session (depending on image sizes and number of passes)
- Bulk processing: Consider rate limits and batching

### Execution Time

- **Per Pass**: 10-30 seconds (depends on image sizes and API latency)
- **Total**: 30-90 seconds for full session

## Validation

### How to Verify Correctness

1. **Run on Known Sessions**: Use sessions that already have ranks in Social RV
2. **Compare Results**: Results should be similar but may differ due to:
   - Random shuffling
   - AI non-determinism
   - Different decoys
3. **Check Logic**: The algorithm steps should match exactly
4. **Statistical Analysis**: Over many runs, distributions should match

### Expected Differences

Even with identical code, results will vary because:

- **Shuffling**: Targets are randomized before each run
- **Temperature**: GPT-4o has inherent randomness (even at temperature=0.1)
- **Timing**: API responses may vary slightly
- **Decoys**: If using different decoys than the original session

### What Should Match

- ✅ Algorithm steps (3 passes + final)
- ✅ Early stopping behavior
- ✅ Rank distribution over many runs
- ✅ Overall reasoning quality
- ✅ JSON output structure

## Troubleshooting

### Common Issues

1. **"Node.js wrapper not found"**

   - Run: `cd nodejs_wrapper && npm install`

2. **"tsx: command not found"**

   - Install tsx: `npm install -g tsx`
   - Or use npx: `npx tsx cli.ts`

3. **"OpenAI API key not set"**

   - Add to `.env`: `OPENAI_API_KEY=your_key_here`

4. **"Failed to parse Node.js output"**

   - Check Node.js version (need 18+)
   - Check for console.log statements in TypeScript (should only output JSON)

5. **Different results than Social RV**
   - This is expected! See "Expected Differences" above
   - Verify the algorithm steps match, not the exact ranks

## Future Improvements

### Potential Enhancements

- [ ] Batch processing support
- [ ] Caching of target images
- [ ] Progress callbacks for long-running operations
- [ ] Parallel session processing
- [ ] Result comparison tools

### Not Recommended

- ❌ Rewriting in pure Python (defeats the purpose)
- ❌ Modifying the algorithm (should match Social RV exactly)
- ❌ Removing early stopping (core feature)

## Questions?

If you have questions about this implementation:

1. Check the Social RV codebase for the original implementation
2. Review the TypeScript file: `nodejs_wrapper/comparative-judging.server.ts`
3. Run the test script: `python test_wrapper.py`
4. Open an issue in this repository
