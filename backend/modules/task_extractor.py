"""
Task extraction module using Ollama - FRESH VERSION
Extracts action items from meeting transcripts using local LLM
"""
import logging
import json
import re
from typing import List, Dict, Any
import ollama

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """Extract action items from this meeting transcript.

Rules:
- Only extract explicit commitments or assignments
- Identify task owner if mentioned
- Extract deadline if mentioned (YYYY-MM-DD format)
- Return JSON array only

Transcript: {transcript}

Return JSON array like: [{{"task": "...", "owner": "...", "deadline": "...", "confidence": 0.9}}]"""

async def extract_tasks(transcript: str, model: str = "llama3.1:8b") -> List[Dict[str, Any]]:
    """Extract action items from transcript using Ollama"""
    try:
        logger.info(f"🤖 Calling Ollama with model: {model}")
        
        prompt = EXTRACTION_PROMPT.format(transcript=transcript)
        
        # Call Ollama
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        
        logger.info("✅ Ollama responded successfully")
        
        # Extract content
        content = response['message']['content']
        logger.info(f"📝 Response preview: {content[:200]}")
        
        # Clean response
        content = content.strip()
        
        # Remove markdown code blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        content = content.strip()
        
        # Try to extract JSON array
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            content = json_match.group(0)
        
        logger.info(f"🔍 Parsing JSON: {content[:300]}")
        
        # Parse JSON
        tasks = json.loads(content)
        
        if not isinstance(tasks, list):
            tasks = [tasks]
        
        # Validate and format - handle flexible field names
        result = []
        for task in tasks:
            # Extract task description (try multiple field names)
            task_desc = (
                task.get("task") or 
                task.get("topic") or 
                task.get("description") or 
                task.get("action") or
                "Unknown task"
            )
            
            # If description is separate, append it to task
            if task.get("description") and task.get("topic"):
                task_desc = f"{task.get('topic')}: {task.get('description')}"
            
            result.append({
                "task": task_desc,
                "owner": task.get("owner") or task.get("assignee") or "unknown",
                "deadline": task.get("deadline") or task.get("due_date") or "unknown",
                "confidence": float(task.get("confidence", 0.7))
            })
        
        logger.info(f"✨ Successfully extracted {len(result)} tasks")
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON parse error: {e}")
        logger.error(f"Content was: {content if 'content' in locals() else 'N/A'}")
        return [{
            "task": "Could not parse AI response - check logs",
            "owner": "unknown",
            "deadline": "unknown",
            "confidence": 0.0
        }]
    except Exception as e:
        logger.error(f"❌ Error: {type(e).__name__}: {str(e)}")
        return [{
            "task": f"Error: {str(e)[:100]}",
            "owner": "unknown",
            "deadline": "unknown",
            "confidence": 0.0
        }]
