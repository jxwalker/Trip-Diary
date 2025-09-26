"""
Optimized Perplexity Service
High-performance service with concurrent processing, smart caching, and optimized timeouts
"""
import os
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Callable, Awaitable
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv
import logging

# Load environment
root_dir = Path(__file__).parent.parent.parent.parent
env_path = root_dir / ".env"
load_dotenv(env_path)

logger = logging.getLogger(__name__)


@dataclass
class PerplexityConfig:
    """Optimized Perplexity configuration"""
    api_key: str
    model: str = "sonar"  # Use faster model by default
    timeout: int = 30  # Increased timeout for complex prompts
    max_tokens: int = 3000  # Balanced token limit
    temperature: float = 0.3  # Lower for more consistent results
    max_concurrent: int = 3  # Limit concurrent requests to avoid rate limits
    retry_attempts: int = 2  # Quick retry logic
    retry_delay: float = 1.0  # Fast retry delay


class OptimizedPerplexityService:
    """
    High-performance Perplexity service with:
    - Concurrent processing for multiple requests
    - Smart caching to reduce API calls
    - Optimized timeouts and retry logic
    - Consistent model and parameter usage
    """
    
    def __init__(self):
        self.config = PerplexityConfig(
            api_key=os.getenv("PERPLEXITY_API_KEY", ""),
            model=os.getenv("PERPLEXITY_MODEL", "sonar"),
            timeout=int(os.getenv("PERPLEXITY_TIMEOUT", "30")),  # Increased from 20 to 30 seconds
            max_tokens=int(os.getenv("PERPLEXITY_MAX_TOKENS", "3000")),
            temperature=float(os.getenv("PERPLEXITY_TEMPERATURE", "0.3"))
        )
        
        # In-memory cache for destination data (24 hour TTL)
        self._cache: Dict[str, Dict] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        self._semaphore = asyncio.Semaphore(self.config.max_concurrent)
        
        self._failure_count = 0
        self._last_failure_time = None
        self._circuit_open = False
        self._circuit_breaker_threshold = 5
        self._circuit_breaker_timeout = 300
        
        # OpenAI client for parsing (if available)
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if openai_api_key:
            import openai
            self.openai_client = openai.AsyncOpenAI(api_key=openai_api_key)
        else:
            self.openai_client = None
    
    async def generate_complete_guide_data(
        self,
        destination: str,
        start_date: str,
        end_date: str,
        preferences: Dict,
        progress_callback: Optional[Callable[[int, str], Awaitable[None]]] = None
    ) -> Dict:
        """
        Generate complete guide data using concurrent API calls
        This is the main entry point for optimized guide generation
        """
        if not self.config.api_key:
            return self._create_error_response("Perplexity API key not configured")
        
        logger.debug(f"generate_complete_guide_data called with callback: {progress_callback}")
        
        if progress_callback:
            try:
                logger.debug(f"Calling progress_callback with (10, 'Starting concurrent data fetching')")
                await progress_callback(10, "Starting concurrent data fetching")
            except Exception as e:
                logger.error(f"Error calling progress_callback: {e}")
                raise
        
        # Check cache first
        cache_key = f"{destination}_{start_date}_{end_date}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            if progress_callback:
                await progress_callback(100, "Using cached data")
            return cached_data
        
        # Prepare concurrent tasks
        tasks = []
        
        # Task 1: Restaurants and dining
        tasks.append(self._fetch_restaurants(destination, preferences))
        
        # Task 2: Attractions and activities  
        tasks.append(self._fetch_attractions(destination, preferences))
        
        # Task 3: Events and entertainment
        tasks.append(self._fetch_events(destination, start_date, end_date, preferences))
        
        # Task 4: Practical information
        tasks.append(self._fetch_practical_info(destination))
        
        # Task 5: Daily itinerary suggestions
        tasks.append(self._fetch_daily_suggestions(destination, start_date, end_date, preferences))
        
        if progress_callback:
            await progress_callback(30, "Fetching data concurrently")
        
        try:
            # Execute all tasks concurrently with timeout
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=self.config.timeout * 2  # Allow extra time for concurrent requests
            )
            
            if progress_callback:
                await progress_callback(80, "Processing results")
            
            # Process results
            restaurants, attractions, events, practical_info, daily_suggestions = results
            
            # Handle any exceptions
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.warning(f"Task {i} failed: {result}")
                    results[i] = []  # Use empty list as fallback
            
            # Combine results
            guide_data = {
                "destination": destination,
                "start_date": start_date,
                "end_date": end_date,
                "restaurants": restaurants if not isinstance(restaurants, Exception) else [],
                "attractions": attractions if not isinstance(attractions, Exception) else [],
                "events": events if not isinstance(events, Exception) else [],
                "practical_info": practical_info if not isinstance(practical_info, Exception) else {},
                "daily_suggestions": daily_suggestions if not isinstance(daily_suggestions, Exception) else [],
                "generated_at": datetime.now().isoformat(),
                "cache_key": cache_key
            }
            
            # Cache the results
            self._cache_data(cache_key, guide_data)
            
            if progress_callback:
                await progress_callback(100, "Guide data ready")
            
            return guide_data
            
        except asyncio.TimeoutError:
            logger.error(f"Timeout generating guide data for {destination}")
            return self._create_error_response(f"Timeout generating guide data for {destination}")
        except Exception as e:
            logger.error(f"Error generating guide data: {e}")
            return self._create_error_response(f"Error generating guide data: {str(e)}")
    
    async def _fetch_restaurants(self, destination: str, preferences: Dict) -> List[Dict]:
        """Fetch restaurant recommendations"""
        cuisine_types = preferences.get("cuisineTypes", [])
        price_range = preferences.get("priceRange", "")
        
        prompt = f"""Find the top 8 restaurants in {destination} for these preferences:
- Cuisine types: {', '.join(cuisine_types)}
- Price range: {price_range}
- Include mix of local favorites and popular spots

For each restaurant provide:
- Name
- Cuisine type
- Price range ($/$$/$$$/$$$$)
- Address
- Why recommended (1 sentence)
- Reservation info if needed

Return as JSON array with these exact keys: name, cuisine, price_range, address, recommendation, reservation_info"""
        
        try:
            response = await self._make_api_request(prompt)
            return await self._parse_json_response(response, "restaurants") or []
        except Exception as e:
            logger.warning(f"Restaurant fetch failed: {e}")
            return []
    
    async def _fetch_attractions(self, destination: str, preferences: Dict) -> List[Dict]:
        """Fetch attraction recommendations"""
        interests = preferences.get("specialInterests", ["culture", "history", "landmarks"])
        
        prompt = f"""Find the top 8 attractions in {destination} for these interests:
- Special interests: {', '.join(interests)}
- Include mix of must-see landmarks and hidden gems

For each attraction provide:
- Name
- Type/category
- Address
- Opening hours
- Admission price
- Why visit (1 sentence)
- Time needed for visit

Return as JSON array with these exact keys: name, type, address, hours, price, description, time_needed"""
        
        try:
            response = await self._make_api_request(prompt)
            return await self._parse_json_response(response, "attractions") or []
        except Exception as e:
            logger.warning(f"Attractions fetch failed: {e}")
            return []
    
    async def _fetch_events(self, destination: str, start_date: str, end_date: str, preferences: Dict) -> List[Dict]:
        """Fetch events happening during travel dates"""
        prompt = f"""Find REAL events happening in {destination} between {start_date} and {end_date}:
- Concerts, shows, exhibitions, festivals
- Sports events, cultural events
- Seasonal activities

For each event provide:
- Name
- Date and time
- Venue
- Ticket price range
- Brief description
- How to book

Return as JSON array with these exact keys: name, date, venue, price_range, description, booking_info"""
        
        try:
            response = await self._make_api_request(prompt)
            return await self._parse_json_response(response, "events") or []
        except Exception as e:
            logger.warning(f"Events fetch failed: {e}")
            return []
    
    async def _fetch_practical_info(self, destination: str) -> Dict:
        """Fetch practical travel information"""
        prompt = f"""Provide practical travel information for {destination}:

1. Transportation: How to get around (public transit, taxis, walking)
2. Currency: Local currency and payment methods
3. Language: Local language and English usage
4. Tipping: Tipping customs and amounts
5. Safety: General safety tips and areas to avoid
6. Emergency: Emergency numbers and useful contacts

Return as JSON object with keys: transportation, currency, language, tipping, safety, emergency"""
        
        try:
            response = await self._make_api_request(prompt)
            return await self._parse_json_response(response, "practical_info") or {}
        except Exception as e:
            logger.warning(f"Practical info fetch failed: {e}")
            return {}
    
    async def _fetch_daily_suggestions(self, destination: str, start_date: str, end_date: str, preferences: Dict) -> List[Dict]:
        """Fetch daily activity suggestions"""
        from datetime import datetime, timedelta
        
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        days = (end - start).days + 1
        
        prompt = f"""Create {days} days of activity suggestions for {destination} from {start_date} to {end_date}:

For each day provide:
- Day number and date
- Morning activity (9-12pm)
- Afternoon activity (1-5pm)  
- Evening activity (6-10pm)
- Walking/transport between activities
- Estimated costs

Consider traveler preferences: {preferences.get('specialInterests', [])}

Return as JSON array with keys: day, date, morning, afternoon, evening, transport_notes, estimated_cost"""
        
        try:
            response = await self._make_api_request(prompt)
            return await self._parse_json_response(response, "daily_suggestions") or []
        except Exception as e:
            logger.warning(f"Daily suggestions fetch failed: {e}")
            return []

    def _check_circuit_breaker(self) -> bool:
        """Check if circuit breaker should prevent API calls"""
        if not self._circuit_open:
            return False
            
        # Check if enough time has passed to try again
        if self._last_failure_time:
            time_since_failure = (datetime.now() - self._last_failure_time).total_seconds()
            if time_since_failure > self._circuit_breaker_timeout:
                logger.info("Circuit breaker timeout expired, allowing API calls")
                self._circuit_open = False
                self._failure_count = 0
                return False
        
        return True
    
    def _record_success(self):
        """Record successful API call"""
        self._failure_count = 0
        self._circuit_open = False
        self._last_failure_time = None
    
    def _record_failure(self):
        """Record failed API call and potentially open circuit breaker"""
        self._failure_count += 1
        self._last_failure_time = datetime.now()
        
        if self._failure_count >= self._circuit_breaker_threshold:
            self._circuit_open = True
            logger.warning(f"Circuit breaker opened after {self._failure_count} consecutive failures")

    async def search(
        self,
        query: str,
        max_results: int = 10,
        search_type: str = "web"
    ) -> Dict[str, Any]:
        """
        Perform a search query using Perplexity API
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            search_type: Type of search (web, academic, etc.)
            
        Returns:
            Dictionary containing search results
        """
        try:
            search_prompt = f"""
            Search for: {query}
            
            Please provide comprehensive information about this query.
            Include relevant facts, current information, and practical details.
            Format the response as structured information that would be useful for travel planning.
            
            Limit to {max_results} key pieces of information.
            """
            
            response = await self._make_api_request(search_prompt)
            
            if response and not isinstance(response, str):
                return {
                    "query": query,
                    "results": response,
                    "search_type": search_type,
                    "max_results": max_results,
                    "success": True
                }
            else:
                logger.error(f"Search failed for query: {query}")
                return {
                    "query": query,
                    "results": [],
                    "error": "Search request failed",
                    "success": False
                }
                
        except Exception as e:
            logger.error(f"Search error for query '{query}': {e}")
            return {
                "query": query,
                "results": [],
                "error": str(e),
                "success": False
            }

    async def search_with_context(
        self,
        query: str,
        context: str,
        max_results: int = 10
    ) -> Dict[str, Any]:
        """
        Search with additional context using Perplexity API
        
        Args:
            query: Search query string
            context: Additional context for the search
            max_results: Maximum number of results to return
            
        Returns:
            Dictionary containing search results with context
        """
        try:
            # Combine query and context for better search results
            contextual_prompt = f"""
            Context: {context}
            
            Search for: {query}
            
            Please provide comprehensive information about this query within the given context.
            Include relevant facts, current information, and practical details.
            Format the response as structured information that would be useful for travel planning.
            
            Limit to {max_results} key pieces of information.
            """
            
            response = await self._make_api_request(contextual_prompt)
            
            if response and isinstance(response, str):
                return {
                    "query": query,
                    "context": context,
                    "results": response,
                    "max_results": max_results,
                    "success": True
                }
            else:
                logger.error(f"Contextual search failed for query: {query}")
                return {
                    "query": query,
                    "context": context,
                    "results": [],
                    "error": "Contextual search request failed",
                    "success": False
                }
                
        except Exception as e:
            logger.error(f"Contextual search error for query '{query}': {e}")
            return {
                "query": query,
                "context": context,
                "results": [],
                "error": str(e),
                "success": False
            }

    async def _make_api_request(self, prompt: str) -> str:
        """Make optimized API request to Perplexity with retry logic and circuit breaker"""
        if self._check_circuit_breaker():
            logger.warning("Circuit breaker is open, skipping Perplexity API call")
            raise Exception("Circuit breaker is open - too many recent failures")
        
        async with self._semaphore:  # Limit concurrent requests
            for attempt in range(self.config.retry_attempts):
                try:
                    timeout = aiohttp.ClientTimeout(
                        total=min(self.config.timeout, 15),  # Cap at 15 seconds
                        connect=5,  # 5 second connect timeout
                        sock_read=10  # 10 second read timeout
                    )
                    
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        headers = {
                            "Authorization": f"Bearer {self.config.api_key}",
                            "Content-Type": "application/json"
                        }

                        payload = {
                            "model": self.config.model,
                            "messages": [
                                {
                                    "role": "system",
                                    "content": "You are a travel expert with real-time web access. Provide accurate, current information in the requested JSON format."
                                },
                                {
                                    "role": "user",
                                    "content": prompt
                                }
                            ],
                            "temperature": self.config.temperature,
                            "max_tokens": self.config.max_tokens
                        }

                        async with session.post("https://api.perplexity.ai/chat/completions",
                                               json=payload, headers=headers) as response:
                            if response.status == 200:
                                data = await response.json()
                                content = data["choices"][0]["message"]["content"]
                                self._record_success()
                                return content
                            else:
                                error_text = await response.text()
                                logger.warning(f"Perplexity API error {response.status}: {error_text}")
                                
                                # Return error response for non-retryable errors
                                if response.status in [401, 403, 429]:
                                    self._record_failure()
                                    raise Exception(f"API error {response.status}: {error_text}")

                except asyncio.TimeoutError:
                    logger.warning(f"Perplexity timeout (attempt {attempt + 1}/{self.config.retry_attempts})")
                except aiohttp.ClientError as e:
                    logger.warning(f"Perplexity client error (attempt {attempt + 1}): {e}")
                except Exception as e:
                    logger.warning(f"Perplexity error (attempt {attempt + 1}): {e}")
                    if "401" in str(e) or "403" in str(e) or "429" in str(e):
                        self._record_failure()
                        raise e

                if attempt < self.config.retry_attempts - 1:
                    await asyncio.sleep(self.config.retry_delay * (attempt + 1))

            self._record_failure()
            raise Exception(f"Failed after {self.config.retry_attempts} attempts")

    async def _parse_json_response(self, response: str, data_type: str) -> Any:
        """Parse JSON response with fallback to LLM parsing"""
        try:
            # Try direct JSON parsing first
            json_start = response.find('[') if data_type != "practical_info" else response.find('{')
            json_end = response.rfind(']') + 1 if data_type != "practical_info" else response.rfind('}') + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass

        # Fallback to LLM parsing if available
        if self.openai_client:
            try:
                parse_prompt = f"""Extract {data_type} information from this text and return ONLY valid JSON:

{response}

Return only the JSON, no markdown, no explanations."""

                llm_response = await self.openai_client.chat.completions.create(
                    model=os.getenv("PRIMARY_MODEL", "xai/grok-4-fast-free"),
                    messages=[
                        {"role": "system", "content": f"Extract {data_type} data as JSON."},
                        {"role": "user", "content": parse_prompt}
                    ],
                    temperature=0.1,
                    max_tokens=2000
                )

                content = llm_response.choices[0].message.content
                return json.loads(content)
            except Exception as e:
                logger.warning(f"LLM parsing failed for {data_type}: {e}")

        # Return empty structure as fallback
        return [] if data_type != "practical_info" else {}

    def _get_cached_data(self, cache_key: str) -> Optional[Dict]:
        """Get cached data if still valid"""
        if cache_key not in self._cache:
            return None

        # Check if cache is still valid (24 hours)
        cache_time = self._cache_timestamps.get(cache_key)
        if cache_time and datetime.now() - cache_time < timedelta(hours=24):
            logger.info(f"Using cached data for {cache_key}")
            return self._cache[cache_key]

        # Remove expired cache
        self._cache.pop(cache_key, None)
        self._cache_timestamps.pop(cache_key, None)
        return None

    def _cache_data(self, cache_key: str, data: Dict) -> None:
        """Cache data with timestamp"""
        self._cache[cache_key] = data
        self._cache_timestamps[cache_key] = datetime.now()
        logger.info(f"Cached data for {cache_key}")

    def _create_error_response(self, error_message: str) -> Dict:
        """Create standardized error response"""
        return {
            "error": error_message,
            "restaurants": [],
            "attractions": [],
            "events": [],
            "practical_info": {},
            "daily_suggestions": [],
            "generated_at": datetime.now().isoformat()
        }
