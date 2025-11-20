import os
import json
from typing import Dict, Any
import aiohttp
from src.gpt_interfaces.gpt_interface import GPTInterface


class GeminiGPT(GPTInterface):
    """Google Gemini LLM provider for high-quality creative content generation.

    Gemini excels at:
    - Creative, magazine-quality writing
    - Rich, detailed descriptions
    - Cultural and contextual understanding
    - Long-form content generation
    """

    def __init__(self, api_key: str = None, model: str = None):
        """Initialize Gemini provider.

        Args:
            api_key: Google AI API key (or uses GOOGLE_API_KEY env var)
            model: Model to use. Options:
                - gemini-3-pro-preview (LATEST: best for complex tasks, broad knowledge)
                - gemini-2.0-flash-exp (fast, high quality, experimental)
                - gemini-2.0-flash-thinking-exp (advanced reasoning)
                - gemini-1.5-pro-latest (production stable)
                - gemini-1.5-flash-latest (fast, efficient)

        Gemini 3 Pro features:
            - 1M token context / 64K output
            - Knowledge cutoff: January 2025
            - Advanced reasoning across modalities
            - Note: Less verbose by default - prompts should explicitly request creative/literary style
        """
        if api_key is None:
            api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')

        if model is None:
            # Check for model in environment, default to Gemini 3 Pro Preview
            model = os.getenv('GEMINI_MODEL', 'gemini-3-pro-preview')

        if not api_key:
            raise ValueError("Gemini API key not found. Set GOOGLE_API_KEY or GEMINI_API_KEY")

        self.api_key = api_key
        self.model = model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    def generate_text(self, prompt: str, system: str | None = None) -> Dict[str, Any]:
        """Synchronous wrapper for async generation (for backward compatibility)."""
        import asyncio
        return asyncio.run(self.generate_text_async(prompt, system))

    async def generate_text_async(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.8,
        max_tokens: int = 8192
    ) -> Dict[str, Any]:
        """Generate text using Gemini API.

        Args:
            prompt: User prompt
            system: System instructions (Gemini uses this to set behavior)
            temperature: 0.0-2.0, higher = more creative (default 0.8 for magazine quality)
            max_tokens: Maximum output tokens

        Returns:
            Dict with 'content' key containing generated text
        """
        try:
            url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"

            # Build the request payload
            contents = []

            # Gemini 2.0 supports system instructions
            system_instruction = None
            if system:
                system_instruction = {"parts": [{"text": system}]}

            # Add user prompt
            contents.append({
                "role": "user",
                "parts": [{"text": prompt}]
            })

            payload = {
                "contents": contents,
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens,
                    "topP": 0.95,
                    "topK": 40
                }
            }

            # Add system instruction if provided
            if system_instruction:
                payload["systemInstruction"] = system_instruction

            # Make async API call
            timeout = aiohttp.ClientTimeout(total=120)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Gemini API error {response.status}: {error_text}")

                    data = await response.json()

                    # Extract text from response
                    if "candidates" in data and len(data["candidates"]) > 0:
                        candidate = data["candidates"][0]
                        if "content" in candidate and "parts" in candidate["content"]:
                            text = candidate["content"]["parts"][0]["text"]

                            return {
                                "content": text,
                                "model": self.model,
                                "finish_reason": candidate.get("finishReason", "STOP")
                            }

                    raise Exception(f"Unexpected Gemini API response structure: {data}")

        except Exception as e:
            print(f"[ERROR] Gemini generation failed: {str(e)}")
            return {
                "content": "",
                "error": str(e)
            }

    async def generate_json(
        self,
        prompt: str,
        system: str | None = None,
        schema: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        """Generate structured JSON output.

        Args:
            prompt: User prompt requesting JSON output
            system: System instructions
            schema: Optional JSON schema for validation

        Returns:
            Parsed JSON dict
        """
        # Add JSON instruction to system prompt
        json_system = (system or "") + "\n\nYou MUST respond with valid JSON only. No markdown, no explanations."

        result = await self.generate_text_async(prompt, system=json_system, temperature=0.4)

        if "error" in result:
            return result

        try:
            # Try to parse JSON from response
            content = result["content"].strip()

            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]

            if content.endswith("```"):
                content = content[:-3]

            content = content.strip()

            return json.loads(content)

        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to parse JSON from Gemini: {e}")
            print(f"[DEBUG] Raw content: {result['content'][:500]}")
            return {
                "error": "Failed to parse JSON from Gemini response",
                "raw_content": result["content"]
            }
