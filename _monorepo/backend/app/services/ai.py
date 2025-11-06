"""
AI service for merchant normalization and transaction categorization using OpenAI
"""
import hashlib
import json
from typing import Optional, Tuple
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from redis import Redis
from loguru import logger

from app.core.config import settings


class AIService:
    """Service for AI-powered categorization and merchant normalization"""
    
    def __init__(self):
        """Initialize OpenAI client and Redis cache"""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
        self.model = settings.OPENAI_MODEL
        
        # Cache TTL: 30 days
        self.cache_ttl = 30 * 24 * 60 * 60
    
    def _get_cache_key(self, prefix: str, text: str) -> str:
        """Generate cache key from text"""
        text_hash = hashlib.md5(text.lower().encode()).hexdigest()
        return f"ai:{prefix}:{text_hash}"
    
    def _get_cached(self, key: str) -> Optional[dict]:
        """Get cached result"""
        try:
            cached = self.redis.get(key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache read failed: {e}")
        return None
    
    def _set_cached(self, key: str, value: dict):
        """Set cached result"""
        try:
            self.redis.setex(key, self.cache_ttl, json.dumps(value))
        except Exception as e:
            logger.warning(f"Cache write failed: {e}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def normalize_merchant(
        self,
        raw_merchant: str,
        amount: Optional[float] = None,
        locale: str = "en"
    ) -> Tuple[str, int]:
        """
        Normalize merchant name using AI
        
        Returns:
            (canonical_name, confidence_score)
        """
        # Check cache first
        cache_key = self._get_cache_key("merchant", raw_merchant)
        cached = self._get_cached(cache_key)
        if cached:
            logger.debug(f"Cache hit for merchant: {raw_merchant}")
            return cached["canonical"], cached["confidence"]
        
        # Build prompt
        prompt = f"""Given the raw merchant name from a credit card statement, normalize it to a clean, canonical merchant name.

Raw merchant: {raw_merchant}

Rules:
1. Remove transaction codes, POS numbers, location codes
2. Use proper capitalization
3. Use the most recognizable brand name
4. Be concise (2-4 words max)

Examples:
- "AMZ*MKTP US*1A2B3C" -> "Amazon"
- "STARBUCKS #12345 TORONTO" -> "Starbucks"
- "SQ *COFFEE SHOP" -> "Coffee Shop"
- "WAL-MART #1234" -> "Walmart"

Return ONLY the canonical name, nothing else."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial data expert specializing in merchant name normalization."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=50
            )
            
            canonical = response.choices[0].message.content.strip()
            
            # Simple confidence heuristic based on output
            confidence = 85 if len(canonical) < 30 else 70
            
            # Cache result
            result = {"canonical": canonical, "confidence": confidence}
            self._set_cached(cache_key, result)
            
            logger.info(f"AI normalized: '{raw_merchant}' -> '{canonical}' (confidence: {confidence})")
            
            return canonical, confidence
            
        except Exception as e:
            logger.error(f"AI merchant normalization failed: {e}")
            # Fallback: clean up raw merchant
            cleaned = raw_merchant.split('#')[0].split('*')[0].strip()
            return cleaned, 50
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def categorize_transaction(
        self,
        merchant: str,
        amount: float,
        description: Optional[str] = None,
        locale: str = "en"
    ) -> Tuple[str, Optional[str], int]:
        """
        Categorize transaction using AI
        
        Returns:
            (category, subcategory, confidence_score)
        """
        # Build cache key from all inputs
        cache_input = f"{merchant}|{amount}|{description or ''}"
        cache_key = self._get_cache_key("category", cache_input)
        cached = self._get_cached(cache_key)
        if cached:
            logger.debug(f"Cache hit for category: {merchant}")
            return cached["category"], cached.get("subcategory"), cached["confidence"]
        
        # Available categories
        categories = [
            "groceries", "dining", "subscription", "transport", "rent",
            "travel", "utilities", "pharmacy", "gas", "entertainment",
            "shopping", "other"
        ]
        
        # Build prompt
        prompt = f"""Categorize this transaction from a credit card statement.

Merchant: {merchant}
Amount: ${abs(amount):.2f}
{"Description: " + description if description else ""}

Categories: {", ".join(categories)}

Rules:
1. Choose the MOST SPECIFIC category that fits
2. If uncertain, choose "other"
3. Consider the merchant name and amount
4. Return in format: category|subcategory or just category

Examples:
- "Starbucks" -> dining|coffee
- "Walmart" -> groceries
- "Shell Gas" -> gas
- "Netflix" -> subscription|streaming
- "Uber" -> transport|rideshare

Return ONLY the category (and optional subcategory), nothing else."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial categorization expert. Be precise and consistent."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=30
            )
            
            result = response.choices[0].message.content.strip().lower()
            
            # Parse result
            parts = result.split('|')
            category = parts[0].strip()
            subcategory = parts[1].strip() if len(parts) > 1 else None
            
            # Validate category
            if category not in categories:
                logger.warning(f"AI returned invalid category: {category}, using 'other'")
                category = "other"
                confidence = 60
            else:
                confidence = 90
            
            # Cache result
            cache_result = {
                "category": category,
                "subcategory": subcategory,
                "confidence": confidence
            }
            self._set_cached(cache_key, cache_result)
            
            logger.info(
                f"AI categorized: '{merchant}' -> {category}"
                f"{('/' + subcategory) if subcategory else ''} (confidence: {confidence})"
            )
            
            return category, subcategory, confidence
            
        except Exception as e:
            logger.error(f"AI categorization failed: {e}")
            return "other", None, 50
    
    def analyze_spending_pattern(
        self,
        transactions: list,
        locale: str = "en"
    ) -> dict:
        """
        Analyze spending patterns and provide insights
        
        Args:
            transactions: List of transaction dicts with merchant, amount, category
            locale: Language for insights
        
        Returns:
            dict with insights and recommendations
        """
        if not transactions:
            return {"insights": [], "recommendations": []}
        
        # Build summary
        total_spent = sum(t["amount"] for t in transactions if t["amount"] > 0)
        category_totals = {}
        
        for t in transactions:
            cat = t.get("category", "other")
            category_totals[cat] = category_totals.get(cat, 0) + t["amount"]
        
        # Build prompt
        prompt = f"""Analyze this spending data and provide insights in {"Chinese" if locale == "zh" else "English"}.

Total spent: ${total_spent:.2f}
Number of transactions: {len(transactions)}

Category breakdown:
{chr(10).join(f"- {cat}: ${amt:.2f}" for cat, amt in sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:5])}

Provide:
1. Top 2-3 key insights about spending patterns
2. 2-3 actionable recommendations to save money

Format as JSON:
{{
  "insights": ["insight 1", "insight 2"],
  "recommendations": ["recommendation 1", "recommendation 2"]
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial advisor providing spending insights."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            result = response.choices[0].message.content.strip()
            
            # Parse JSON
            # Remove markdown code blocks if present
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()
            
            insights_data = json.loads(result)
            
            logger.info(f"Generated {len(insights_data.get('insights', []))} insights")
            
            return insights_data
            
        except Exception as e:
            logger.error(f"AI spending analysis failed: {e}")
            return {
                "insights": ["Unable to analyze spending patterns at this time."],
                "recommendations": []
            }


# Global instance
ai_service = AIService()
