from app.services.vector_store import VectorStoreService
from app.services.llm_service import LLMService
from app.config import USER_PREFERENCE_PROMPT
import json
from typing import Dict, List, Any
import logging
from datetime import datetime
import re

# Configure logging
logger = logging.getLogger(__name__)

class MemoryService:
    def __init__(self, vector_store: VectorStoreService, llm_service: LLMService):
        self.vector_store = vector_store
        self.llm_service = llm_service
    
    async def detect_preferences(self, user_message: str) -> Dict[str, List[str]]:
        """
        Detect user preferences (favorite ingredients, cocktails) from a message.
        
        Args:
            user_message: The message from the user
        
        Returns:
            Dictionary with detected preferences
        """
        try:
            # Check if USER_PREFERENCE_PROMPT is properly defined
            if not USER_PREFERENCE_PROMPT:
                logger.error("USER_PREFERENCE_PROMPT is not defined or empty")
                return {
                    "favorite_ingredients": [],
                    "favorite_cocktails": []
                }
            
            # Make sure user_message is a string
            if not isinstance(user_message, str) or not user_message.strip():
                logger.warning(f"Invalid user_message: {user_message}")
                return {
                    "favorite_ingredients": [],
                    "favorite_cocktails": []
                }
            
            # Format the prompt with the user message
            try:
                prompt = USER_PREFERENCE_PROMPT.format(message=user_message)
            except Exception as format_error:
                logger.error(f"Error formatting USER_PREFERENCE_PROMPT: {str(format_error)}")
                # Fall back to a basic prompt if formatting fails
                prompt = f"Extract favorite cocktail ingredients and cocktails from this message: {user_message}. Return as JSON with keys 'favorite_ingredients' and 'favorite_cocktails'."
            
            # Log the prompt for debugging
            logger.debug(f"Formatted prompt for preference detection: {prompt}")
            
            # Use the LLM to detect preferences with specific JSON instruction
            system_prompt = "You are an assistant that extracts user preferences and returns them in valid JSON format only."
            response = await self.llm_service.generate_text(prompt, system_prompt=system_prompt)
            logger.info(f"LLM response for preference detection: {response}")
            
            try:
                # Try to find and extract JSON from the response
                json_match = re.search(r'(\{.*\})', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    logger.debug(f"Extracted JSON string: {json_str}")
                    
                    # Try to parse JSON response
                    preferences = json.loads(json_str)
                    
                    # Ensure the expected keys are present, with defaults if not
                    if not isinstance(preferences, dict):
                        logger.warning(f"LLM response is not a dictionary: {preferences}")
                        return {
                            "favorite_ingredients": [],
                            "favorite_cocktails": []
                        }
                    
                    # Ensure the expected keys are present
                    preferences.setdefault("favorite_ingredients", [])
                    preferences.setdefault("favorite_cocktails", [])
                    
                    # Ensure values are lists
                    if not isinstance(preferences["favorite_ingredients"], list):
                        preferences["favorite_ingredients"] = []
                    if not isinstance(preferences["favorite_cocktails"], list):
                        preferences["favorite_cocktails"] = []
                    
                    # Log detected preferences
                    logger.info(f"Detected preferences: {preferences}")
                    return preferences
                else:
                    logger.error(f"No JSON found in LLM response: {response}")
                    return {
                        "favorite_ingredients": [],
                        "favorite_cocktails": []
                    }
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from LLM response: {response}. Error: {str(e)}")

                return {
                    "favorite_ingredients": [],
                    "favorite_cocktails": []
                }
        except Exception as e:
            logger.exception(f"Error detecting preferences: {str(e)}")
            return {
                "favorite_ingredients": [],
                "favorite_cocktails": []
            }
    
    async def save_user_preferences(self, user_id: str, user_message: str) -> bool:
        """
        Save user preferences detected from a message.
        
        Args:
            user_id: Unique identifier for the user
            user_message: The message from the user
        
        Returns:
            True if preferences were detected and saved, False otherwise
        """
        try:
            preferences = await self.detect_preferences(user_message)
            logger.info(f"Detected preferences for user {user_id}: {preferences}")
            

            has_preferences = len(preferences["favorite_ingredients"]) > 0 or len(preferences["favorite_cocktails"]) > 0
            
            if has_preferences:

                preferences["timestamp"] = datetime.now().isoformat()
                

                memory_id = self.vector_store.store_user_memory(user_id, preferences)
                if memory_id:
                    logger.info(f"Successfully stored preferences with ID {memory_id}")
                    return True
                else:
                    logger.error("Failed to store preferences in vector store")
                    return False
            else:
                logger.info(f"No preferences detected for user {user_id}")
            
            return False
        except Exception as e:
            logger.exception(f"Error saving user preferences: {str(e)}")
            return False
    
    def get_user_preferences(self, user_id: str) -> Dict[str, List[str]]:
        """
        Get the latest user preferences.
        
        Args:
            user_id: Unique identifier for the user
        
        Returns:
            Dictionary with user preferences
        """
        try:
            logger.info(f"Retrieving preferences for user {user_id}")
            memories = self.vector_store.get_user_memories(user_id)
            logger.info(f"Retrieved {len(memories)} memory entries for user {user_id}")
            

            all_ingredients = set()
            all_cocktails = set()
            
            for memory in memories:
                metadata = memory.get("metadata", {})
                
                if not isinstance(metadata, dict):
                    logger.warning(f"Unexpected metadata format: {metadata}")
                    continue
                
                ingredients = metadata.get("favorite_ingredients", [])
                cocktails = metadata.get("favorite_cocktails", [])
                
                if isinstance(ingredients, list):
                    all_ingredients.update(ingredients)
                elif ingredients:
                    logger.warning(f"Unexpected ingredients format: {ingredients}")
                    
                if isinstance(cocktails, list):
                    all_cocktails.update(cocktails)
                elif cocktails:
                    logger.warning(f"Unexpected cocktails format: {cocktails}")
            
            result = {
                "favorite_ingredients": list(all_ingredients),
                "favorite_cocktails": list(all_cocktails)
            }
            logger.info(f"Aggregated preferences for user {user_id}: {result}")
            return result
        except Exception as e:
            logger.exception(f"Error getting user preferences: {str(e)}")
            return {
                "favorite_ingredients": [],
                "favorite_cocktails": []
            }