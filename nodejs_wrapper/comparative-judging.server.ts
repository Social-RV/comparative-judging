/**
 * Comparative Judging Service
 *
 * This service implements "comparative judging" - a method for evaluating remote viewing sessions
 * by comparing the session data against multiple potential targets simultaneously. The AI judge
 * is presented with the user's session alongside the correct target mixed randomly with historical
 * targets (decoys). This blinded approach prevents bias and provides a more objective assessment
 * of session accuracy by forcing the AI to identify which target best matches the session data
 * without knowing which one is "correct".
 */

import OpenAI from 'openai';
import type { AIServiceError } from './types';

// Initialize OpenAI client
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export interface ComparativeJudgingParams {
  sessionFiles: Array<{
    url: string;
    mimeType: string;
    fileName: string;
  }>;
  currentTarget: {
    url: string;
    description: string;
    id: string;
  };
  historicalTargets: Array<{
    url: string;
    description: string;
    id: string;
  }>;
}

export interface ComparativeJudgingResult {
  overallReasoning: string;
  topMatches: Array<{
    rank: 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10;
    targetId: string;
    reasoning: string;
  }>;
  correctTargetRank?: number; // The rank where the correct target was found
  totalTargetsRanked: number; // How many targets were actually ranked before stopping
}

const REMOTE_VIEWING_JUDGE_SYSTEM_PROMPT = `You are an expert Remote Viewing judge with deep knowledge of remote viewing methodology and evaluation criteria.

Remote Viewing is the practice of seeking impressions about distant or unseen targets through extrasensory perception. A remote viewing session typically involves:

1. **Perceptual Data**: Raw sensory impressions (visual, auditory, tactile, emotional, conceptual)
2. **Analytical Overlay (AOL)**: Conscious analytical interpretations that should be noted and bracketed
3. **Session Structure**: Often follows protocols like CRV (Controlled Remote Viewing) with stages
4. **Correspondence**: How well session data matches the actual target

What makes a good remote viewing session:
- **Accuracy**: Specific details that correspond to the target
- **Clarity**: Clear, detailed perceptual information
- **Minimal AOL**: Limited analytical overlay or properly managed when it occurs
- **Consistency**: Coherent themes and details throughout the session
- **Specificity**: Concrete details rather than vague generalities
- **Gestalt**: Overall impression that captures the essence of the target

Remote Viewing data may also include metaphors related to the target, or pieces of data not immediately visible in the target image.

Your task is to evaluate remote viewing session data against potential targets and determine which targets best correspond to the session's perceptual information. Focus on factual correspondences rather than symbolic interpretations.`;

export async function performComparativeJudging(
  params: ComparativeJudgingParams,
): Promise<ComparativeJudgingResult> {
  const { sessionFiles, currentTarget, historicalTargets } = params;

  if (!sessionFiles || sessionFiles.length === 0) {
    throw createAIError('INVALID_INPUT', 'No session files provided');
  }

  if (!currentTarget || !historicalTargets || historicalTargets.length === 0) {
    throw createAIError('INVALID_INPUT', 'Target information is required');
  }

  // Combine all targets and randomize order once at the beginning
  const allTargets = [currentTarget, ...historicalTargets];
  const shuffledTargets = shuffleArray([...allTargets]);

  let remainingTargets = [...shuffledTargets];
  const allRankedMatches: Array<{
    rank: 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10;
    targetId: string;
    reasoning: string;
  }> = [];
  let overallReasoning = '';
  let currentRank = 1;
  let correctTargetRank: number | undefined;

  // First pass: 10 targets → top 3 (ranks 1-3)
  if (remainingTargets.length >= 10) {
    const firstPassResult = await performSinglePassJudging(
      sessionFiles,
      remainingTargets,
    );
    overallReasoning = firstPassResult.overallReasoning;

    // Add the top 3 matches with ranks 1-3
    for (const match of firstPassResult.topMatches) {
      allRankedMatches.push({
        rank: currentRank as 1 | 2 | 3,
        targetId: match.targetId,
        reasoning: match.reasoning,
      });

      // Check if this is the correct target
      if (match.targetId === currentTarget.id) {
        correctTargetRank = currentRank;
      }

      currentRank++;
    }

    // If we found the correct target, stop here
    if (correctTargetRank) {
      return {
        overallReasoning,
        topMatches: allRankedMatches,
        correctTargetRank,
        totalTargetsRanked: allRankedMatches.length,
      };
    }

    // Remove the selected targets from remaining pool
    const selectedTargetIds = firstPassResult.topMatches.map(m => m.targetId);
    remainingTargets = remainingTargets.filter(
      t => !selectedTargetIds.includes(t.id),
    );
  }

  // Second pass: 7 targets → top 3 (ranks 4-6)
  if (remainingTargets.length >= 7) {
    const secondPassResult = await performSinglePassJudging(
      sessionFiles,
      remainingTargets,
    );

    // Add the next 3 matches with ranks 4-6
    for (const match of secondPassResult.topMatches) {
      allRankedMatches.push({
        rank: currentRank as 4 | 5 | 6,
        targetId: match.targetId,
        reasoning: match.reasoning,
      });

      // Check if this is the correct target
      if (match.targetId === currentTarget.id) {
        correctTargetRank = currentRank;
      }

      currentRank++;
    }

    // If we found the correct target, stop here
    if (correctTargetRank) {
      return {
        overallReasoning,
        topMatches: allRankedMatches,
        correctTargetRank,
        totalTargetsRanked: allRankedMatches.length,
      };
    }

    // Remove the selected targets from remaining pool
    const selectedTargetIds = secondPassResult.topMatches.map(m => m.targetId);
    remainingTargets = remainingTargets.filter(
      t => !selectedTargetIds.includes(t.id),
    );
  }

  // Third pass: 4 targets → top 3 (ranks 7-9)
  if (remainingTargets.length >= 4) {
    const thirdPassResult = await performSinglePassJudging(
      sessionFiles,
      remainingTargets,
    );

    // Add the next 3 matches with ranks 7-9
    for (const match of thirdPassResult.topMatches) {
      allRankedMatches.push({
        rank: currentRank as 7 | 8 | 9,
        targetId: match.targetId,
        reasoning: match.reasoning,
      });

      // Check if this is the correct target
      if (match.targetId === currentTarget.id) {
        correctTargetRank = currentRank;
      }

      currentRank++;
    }

    // If we found the correct target, stop here
    if (correctTargetRank) {
      return {
        overallReasoning,
        topMatches: allRankedMatches,
        correctTargetRank,
        totalTargetsRanked: allRankedMatches.length,
      };
    }

    // Remove the selected targets from remaining pool
    const selectedTargetIds = thirdPassResult.topMatches.map(m => m.targetId);
    remainingTargets = remainingTargets.filter(
      t => !selectedTargetIds.includes(t.id),
    );

    // After 3rd pass, always add the final remaining target as rank 10
    if (remainingTargets.length === 1) {
      allRankedMatches.push({
        rank: 10,
        targetId: remainingTargets[0].id,
        reasoning: 'Final remaining target after elimination rounds.',
      });

      // Check if this final target is the correct one
      if (remainingTargets[0].id === currentTarget.id) {
        correctTargetRank = 10;
      }
    }
  }

  return {
    overallReasoning,
    topMatches: allRankedMatches,
    correctTargetRank,
    totalTargetsRanked: allRankedMatches.length,
  };
}

