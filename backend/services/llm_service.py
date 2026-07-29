import json
import logging
from openai import AsyncOpenAI
from backend.config import settings
from backend.prompts.system_prompts import SYSTEM_PROMPTS
from backend.prompts.extraction_prompts import EXTRACTION_SYSTEM_PROMPT, RETRY_PROMPT_TEMPLATE
from backend.models.schemas import InvoiceData

logger = logging.getLogger("uvicorn")

class LLMService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL,
            default_headers={
                "HTTP-Referer": "https://localhost:3000",
                "X-Title": "Smart Extractor Chat"
            }
        )

    async def stream_chat(self, messages, system_prompt_key, custom_prompt, temperature):
        # Determine active system prompt
        system_content = custom_prompt if custom_prompt else SYSTEM_PROMPTS.get(system_prompt_key, SYSTEM_PROMPTS["AI Tech Mentor"])
        
        full_messages = [{"role": "system", "content": system_content}]
        for m in messages:
            full_messages.append({"role": m.role, "content": m.content})

        response = await self.client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=full_messages,
            temperature=temperature,
            stream=True
        )

        async for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def extract_invoice(self, raw_text: str, max_retries: int = 3) -> dict:
        messages = [
            {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
            {"role": "user", "content": f"Extract structured invoice JSON from this text:\n\n{raw_text}"}
        ]

        prompt_tokens = 0
        completion_tokens = 0
        last_error = ""
        last_raw_response = ""

        for attempt in range(1, max_retries + 1):
            try:
                response = await self.client.chat.completions.create(
                    model=settings.MODEL_NAME,
                    messages=messages,
                    temperature=0.0
                )

                if response.usage:
                    prompt_tokens += response.usage.prompt_tokens or 0
                    completion_tokens += response.usage.completion_tokens or 0

                content = response.choices[0].message.content.strip()
                last_raw_response = content

                # Clean markdown codeblocks if model hallucinated them
                if content.startswith("```"):
                    content = content.replace("```json", "").replace("```", "").strip()

                parsed_json = json.loads(content)
                validated_data = InvoiceData.model_validate(parsed_json)

                # Cost estimation for typical OpenRouter free/budget models ($0.15/1M in, $0.60/1M out approx)
                est_cost = (prompt_tokens * 0.00000015) + (completion_tokens * 0.00000060)

                return {
                    "success": True,
                    "data": validated_data,
                    "attempts": attempt,
                    "tokens_used": {
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "total_tokens": prompt_tokens + completion_tokens
                    },
                    "estimated_cost": round(est_cost, 6),
                    "error": None
                }

            except (json.JSONDecodeError, Exception) as e:
                last_error = str(e)
                logger.warning(f"Extraction attempt {attempt} failed: {last_error}")
                
                # Feedback loop: append error context to message log for retry
                messages.append({"role": "assistant", "content": last_raw_response})
                retry_msg = RETRY_PROMPT_TEMPLATE.format(
                    error_details=last_error,
                    previous_output=last_raw_response
                )
                messages.append({"role": "user", "content": retry_msg})

        est_cost = (prompt_tokens * 0.00000015) + (completion_tokens * 0.00000060)
        return {
            "success": False,
            "data": None,
            "attempts": max_retries,
            "tokens_used": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens
            },
            "estimated_cost": round(est_cost, 6),
            "error": f"Failed after {max_retries} retries. Last error: {last_error}"
        }

llm_service = LLMService()