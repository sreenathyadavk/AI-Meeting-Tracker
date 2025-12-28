"""
Task extraction module using Ollama
Extracts action items from meeting transcripts using local LLM
"""
import logging
import json
from typing import List, Dict, Any
import ollama

logger = logging.getLogger(__name__)

# Carefully engineered prompt for accurate task extraction
EXTRACTION_PROMPT = """You are an AI assistant that extracts action items from meeting transcripts.

**RULES:**
1. Extract ONLY explicit commitments or assignments (e.g., "I'll do X", "Can you handle Y?")
2. DO NOT extract discussions, ideas, or questions
3. Identify the task owner if mentioned
4. Extract deadline if mentioned (convert to YYYY-MM-DD format)
5. Assign confidence score (0.0 to 1.0) based on clarity
6. Mark missing fields as "unknown"

**OUTPUT FORMAT (JSON only):**
[
  {
    "task": "Brief task description",
    "owner": "Person's name or unknown",
    "deadline": "YYYY-MM-DD or unknown",
    "confidence": 0.95
  }
]

**TRANSCRIPT:**
{transcript}

**Extract action items as JSON:**"""

async def extract_tasks(transcript: str, model: str = "llama3.1:8b") -> List[Dict[str, Any]]:
    """
    Extract action items from transcript using Ollama
    
    Args:
        transcript: Meeting transcript text
        model: Ollama model to use (default: llama3.1:8b)
        
    Returns:
        List of tasks with owner, deadline, confidence
    """
    try:
        logger.info(f"Extracting tasks using model: {model}")
        
        # Format prompt with transcript
        prompt = EXTRACTION_PROMPT.format(transcript=transcript)
        
        # Call Ollama synchronously with error handling
        try:
            logger.info("Calling Ollama API...")
            response = ollama.chat(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            logger.info("Ollama API call successful")
        except Exception as ollama_error:
            logger.error(f"Ollama API call failed: {type(ollama_error).__name__}: {str(ollama_error)}")
            return [{
                "task": f"Ollama connection error: {str(ollama_error)[:100]}",
                "owner": "unknown",
                "deadline": "unknown",
                "confidence": 0.0
            }]
        
        
        # Safely extract response text with detailed logging
        logger.info(f"Ollama response type: {type(response)}")
        logger.info(f"Ollama response keys: {response.keys() if isinstance(response, dict) else 'N/A'}")
        
        # Try to access response content safely
        try:
            if isinstance(response, dict):
                if 'message' in response:
                    response_text = response['message']['content']
                elif 'response' in response:
                    response_text = response['response']
                elif 'content' in response:
                    response_text = response['content']
                else:
                    logger.error(f"Unexpected response structure: {response}")
                    raise KeyError(f"Could not find message content in response. Keys: {list(response.keys())}")
            else:
                response_text = str(response)
                
            logger.info(f"Ollama raw response (first 200 chars): {response_text[:200]}")
            logger.info(f"Ollama raw response (FULL): {response_text}")  # Log full response
            
        except KeyError as ke:
            logger.error(f"KeyError accessing response: {str(ke)}")
            logger.error(f"Full response object: {response}")
            raise
        
        # Parse JSON from response
        # Sometimes models wrap JSON in markdown code blocks or add extra text
        original_response = response_text  # Keep original for error logging
        response_text = response_text.strip()
        
        # Remove markdown code blocks
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]
        
        response_text = response_text.strip()
        
        # Try to find JSON array using regex if direct parsing fails
        import re
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(0)
        
        logger.info(f"Cleaned response for parsing: {response_text[:300]}...")
        
        # Parse JSON
        try:
            tasks = json.loads(response_text)
        except json.JSONDecodeError as json_err:
            logger.error(f"JSON Parse Error: {str(json_err)}")
            logger.error(f"Failed to parse: {response_text}")
            logger.error(f"Original response was: {original_response}")
            return [{
                "task": "Error: Could not parse AI response - check backend logs for details",
                "owner": "unknown",
                "deadline": "unknown",
                "confidence": 0.0
            }]
        
        # Validate structure
        if not isinstance(tasks, list):
            tasks = [tasks]
        
        # Ensure all tasks have required fields
        validated_tasks = []
        for task in tasks:
            validated_task = {
                "task": task.get("task", "Unknown task"),
                "owner": task.get("owner", "unknown"),
                "deadline": task.get("deadline", "unknown"),
                "confidence": float(task.get("confidence", 0.5))
            }
            validated_tasks.append(validated_task)
        
        logger.info(f"Successfully extracted {len(validated_tasks)} tasks")
        return validated_tasks
        
    except KeyError as e:
        logger.error(f"Ollama response format error: {str(e)}")
        logger.error(f"Response structure: {response if 'response' in locals() else 'N/A'}")
        return [{
            "task": "Error: Unexpected Ollama response format",
            "owner": "unknown",
            "deadline": "unknown",
            "confidence": 0.0
        }]
    except Exception as e:
        logger.error(f"Task extraction error: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        if 'original_response' in locals():
            logger.error(f"Original Ollama response: {original_response}")
        return [{
            "task": f"Error: {str(e)[:100]}",
            "owner": "unknown",
            "deadline": "unknown",
            "confidence": 0.0
        }]
