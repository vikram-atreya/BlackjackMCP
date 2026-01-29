"""
AI Player for Blackjack - plays automatically by asking LLM for decisions.
"""
from typing import Tuple, Optional
import os
from openai import AzureOpenAI


class AIPlayerStrategy:
    """AI player that asks LLM for blackjack decisions."""
    
    SYSTEM_PROMPT = """You are an AI playing blackjack. Given the game state, decide your action.

Rules:
- Dealer must hit on 16 or less, stand on 17+
- You can only see one dealer card
- Going over 21 = bust = lose

You MUST respond with EXACTLY ONE WORD from: HIT, STAND, or DOUBLE
Nothing else. Just the action word."""

    _client: Optional[AzureOpenAI] = None
    _model: str = "gpt-5.2-chat"
    
    @classmethod
    def _get_client(cls) -> Optional[AzureOpenAI]:
        """Get or create the Azure OpenAI client."""
        if cls._client is None:
            azure_key = os.getenv("AZURE_OPENAI_API_KEY")
            azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://vikramatagenteastus2.openai.azure.com/")
            
            if azure_key and azure_endpoint:
                try:
                    cls._client = AzureOpenAI(
                        api_key=azure_key,
                        api_version="2024-02-15-preview",
                        azure_endpoint=azure_endpoint
                    )
                except Exception as e:
                    print(f"Warning: Could not initialize Azure OpenAI: {e}")
        return cls._client
    
    @classmethod
    def decide(cls, player_hand: list, player_score: int, dealer_visible_card: str,
               dealer_visible_score: int, can_double: bool, num_cards: int) -> Tuple[str, str]:
        """
        Ask LLM to decide the action.
        
        Returns:
            Tuple of (action, reason)
        """
        client = cls._get_client()
        
        user_message = f"""My hand: {', '.join(player_hand)} (Score: {player_score})
Dealer shows: {dealer_visible_card} (Value: {dealer_visible_score})
Available actions: HIT, STAND{', DOUBLE' if can_double else ''}

What should I do? Reply with just ONE word: HIT, STAND, or DOUBLE"""

        if client:
            try:
                response = client.chat.completions.create(
                    model=cls._model,
                    messages=[
                        {"role": "system", "content": cls.SYSTEM_PROMPT},
                        {"role": "user", "content": user_message}
                    ],
                    max_completion_tokens=10
                )
                
                if response.choices and len(response.choices) > 0:
                    content = response.choices[0].message.content
                    if content:
                        action_word = content.strip().upper()
                        
                        # Parse the response
                        if "DOUBLE" in action_word and can_double:
                            return "double_down", f"LLM decided to double down"
                        elif "STAND" in action_word:
                            return "stand", f"LLM decided to stand on {player_score}"
                        elif "HIT" in action_word:
                            return "hit", f"LLM decided to hit on {player_score}"
                        else:
                            # Default to hit if unclear
                            return "hit", f"LLM response unclear: '{content}', defaulting to hit"
                            
            except Exception as e:
                print(f"   [AI Player API Error]: {e}")
        
        # Fallback: simple logic if API fails
        if player_score >= 17:
            return "stand", f"Fallback: standing on {player_score}"
        elif player_score <= 11:
            return "hit", f"Fallback: hitting on {player_score}"
        else:
            return "hit", f"Fallback: hitting on {player_score}"
    
    @staticmethod
    def decide_bet(chips: int) -> int:
        """
        Decide bet amount. AI uses conservative betting.
        
        Args:
            chips: Available chips
        
        Returns:
            Bet amount (10% of chips, min 1, max 50)
        """
        bet = max(1, min(chips // 10, 50))
        return bet

# AI Player names for variety
AI_NAMES = [
    "🤖 Bot-Alpha",
    "🤖 Bot-Beta", 
    "🤖 Bot-Gamma",
    "🤖 Bot-Delta",
    "🤖 Bot-Epsilon",
    "🤖 Bot-Zeta",
]
