from pydantic import BaseModel
from typing import List, Optional


class Cocktail(BaseModel):
    name: str
    alcoholic: str  # "Alcoholic", "Non-Alcoholic", etc.
    category: str
    ingredients: List[str]
    instructions: Optional[str] = None




class CocktailQuery(BaseModel):
    query: str
    limit: int = 5
    filters: Optional[dict] = None