# Node.js Wrapper for Social RV Comparative Judging

This directory contains the exact TypeScript implementation of comparative judging from Social RV's production system.

## Purpose

This wrapper allows Python code to invoke the actual TypeScript logic used in Social RV, ensuring 100% identical behavior for research validation.

## Setup

Install dependencies:

```bash
npm install
```

## How It Works

The wrapper consists of:

1. **`comparative-judging.server.ts`** - Exact copy from Social RV's codebase
2. **`cli.ts`** - Command-line interface that accepts JSON input via stdin
3. **`types.ts`** - Type definitions needed by the comparative judging code

## Usage

The Python code in `src/comparative_judging/judging.py` calls this wrapper automatically.

You can also test it manually:

```bash
echo '{"sessionFiles": [...], "currentTarget": {...}, "historicalTargets": [...]}' | npx tsx cli.ts
```

## Environment Variables

Required:
- `OPENAI_API_KEY` - Your OpenAI API key

## Multi-Pass Elimination Algorithm

The implementation uses a 3-pass elimination system:

1. **Pass 1**: 10 targets → select top 3 (ranks 1-3)
2. **Pass 2**: Remaining 7 → select top 3 (ranks 4-6)
3. **Pass 3**: Remaining 4 → select top 3 (ranks 7-9)
4. **Final**: Last remaining target gets rank 10

The system stops early if the correct target is found in any pass.

## Keeping in Sync

To update this wrapper with changes from Social RV:

```bash
cp /path/to/social-rv/app/services/ai/comparative-judging.server.ts ./comparative-judging.server.ts
```