// New helper function for single-pass judging
async function performSinglePassJudging(
  sessionFiles: Array<{
    url: string;
    mimeType: string;
    fileName: string;
  }>,
  targets: Array<{
    url: string;
    description: string;
    id: string;
  }>,
): Promise<{
  overallReasoning: string;
  topMatches: Array<{
    rank: 1 | 2 | 3;
    targetId: string;
    reasoning: string;
  }>;
}> {
  // Create the comparative judging prompt with session files and targets
  const { messageContent, uploadedFileIds } =
    await createComparativeJudgingPrompt(sessionFiles, targets);

  try {
    const response = await openai.chat.completions.create({
      model: 'gpt-4o',
      messages: [
        {
          role: 'system',
          content: REMOTE_VIEWING_JUDGE_SYSTEM_PROMPT,
        },
        {
          role: 'user',
          content: messageContent,
        },
      ],
      max_tokens: 2000,
      response_format: {
        type: 'json_schema',
        json_schema: {
          name: 'comparative_judging_result',
          strict: true,
          schema: {
            type: 'object',
            properties: {
              overall_reasoning: {
                type: 'string',
                description:
                  'Overall analysis of the session content and methodology used for comparison',
              },
              top_matches: {
                type: 'array',
                items: {
                  type: 'object',
                  properties: {
                    rank: {
                      type: 'integer',
                      enum: [1, 2, 3],
                      description: 'Ranking position (1st, 2nd, or 3rd choice)',
                    },
                    target_id: {
                      type: 'string',
                      description:
                        'The ID of the target that matches this rank',
                    },
                    reasoning: {
                      type: 'string',
                      description:
                        'Specific reasoning for why this target was ranked at this position',
                    },
                  },
                  required: ['rank', 'target_id', 'reasoning'],
                  additionalProperties: false,
                },
                minItems: 1,
                maxItems: 3,
                description:
                  'Array of top matching targets ranked 1-3 with individual reasoning',
              },
            },
            required: ['overall_reasoning', 'top_matches'],
            additionalProperties: false,
          },
        },
      },
    });

    const result = response.choices[0]?.message?.content?.trim();

    if (!result) {
      throw createAIError(
        'API_ERROR',
        'No comparative judging result generated',
      );
    }

    // Parse the structured JSON response
    const structuredResult = JSON.parse(result) as {
      overall_reasoning: string;
      top_matches: Array<{
        rank: 1 | 2 | 3;
        target_id: string;
        reasoning: string;
      }>;
    };
    const topMatches = structuredResult.top_matches.map(match => ({
      rank: match.rank,
      targetId: match.target_id,
      reasoning: match.reasoning,
    }));

    return {
      overallReasoning: structuredResult.overall_reasoning,
      topMatches,
    };
  } catch (error) {
    // Check if it's an OpenAI API error
    if (error && typeof error === 'object' && 'status' in error) {
      const apiError = error as { status: number };
      if (apiError.status === 429) {
        throw createAIError('RATE_LIMIT', 'Rate limit exceeded', apiError);
      } else if (apiError.status === 400) {
        throw createAIError(
          'INVALID_INPUT',
          'Invalid input provided',
          apiError,
        );
      }
    }

    throw createAIError(
      'UNKNOWN',
      'Failed to perform comparative judging',
      error,
    );
  } finally {
    // Clean up uploaded PDF files
    for (const fileId of uploadedFileIds) {
      try {
        await openai.files.del(fileId);
      } catch (error) {
        console.error(`Failed to clean up file ${fileId}:`, error);
      }
    }
  }
}

