"""
AI Advisor for Blackjack - gives players strategic advice.
Uses LLM API (OpenAI or Azure OpenAI) to analyze game state and recommend actions.
"""
import os
from typing import Optional
from openai import OpenAI, AzureOpenAI


class AIAdvisor:
    """AI-powered advisor that recommends blackjack actions."""
    
    SYSTEM_PROMPT = """You are a blackjack strategy advisor. Given the current game state, recommend the optimal action.

Rules reminder:
- Dealer must hit on 16 or less, stand on 17+
- Blackjack (Ace + 10-value) pays 3:2
- You can only see one of the dealer's cards

Basic strategy principles:
- Stand on 17+ always
- Stand on 13-16 if dealer shows 2-6 (dealer likely to bust)
- Hit on 13-16 if dealer shows 7-A (dealer likely has strong hand)
- Double down on 11, and on 10 if dealer shows 2-9
- Always hit on 8 or less

Respond with ONLY one of these actions and a brief reason (max 15 words):
- HIT: [reason]
- STAND: [reason]
- DOUBLE: [reason]

Be concise. Example: "STAND: 18 is strong, dealer showing 6 likely busts."
"""

    def __init__(self, 
                 api_key: Optional[str] = None, 
                 model: str = "gpt-4o-mini",
                 azure_endpoint: Optional[str] = None,
                 azure_deployment: Optional[str] = None,
                 azure_api_version: str = "2024-02-15-preview"):
        """
        Initialize the AI advisor.
        
        For regular OpenAI:
            api_key: OpenAI API key (or set OPENAI_API_KEY env var)
            model: Model name (default: gpt-4o-mini)
        
        For Azure OpenAI:
            api_key: Azure OpenAI API key (or set AZURE_OPENAI_API_KEY env var)
            azure_endpoint: Azure endpoint URL (or set AZURE_OPENAI_ENDPOINT env var)
                           e.g., "https://your-resource.openai.azure.com/"
            azure_deployment: Deployment name (or set AZURE_OPENAI_DEPLOYMENT env var)
            azure_api_version: API version (default: 2024-02-15-preview)
        """
        self.client = None
        self.enabled = False
        self.model = model
        self.use_azure = False
        
        # Check for Azure OpenAI first
        azure_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        azure_endpoint = azure_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT", "https://vikramatagenteastus2.openai.azure.com/")
        azure_deployment = azure_deployment or os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5.2-chat")
        
        if azure_key and azure_endpoint:
            try:
                self.client = AzureOpenAI(
                    api_key=azure_key,
                    api_version=azure_api_version,
                    azure_endpoint=azure_endpoint
                )
                self.model = azure_deployment or "gpt-4o-mini"  # Use deployment name
                self.use_azure = True
                self.enabled = True
                # print(f"   Using Azure OpenAI: {azure_endpoint}")
            except Exception as e:
                print(f"Warning: Could not initialize Azure OpenAI client: {e}")
        else:
            # Fall back to regular OpenAI
            openai_key = api_key or os.getenv("OPENAI_API_KEY")
            if openai_key:
                try:
                    self.client = OpenAI(api_key=openai_key)
                    self.enabled = True
                except Exception as e:
                    print(f"Warning: Could not initialize OpenAI client: {e}")
    
    def is_available(self) -> bool:
        """Check if AI advisor is available."""
        return self.enabled and self.client is not None
    
    def get_advice(self, player_hand: list, player_score: int, 
                   dealer_visible_card: str, dealer_visible_score: int,
                   can_double: bool = True) -> str:
        """
        Get AI advice for the current situation.
        
        Args:
            player_hand: List of card strings in player's hand
            player_score: Player's current score
            dealer_visible_card: Dealer's face-up card
            dealer_visible_score: Value of dealer's visible card
            can_double: Whether double down is available
        
        Returns:
            Advice string with recommended action and reason
        """
        if not self.is_available():
            return self._fallback_basic_strategy(player_score, dealer_visible_score, can_double)
        
        # Build the game state message
        user_message = f"""Current situation:
- Your hand: {', '.join(player_hand)} (Score: {player_score})
- Dealer shows: {dealer_visible_card} (Value: {dealer_visible_score})
- Available actions: Hit, Stand{', Double Down' if can_double else ''}

What should I do?"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                max_completion_tokens=15000
            )
            
            # Debug: print the full response structure
            print(f"   [DEBUG] Response: {response}")
            
            # Handle different response structures
            if response.choices and len(response.choices) > 0:
                choice = response.choices[0]
                print(f"   [DEBUG] Choice: {choice}")
                
                # Try different ways to get content
                content = None
                if hasattr(choice, 'message') and choice.message:
                    content = choice.message.content
                elif hasattr(choice, 'text'):
                    content = choice.text
                
                print(f"   [DEBUG] Content: {content}")
                
                if content:
                    return content.strip()
            
            # If no content, fall back to basic strategy
            print("   [DEBUG] No content found, using fallback")
            return self._fallback_basic_strategy(player_score, dealer_visible_score, can_double)
        except Exception as e:
            print(f"AI API error: {e}")
            return self._fallback_basic_strategy(player_score, dealer_visible_score, can_double)
    
    def _fallback_basic_strategy(self, player_score: int, dealer_score: int, 
                                  can_double: bool) -> str:
        """Fallback to basic strategy when API unavailable."""
        
        # Always stand on 17+
        if player_score >= 17:
            return f"STAND: You have {player_score}. Never hit on 17 or higher - too risky to bust."
        
        # 11 is the best double down hand
        if player_score == 11:
            if can_double:
                return f"DOUBLE DOWN: You have 11. Any 10-value card gives you 21. Best doubling hand!"
            else:
                return f"HIT: You have 11. Any 10-value card gives you 21."
        
        # 10 - double against weak dealer
        if player_score == 10:
            if can_double and dealer_score <= 9:
                return f"DOUBLE DOWN: You have 10 vs dealer's {dealer_score}. High chance of getting 20, dealer likely busts."
            else:
                return f"HIT: You have 10. Good chance to improve to 20."
        
        # 9 - double against dealer 3-6
        if player_score == 9 and can_double and 3 <= dealer_score <= 6:
            return f"DOUBLE DOWN: You have 9 vs dealer's {dealer_score}. Dealer showing weak card, likely to bust."
        
        # Dealer shows weak card (2-6) - they're likely to bust
        if dealer_score <= 6:
            if player_score >= 13:
                return f"STAND: Dealer shows {dealer_score} (weak). With {player_score}, let dealer bust - they must hit to 17."
            elif player_score == 12 and dealer_score >= 4:
                return f"STAND: Dealer shows {dealer_score}. Your {player_score} is risky to hit (10 busts you). Let dealer bust."
            else:
                return f"HIT: You have {player_score}. Too low to stand even vs dealer's weak {dealer_score}."
        
        # Dealer shows strong card (7-A)
        if player_score <= 11:
            return f"HIT: You have {player_score} vs dealer's {dealer_score}. Can't bust, must improve your hand."
        elif player_score <= 16:
            return f"HIT: You have {player_score} vs dealer's {dealer_score}. Dealer likely has 17+, you need to improve or lose."
        
        return f"HIT: You have {player_score}. Need a stronger hand vs dealer's {dealer_score}."


# Singleton instance for easy access
_advisor: Optional[AIAdvisor] = None


def get_advisor() -> AIAdvisor:
    """Get or create the AI advisor singleton."""
    global _advisor
    if _advisor is None:
        _advisor = AIAdvisor()
    return _advisor


def get_advice_for_game_state(game_state: dict, player_name: str) -> str:
    """
    Convenience function to get advice from a game state dict.
    
    Args:
        game_state: The game state dictionary from game.get_state()
        player_name: Name of the player requesting advice
    
    Returns:
        Advice string
    """
    advisor = get_advisor()
    
    # Find the player
    player_data = None
    for p in game_state.get('players', []):
        if p['name'].lower() == player_name.lower():
            player_data = p
            break
    
    if not player_data:
        return "Could not find player data."
    
    dealer_data = game_state.get('dealer', {})
    
    # Check if double down is available (only on 2-card hand)
    can_double = len(player_data.get('hand', [])) == 2
    
    return advisor.get_advice(
        player_hand=player_data.get('hand', []),
        player_score=player_data.get('score', 0),
        dealer_visible_card=dealer_data.get('hand', ['?'])[0],
        dealer_visible_score=dealer_data.get('visible_score', 0),
        can_double=can_double
    )
