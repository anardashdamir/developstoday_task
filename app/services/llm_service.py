from langchain_together import ChatTogether
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from app.config import TOGETHER_API_KEY, DEFAULT_LLM_MODEL
import asyncio

class LLMService:
    def __init__(self):
        """Initialize the LLM service with ChatTogether model."""
        self.llm = ChatTogether(
            model=DEFAULT_LLM_MODEL,
            together_api_key=TOGETHER_API_KEY,
            temperature=0.7,
            max_tokens=1000
        )

        self.system_prompt = "You are a helpful AI assistant."
    
    async def generate_text(self, prompt: str, system_prompt: str = None) -> str:
        """
        Generate text using the LLM.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt to override the default
        
        Returns:
            Generated text response
        """
        try:

            messages = []
            

            if system_prompt is not None:
                messages.append(SystemMessage(content=system_prompt))
            else:
                messages.append(SystemMessage(content=self.system_prompt))
            

            messages.append(HumanMessage(content=prompt))
            

            response = await self.llm.ainvoke(messages)
            return response.content.strip()
            
        except Exception as e:
            raise Exception(f"Error generating text: {str(e)}")
    
    async def chat_completion(self, messages: list) -> str:
        """
        Generate a response based on a list of chat messages.
        
        Args:
            messages: List of chat messages, each with 'role' and 'content'
        
        Returns:
            Generated response
        """
        try:
            if not messages or not isinstance(messages, list):
                raise ValueError("Messages must be a non-empty list")

            # Convert input messages to LangChain message types
            formatted_messages = []
            system_message = self.system_prompt
            
            for msg in messages:
                if not isinstance(msg, dict) or "role" not in msg or "content" not in msg:
                    raise ValueError("Each message must be a dict with 'role' and 'content' keys")
                    
                role = msg["role"]
                content = msg["content"]
                
                if role == "system":
                    system_message = content
                elif role == "user":
                    formatted_messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    formatted_messages.append(AIMessage(content=content))
                else:
                    raise ValueError(f"Invalid role: {role}")
            

            final_messages = [SystemMessage(content=system_message)] + formatted_messages
            

            response = await self.llm.ainvoke(final_messages)
            return response.content.strip()
            
        except Exception as e:
            raise Exception(f"Error in chat completion: {str(e)}")