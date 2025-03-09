from app.services.vector_store import VectorStoreService
from app.services.memory_service import MemoryService
from app.services.llm_service import LLMService
from typing import Dict, List, Any, Tuple
import logging
import re

# Configure logging
logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self, vector_store: VectorStoreService, memory_service: MemoryService, llm_service: LLMService):
        self.vector_store = vector_store
        self.memory_service = memory_service
        self.llm_service = llm_service
    
    def _enhance_query_with_preferences(self, query: str, preferences: Dict[str, List[str]]) -> str:
        """
        Enhance the search query with user preferences.
        
        Args:
            query: Original user query
            preferences: User preferences dictionary
        
        Returns:
            Enhanced query incorporating user preferences
        """
        # Skip enhancement for certain query types
        if any(term in query.lower() for term in ["how to", "what is", "explain", "history", "define"]):
            logger.info("Query appears to be informational - not enhancing with preferences")
            return query
            
        # Extract preferences
        favorite_ingredients = preferences.get("favorite_ingredients", [])
        favorite_cocktails = preferences.get("favorite_cocktails", [])
        
        # Don't enhance if no preferences exist
        if not favorite_ingredients and not favorite_cocktails:
            return query
            
        # Start with the original query
        enhanced_query = query
        
        # Add ingredients context if appropriate
        if favorite_ingredients and not any(ingredient.lower() in query.lower() for ingredient in favorite_ingredients):
            ingredients_str = ", ".join(favorite_ingredients[:3])  # Limit to top 3 to avoid too much dilution
            enhanced_query += f" with {ingredients_str}"
            
        # Add cocktail context if appropriate and not already mentioned
        if favorite_cocktails and not any(cocktail.lower() in query.lower() for cocktail in favorite_cocktails):
            # Only add cocktail preferences for recommendation queries
            if any(term in query.lower() for term in ["recommend", "suggest", "like", "similar", "enjoy"]):
                cocktails_str = ", ".join(favorite_cocktails[:2])  # Limit to top 2
                enhanced_query += f" similar to {cocktails_str}"
        
        logger.info(f"Enhanced query: '{query}' -> '{enhanced_query}'")
        return enhanced_query
    
    async def process_query(self, user_id: str, query: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Process a user query using RAG with preference-enhanced retrieval.
        
        Args:
            user_id: Unique identifier for the user
            query: The user's query
        
        Returns:
            Tuple of (response text, source documents)
        """
        
        try:
            # Process user preferences
            try:
                await self.memory_service.save_user_preferences(user_id, query)
            except Exception as e:
                logger.exception(f"Error saving user preferences: {str(e)}")
            
            # Retrieve user preferences
            try:
                user_preferences = self.memory_service.get_user_preferences(user_id)
                logger.info(f"Retrieved user preferences: {user_preferences}")
            except Exception as e:
                logger.exception(f"Error retrieving user preferences: {str(e)}")
                user_preferences = {"favorite_ingredients": [], "favorite_cocktails": []}
            
            # Initialize variables
            sources = []
            context = ""
            retrieved_cocktails = []
            
            # Determine how many cocktails the user wants
            # Default to 5 if not specified, max of 10
            requested_limit = 5  # Default value
            
            # Check if user specified a number in their query
            number_match = re.search(r'(?:show|give|get|list|display|recommend|suggest|find|want|need)\s+(?:me\s+)?(\d+)', query.lower())
            if number_match:
                requested_number = int(number_match.group(1))
                # Ensure requested number is between 1 and 10
                requested_limit = max(1, max(10, requested_number))
            
            try:
                # ENHANCEMENT: Augment query with user preferences before search
                enhanced_query = self._enhance_query_with_preferences(query, user_preferences)
                logger.info(f"Searching with enhanced query: {enhanced_query}")
                
                # Use the enhanced query for vector search
                cocktail_results = self.vector_store.search_cocktails(enhanced_query, limit=10)
                
                # Only use the number of cocktails requested or implied by the user
                limited_results = cocktail_results[:requested_limit]
                sources = limited_results

                # Build context from retrieved results without assuming metadata fields
                if requested_limit == 1:
                    context += "Based on your query, here is a relevant cocktail:\n\n"
                else:
                    context += f"Based on your query, here are {requested_limit} relevant cocktails:\n\n"
                
                # Format retrieved cocktail information as raw text
                for i, cocktail in enumerate(limited_results):
                    content = cocktail.get("metadata", "No information available")
                    context += f"{i+1}. {content}\n\n"
                    
                    # Extract cocktail name if available
                    if isinstance(content, dict) and "name" in content:
                        retrieved_cocktails.append(content["name"])
                
                # Log the retrieved cocktails
                logger.info(f"Retrieved cocktails: {retrieved_cocktails}")
                
            except Exception as e:
                logger.exception(f"Error in retrieval process: {str(e)}")
            
            # Generate response using LLM
            try:
                # Building a prompt that forces the use of retrieved cocktails
                # and respects the user's requested limit
                augmented_prompt = f"""
                You are a Cocktail Advisor chatbot that provides information about cocktails based on available data. Answer the user's question using the information provided below.

                User's question: {query}

                User's known preferences:
                - Favorite ingredients: {', '.join(user_preferences['favorite_ingredients']) if user_preferences['favorite_ingredients'] else 'None shared yet'}
                - Favorite cocktails: {', '.join(user_preferences['favorite_cocktails']) if user_preferences['favorite_cocktails'] else 'None shared yet'}

                Retrieved cocktail information:
                {context}

                INSTRUCTIONS:
                1. Focus on cocktails mentioned in the retrieved information above. Information must be from retrieved data.
                2. If information is not available, simply state "I don't have that information about that" without generating placeholder content.
                3. Base your answers on the retrieved information provided.
                4. If no cocktails are available in the retrieved data, acknowledge this directly without creating empty lists.
                5. Only provide the number of cocktails requested if they're actually available in the data. If fewer cocktails are available than requested, only discuss those that are available.
                6. If user asks about his loved ingredients or flavors, use User's known preferences to personalize your response.
                7. When the retrieval included user preferences, acknowledge this by mentioning "Based on your preference for [relevant preference]..."
                
                Formatting:
                1. Use relevant emojis where appropriate
                2. Format cocktail names in **bold**
                3. Use bullet points for ingredients and instructions
                4. Keep formatting elements proportional to the amount of actual content
                5. End with a friendly closing if cocktail information was provided

                Be informative while strictly using only the retrieved information. Adapt your response length and style to match the available data.
                """
                
                response = await self.llm_service.generate_text(augmented_prompt, system_prompt="You are a professional bartender who can identify drinks and make personalized recommendations")
                return response, sources
            except Exception as e:
                logger.exception(f"Error generating response: {str(e)}")
                return "I'm sorry, I encountered an error while generating a response. Please try again.", sources
        
        except Exception as e:
            logger.exception(f"Unhandled error in process_query: {str(e)}")
            return "I'm sorry, something went wrong. Please try again later.", []