async function createComparativeJudgingPrompt(
  sessionFiles: Array<{
    url: string;
    mimeType: string;
    fileName: string;
  }>,
  shuffledTargets: Array<{
    url: string;
    description: string;
    id: string;
  }>,
): Promise<{
  messageContent: Array<
    | {
        type: 'text';
        text: string;
      }
    | {
        type: 'image_url';
        image_url: {
          url: string;
          detail: 'high';
        };
      }
    | {
        type: 'file';
        file: {
          file_id: string;
        };
      }
  >;
  uploadedFileIds: string[];
}> {
  const targetEntries = shuffledTargets.map((target, index) => ({
    ...target,
    order: index + 1,
  }));

  // Prepare session files content
  const sessionContent: Array<
    | {
        type: 'image_url';
        image_url: {
          url: string;
          detail: 'high';
        };
      }
    | {
        type: 'file';
        file: {
          file_id: string;
        };
      }
  > = [];

  // Add session files description
  const sessionFileDescriptions = sessionFiles
    .map(file => `- ${file.fileName} (${file.mimeType})`)
    .join('\n');

  // Process session files for multimodal content
  const uploadedFileIds: string[] = [];

  for (const file of sessionFiles) {
    if (file.mimeType.startsWith('image/')) {
      sessionContent.push({
        type: 'image_url',
        image_url: {
          url: file.url,
          detail: 'high',
        },
      });
    } else if (file.mimeType === 'application/pdf') {
      try {
        // Upload PDF to OpenAI for direct inclusion
        const response = await fetch(file.url);
        const pdfBytes = await response.arrayBuffer();

        const uploadedFile = await openai.files.create({
          file: new File([pdfBytes], file.fileName, {
            type: 'application/pdf',
          }),
          purpose: 'user_data',
        });

        uploadedFileIds.push(uploadedFile.id);

        sessionContent.push({
          type: 'file',
          file: {
            file_id: uploadedFile.id,
          },
        });
      } catch (error) {
        console.error(`Failed to upload PDF ${file.fileName}:`, error);
      }
    }
  }

  // Add target images
  const targetImageContent = targetEntries.map(target => ({
    type: 'image_url' as const,
    image_url: {
      url: target.url,
      detail: 'high' as const,
    },
  }));

  const targetDescriptions = targetEntries
    .map(
      target => `<target id="${target.id}">
Target ${target.order}: ${target.description}
</target>`,
    )
    .join('\n\n');

  const prompt = `Please analyze the provided remote viewing session files and determine which of the potential targets best corresponds to the session information.

**REMOTE VIEWING SESSION FILES:**
${sessionFileDescriptions}

**POTENTIAL TARGETS:**
${targetDescriptions}

**INSTRUCTIONS:**
1. First, carefully examine all the session files (images and/or PDFs) to identify key perceptual elements (visual details, shapes, colors, textures, emotions, conceptual impressions, handwritten notes, sketches, etc.)

2. Compare these perceptual elements against each target image and description by examining them side-by-side.

3. Look for both obvious visual correspondences and subtle conceptual/emotional connections that might not be immediately apparent.

4. Provide your analysis with both overall reasoning and specific reasoning for each ranked choice.

5. Return your response as JSON with the following structure:
   - "overall_reasoning": Your overall analysis of the session content and how you approached the comparison task
   - "top_matches": Array of your top 1-3 target matches, each with:
     - "rank": 1, 2, or 3 (1 being the best match)
     - "target_id": The target ID
     - "reasoning": Specific reasoning for why this particular target was ranked at this position

Remember to focus on factual correspondences between session perceptions and target characteristics. Consider both visual elements and conceptual/emotional impressions that might correspond to the targets.`;

  const messageContent = [
    {
      type: 'text' as const,
      text: prompt,
    },
    ...sessionContent,
    ...targetImageContent,
  ];

  return { messageContent, uploadedFileIds };
}

function shuffleArray<T>(array: T[]): T[] {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}

function createAIError(
  code: AIServiceError['code'],
  message: string,
  originalError?: unknown,
): AIServiceError {
  const error = new Error(message) as AIServiceError;
  error.code = code;
  error.details =
    originalError instanceof Error
      ? { message: originalError.message, stack: originalError.stack }
      : { originalError };
  return error;
}
