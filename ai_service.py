import os
import requests
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY", "")
        self.base_url = "https://api-inference.huggingface.co/models"
        
    async def summarize_task(self, description: str) -> Dict[str, any]:
        """
        Generate task summary and subtasks using AI
        """
        try:
            if not self.huggingface_api_key:
                logger.warning("No Hugging Face API key found, using fallback")
                return self._generate_fallback_response(description)
            
            # Generate summary using BART model
            summary = await self._generate_summary(description)
            
            # Generate subtasks using T5 model
            subtasks = await self._generate_subtasks(description)
            
            return {
                "summary": summary,
                "subtasks": subtasks,
                "ai_available": True
            }
            
        except Exception as e:
            logger.error(f"AI service error: {str(e)}")
            return self._generate_fallback_response(description)
    
    async def _generate_summary(self, description: str) -> str:
        """Generate task summary using BART model"""
        try:
            url = f"{self.base_url}/facebook/bart-large-cnn"
            headers = {"Authorization": f"Bearer {self.huggingface_api_key}"}
            
            payload = {
                "inputs": f"Summarize this task description in one concise sentence, focusing on the main action and goal: {description}",
                "parameters": {
                    "max_length": 60,
                    "min_length": 15,
                    "do_sample": False,
                    "num_beams": 4,
                    "early_stopping": True
                }
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            # Handle different response formats from BART model
            if isinstance(result, list) and len(result) > 0:
                # Try different possible keys for summary
                summary = (
                    result[0].get("summary_text", "") or 
                    result[0].get("generated_text", "") or 
                    result[0].get("text", "")
                )
            elif isinstance(result, dict):
                summary = (
                    result.get("summary_text", "") or 
                    result.get("generated_text", "") or 
                    result.get("text", "")
                )
            else:
                summary = ""
            
            summary = summary.strip()
            
            # Debug logging
            logger.info(f"Generated summary: '{summary}' (length: {len(summary)})")
            
            # Check if summary is too similar to original description
            if summary and len(summary) > 10:
                # If summary is very similar to description, use fallback
                if summary.lower().strip() == description.lower().strip() or len(summary) > len(description) * 0.8:
                    logger.info("Summary too similar to description, using fallback")
                    return self._create_simple_summary(description)
                return summary
            else:
                logger.info("Summary too short, using fallback")
                return self._create_simple_summary(description)
                
        except Exception as e:
            logger.error(f"Summary generation error: {str(e)}")
            return self._create_simple_summary(description)
    
    async def _generate_subtasks(self, description: str) -> List[str]:
        """Generate subtasks using T5 model"""
        try:
            url = f"{self.base_url}/t5-base"
            headers = {"Authorization": f"Bearer {self.huggingface_api_key}"}
            
            # Create a prompt for subtask generation
            prompt = f"Break down this task into 3-5 specific subtasks: {description}"
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_length": 200,
                    "min_length": 50,
                    "do_sample": True,
                    "temperature": 0.7
                }
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            generated_text = result[0].get("generated_text", "")
            
            # Parse the generated text into subtasks
            subtasks = self._parse_subtasks(generated_text, description)
            
            if subtasks:
                return subtasks
            else:
                return self._create_fallback_subtasks(description)
                
        except Exception as e:
            logger.error(f"Subtask generation error: {str(e)}")
            return self._create_fallback_subtasks(description)
    
    def _parse_subtasks(self, generated_text: str, original_description: str) -> List[str]:
        """Parse AI-generated text into structured subtasks"""
        try:
            # Clean the generated text
            text = generated_text.strip()
            
            # Try to extract numbered or bulleted items
            lines = text.split('\n')
            subtasks = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Remove common prefixes
                for prefix in ['•', '-', '*', '1.', '2.', '3.', '4.', '5.', '1)', '2)', '3)', '4)', '5)']:
                    if line.startswith(prefix):
                        line = line[len(prefix):].strip()
                        break
                
                # Clean up the line
                line = line.strip()
                if line and len(line) > 5 and not line.startswith('Task:'):
                    subtasks.append(line)
            
            # If we got good subtasks, return them
            if len(subtasks) >= 2:
                return subtasks[:5]  # Limit to 5 subtasks
            
            return []
            
        except Exception as e:
            logger.error(f"Subtask parsing error: {str(e)}")
            return []
    
    def _create_simple_summary(self, description: str) -> str:
        """Create a simple summary when AI is not available"""
        description = description.strip()
        
        # For very short descriptions, expand them to be more meaningful
        if len(description) <= 30:
            # Try to make short descriptions more descriptive
            description_lower = description.lower()
            if 'ui' in description_lower and 'test' in description_lower:
                return "Implement UI changes and create comprehensive test cases"
            elif 'ui' in description_lower:
                return "Implement user interface changes and improvements"
            elif 'test' in description_lower:
                return "Create and execute test cases for the application"
            elif 'design' in description_lower:
                return "Design and create visual components and layouts"
            elif 'implement' in description_lower:
                return "Implement the specified functionality and features"
            else:
                # For very short descriptions, make them more meaningful without prefix
                if len(description) <= 10:
                    return f"Implement {description}"
                else:
                    return description
        
        # If description is already short but not too short, return as is
        if len(description) <= 60:
            return description
        
        # Try to create a more intelligent summary
        words = description.split()
        
        # Look for key action words and create a focused summary
        action_words = ['design', 'implement', 'create', 'build', 'develop', 'test', 'deploy', 'configure', 'setup', 'install', 'configure', 'manage', 'analyze', 'review', 'optimize', 'fix', 'debug', 'update', 'upgrade', 'migrate', 'integrate']
        
        # Find the main action
        main_action = None
        for word in words:
            if word.lower() in action_words:
                main_action = word.lower()
                break
        
        if main_action:
            # Create a focused summary around the main action
            if main_action in ['design', 'create', 'build']:
                summary = f"{main_action.title()} {description.split(main_action)[1][:40].strip()}"
            elif main_action in ['implement', 'develop']:
                summary = f"{main_action.title()} {description.split(main_action)[1][:40].strip()}"
            elif main_action in ['test', 'debug']:
                summary = f"{main_action.title()} {description.split(main_action)[1][:40].strip()}"
            else:
                summary = f"{main_action.title()} {description.split(main_action)[1][:40].strip()}"
            
            # Clean up the summary
            summary = summary.strip()
            if len(summary) > 80:
                summary = summary[:77] + "..."
            
            return summary
        
        # Fallback: take first meaningful words
        if len(words) <= 8:
            return description
        
        # Take first 8-12 words and add ellipsis
        summary_words = words[:min(12, len(words))]
        summary = " ".join(summary_words)
        if len(words) > 12:
            summary += "..."
        
        # Make it more readable
        summary = summary.strip()
        if not summary.endswith('.'):
            summary += '.'
        
        return summary
    
    def _create_fallback_subtasks(self, description: str) -> List[str]:
        """Create fallback subtasks when AI is not available"""
        description_lower = description.lower()
        
        # Generic subtask patterns based on common task types
        # Check more specific patterns first
        if any(word in description_lower for word in ['ui', 'interface']) and any(word in description_lower for word in ['test', 'testing']):
            return [
                "Analyze current UI components and identify areas for improvement",
                "Design and implement UI changes based on requirements",
                "Create comprehensive test cases for UI functionality",
                "Implement automated UI testing",
                "Validate changes across different browsers and devices"
            ]
        elif any(word in description_lower for word in ['design', 'ui', 'interface']):
            return [
                "Research design requirements and user needs",
                "Create wireframes and mockups",
                "Design visual components and layouts",
                "Implement responsive design",
                "Test design across different devices"
            ]
        elif any(word in description_lower for word in ['develop', 'build', 'create', 'implement']):
            return [
                "Plan the implementation approach",
                "Set up development environment",
                "Write core functionality",
                "Add error handling and validation",
                "Test and debug the implementation"
            ]
        elif any(word in description_lower for word in ['test', 'testing', 'qa']):
            return [
                "Create test plan and test cases",
                "Set up testing environment",
                "Execute functional tests",
                "Perform integration testing",
                "Document test results and issues"
            ]
        elif any(word in description_lower for word in ['deploy', 'release', 'production']):
            return [
                "Prepare production environment",
                "Configure deployment settings",
                "Deploy to staging environment",
                "Perform final testing",
                "Deploy to production"
            ]
        else:
            # Generic subtasks for any task
            return [
                "Research and gather requirements",
                "Plan the approach and timeline",
                "Execute the main task",
                "Review and validate results",
                "Document the completed work"
            ]
    
    def _generate_fallback_response(self, description: str) -> Dict[str, any]:
        """Generate fallback response when AI is not available"""
        return {
            "summary": self._create_simple_summary(description),
            "subtasks": self._create_fallback_subtasks(description),
            "ai_available": False
        }

# Create global instance
ai_service = AIService()
