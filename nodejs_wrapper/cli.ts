#!/usr/bin/env node
/**
 * CLI wrapper for Social RV's comparative judging logic
 * 
 * This script allows Python to invoke the exact TypeScript implementation
 * used in Social RV, ensuring 100% identical logic.
 * 
 * Input: JSON via stdin with structure:
 * {
 *   "sessionFiles": [{"url": string, "mimeType": string, "fileName": string}],
 *   "currentTarget": {"url": string, "description": string, "id": string},
 *   "historicalTargets": [{"url": string, "description": string, "id": string}]
 * }
 * 
 * Output: JSON to stdout with judging results
 */

import { performComparativeJudging } from './comparative-judging.server.js';
import type { ComparativeJudgingParams, ComparativeJudgingResult } from './comparative-judging.server.js';

async function main() {
  try {
    // Read JSON input from stdin
    const input = await readStdin();
    const params: ComparativeJudgingParams = JSON.parse(input);

    // Perform comparative judging
    const result: ComparativeJudgingResult = await performComparativeJudging(params);

    // Output result as JSON
    console.log(JSON.stringify(result, null, 2));
    process.exit(0);
  } catch (error) {
    // Output error as JSON to stderr
    const errorOutput = {
      error: true,
      message: error instanceof Error ? error.message : 'Unknown error',
      code: (error as any)?.code || 'UNKNOWN',
      details: (error as any)?.details,
    };
    console.error(JSON.stringify(errorOutput, null, 2));
    process.exit(1);
  }
}

function readStdin(): Promise<string> {
  return new Promise((resolve) => {
    let data = '';
    process.stdin.on('data', (chunk) => {
      data += chunk;
    });
    process.stdin.on('end', () => {
      resolve(data);
    });
  });
}

main();

