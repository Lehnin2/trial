"""
LLM Manager - Handles multiple LLM providers with fallback
Supports: TokenFactory (primary) and Gemini (fallback)
Includes token usage tracking, rate limit handling, and chunking for large prompts
"""

import os
import httpx
import time
from openai import OpenAI
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Try to import logger, fallback to print if not available
try:
    from logger_config import logger
except ImportError:
    class SimpleLogger:
        def info(self, msg): print(f"ℹ️  {msg}")
        def warning(self, msg): print(f"⚠️  {msg}")
        def error(self, msg): print(f"❌ {msg}")
    logger = SimpleLogger()


# Constants for rate limiting and chunking
GEMINI_RPM_LIMIT = 15  # Requests per minute for free tier
GEMINI_TPM_LIMIT = 1000000  # Tokens per minute (1M for free tier)
CHUNK_SIZE_TOKENS = 25000  # Max tokens per chunk to stay safe
TOKENFACTORY_TIMEOUT = 45  # Seconds before timeout
TOKENFACTORY_MAX_RETRIES = 2  # Max retries before fallback


class LLMManager:
    """Manages LLM calls with automatic fallback between TokenFactory and Gemini"""
    
    def __init__(self):
        self.tokenfactory_key = os.environ.get('TOKENFACTORY_API_KEY', '')
        self.gemini_key = os.environ.get('GEMINI_API_KEY', '')
        self.current_provider = None
        self.last_error = None
        self.tokenfactory_failures = 0  # Track consecutive failures
        self.skip_tokenfactory = False  # Skip if too many failures
        
        # Token usage tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.call_count = 0
        self.gemini_calls_this_minute = 0
        self.gemini_tokens_this_minute = 0
        self.last_minute_reset = datetime.now()

    def get_available_providers(self) -> list:
        """Get list of available providers based on API keys"""
        providers = []
        if self.tokenfactory_key:
            providers.append('TokenFactory')
        if self.gemini_key:
            providers.append('Gemini')
        return providers
    
    def get_current_provider(self) -> str:
        """Get the name of the current provider being used"""
        return self.current_provider or 'None'
    
    def get_token_usage(self) -> dict:
        """Get current token usage statistics"""
        return {
            'total_input_tokens': self.total_input_tokens,
            'total_output_tokens': self.total_output_tokens,
            'total_tokens': self.total_input_tokens + self.total_output_tokens,
            'call_count': self.call_count,
            'gemini_calls_this_minute': self.gemini_calls_this_minute,
            'current_provider': self.current_provider
        }
    
    def print_status(self, action: str = ""):
        """Print current status and token usage"""
        usage = self.get_token_usage()
        print(f"\n{'='*60}")
        print(f"🤖 LLM STATUS {f'- {action}' if action else ''}")
        print(f"{'='*60}")
        print(f"   Provider: {usage['current_provider'] or 'Not set'}")
        print(f"   Total Calls: {usage['call_count']}")
        print(f"   Input Tokens: {usage['total_input_tokens']:,}")
        print(f"   Output Tokens: {usage['total_output_tokens']:,}")
        print(f"   Total Tokens: {usage['total_tokens']:,}")
        if self.current_provider == 'Gemini':
            print(f"   Gemini calls this minute: {usage['gemini_calls_this_minute']}/15 (rate limit)")
        print(f"{'='*60}\n")
        
    def call_llm(self, system_prompt: str, user_prompt: str, 
                 temperature: float = 0.3, max_tokens: int = 8000) -> Optional[str]:
        """Call LLM with automatic fallback and chunking support"""
        self.call_count += 1
        
        # Estimate input tokens
        estimated_input = self._estimate_tokens(system_prompt + user_prompt)
        
        print(f"\n📡 LLM Call #{self.call_count}")
        print(f"   Estimated input: ~{estimated_input:,} tokens")
        
        # Check if prompt is too large and needs chunking
        if estimated_input > CHUNK_SIZE_TOKENS:
            print(f"   ⚠️ Large prompt detected, using chunked processing...")
            return self._call_llm_chunked(system_prompt, user_prompt, temperature, max_tokens)
        
        # Try TokenFactory first (unless we've had too many failures)
        if self.tokenfactory_key and not self.skip_tokenfactory:
            print(f"   Trying TokenFactory...")
            result = self._call_tokenfactory(system_prompt, user_prompt, temperature, max_tokens)
            if result:
                self.current_provider = 'TokenFactory'
                self.total_input_tokens += estimated_input
                self.total_output_tokens += len(result) // 4
                self.tokenfactory_failures = 0  # Reset failure counter
                print(f"   ✅ TokenFactory responded ({len(result):,} chars)")
                return result
            
            # Track failures
            self.tokenfactory_failures += 1
            if self.tokenfactory_failures >= 3:
                print(f"   ⚠️ TokenFactory failed {self.tokenfactory_failures} times, skipping for this session")
                self.skip_tokenfactory = True
            print(f"   ⚠️ TokenFactory failed, trying Gemini...")
        
        # Fallback to Gemini
        if self.gemini_key:
            # Check and handle rate limits
            self._check_gemini_rate_limit(estimated_input)
            
            print(f"   Trying Gemini (calls: {self.gemini_calls_this_minute}/{GEMINI_RPM_LIMIT}, tokens: {self.gemini_tokens_this_minute:,})...")
            result = self._call_gemini(system_prompt, user_prompt, temperature, max_tokens)
            if result:
                self.current_provider = 'Gemini'
                self.total_input_tokens += estimated_input
                output_tokens = len(result) // 4
                self.total_output_tokens += output_tokens
                self.gemini_calls_this_minute += 1
                self.gemini_tokens_this_minute += estimated_input + output_tokens
                print(f"   ✅ Gemini responded ({len(result):,} chars)")
                return result
        
        print(f"   ❌ All providers failed")
        logger.error("All LLM providers failed")
        return None
    
    def _call_llm_chunked(self, system_prompt: str, user_prompt: str,
                          temperature: float = 0.3, max_tokens: int = 8000) -> Optional[str]:
        """Process large prompts by chunking the user prompt"""
        chunks = self._chunk_text(user_prompt)
        print(f"   📦 Split into {len(chunks)} chunks")
        
        all_results = []
        
        for i, chunk in enumerate(chunks):
            print(f"\n   Processing chunk {i+1}/{len(chunks)} ({len(chunk):,} chars)...")
            
            # Modify system prompt to indicate this is a chunk
            chunk_system = system_prompt
            if len(chunks) > 1:
                chunk_system += f"\n\nNote: This is part {i+1} of {len(chunks)} of a larger document. Analyze this section."
            
            result = self._call_single_chunk(chunk_system, chunk, temperature, max_tokens)
            if result:
                all_results.append(result)
            else:
                print(f"   ⚠️ Chunk {i+1} failed")
            
            # Add delay between chunks to avoid rate limits
            if i < len(chunks) - 1:
                time.sleep(2)
        
        if not all_results:
            return None
        
        # Combine results
        if len(all_results) == 1:
            return all_results[0]
        
        # For multiple chunks, combine the JSON results
        return self._combine_chunk_results(all_results)
    
    def _call_single_chunk(self, system_prompt: str, user_prompt: str,
                           temperature: float, max_tokens: int) -> Optional[str]:
        """Call LLM for a single chunk"""
        estimated_input = self._estimate_tokens(system_prompt + user_prompt)
        
        # Try TokenFactory first
        if self.tokenfactory_key and not self.skip_tokenfactory:
            result = self._call_tokenfactory(system_prompt, user_prompt, temperature, max_tokens)
            if result:
                self.current_provider = 'TokenFactory'
                self.total_input_tokens += estimated_input
                self.total_output_tokens += len(result) // 4
                return result
        
        # Fallback to Gemini
        if self.gemini_key:
            self._check_gemini_rate_limit(estimated_input)
            result = self._call_gemini(system_prompt, user_prompt, temperature, max_tokens)
            if result:
                self.current_provider = 'Gemini'
                self.total_input_tokens += estimated_input
                output_tokens = len(result) // 4
                self.total_output_tokens += output_tokens
                self.gemini_calls_this_minute += 1
                self.gemini_tokens_this_minute += estimated_input + output_tokens
                return result
        
        return None
    
    def _combine_chunk_results(self, results: List[str]) -> str:
        """Combine results from multiple chunks"""
        # Try to parse as JSON and merge
        import json
        
        combined_violations = []
        
        for result in results:
            try:
                # Try to extract JSON from result
                if '{' in result:
                    start = result.find('{')
                    end = result.rfind('}') + 1
                    json_str = result[start:end]
                    data = json.loads(json_str)
                    
                    # Extract violations if present
                    if isinstance(data, dict):
                        if 'violations' in data:
                            combined_violations.extend(data['violations'])
                        elif 'all_violations' in data:
                            combined_violations.extend(data['all_violations'])
                    elif isinstance(data, list):
                        combined_violations.extend(data)
            except:
                # If not JSON, just append the text
                combined_violations.append({"raw_result": result})
        
        # Return combined result
        return json.dumps({
            "violations": combined_violations,
            "chunk_count": len(results)
        }, indent=2)
    
    def _check_gemini_rate_limit(self, estimated_tokens: int = 0):
        """Check and handle Gemini rate limits"""
        now = datetime.now()
        seconds_elapsed = (now - self.last_minute_reset).seconds
        
        # Reset counters if a minute has passed
        if seconds_elapsed >= 60:
            self.gemini_calls_this_minute = 0
            self.gemini_tokens_this_minute = 0
            self.last_minute_reset = now
            print(f"   📊 Gemini rate limit reset")
            return True
        
        # Check if we're approaching rate limits
        if self.gemini_calls_this_minute >= GEMINI_RPM_LIMIT - 1:
            wait_time = 60 - seconds_elapsed + 2  # Wait until next minute + buffer
            print(f"   ⏳ Rate limit approaching, waiting {wait_time}s...")
            time.sleep(wait_time)
            self.gemini_calls_this_minute = 0
            self.gemini_tokens_this_minute = 0
            self.last_minute_reset = datetime.now()
        
        # Check token limit
        if self.gemini_tokens_this_minute + estimated_tokens > GEMINI_TPM_LIMIT * 0.9:
            wait_time = 60 - seconds_elapsed + 2
            print(f"   ⏳ Token limit approaching ({self.gemini_tokens_this_minute:,} tokens), waiting {wait_time}s...")
            time.sleep(wait_time)
            self.gemini_calls_this_minute = 0
            self.gemini_tokens_this_minute = 0
            self.last_minute_reset = datetime.now()
        
        return True
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough: 1 token ≈ 4 chars)"""
        return len(text) // 4
    
    def _chunk_text(self, text: str, max_tokens: int = CHUNK_SIZE_TOKENS) -> List[str]:
        """Split text into chunks that fit within token limits"""
        max_chars = max_tokens * 4  # Convert tokens to chars
        
        if len(text) <= max_chars:
            return [text]
        
        chunks = []
        # Try to split on paragraph boundaries
        paragraphs = text.split('\n\n')
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) + 2 <= max_chars:
                current_chunk += para + '\n\n'
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                # If single paragraph is too long, split by sentences
                if len(para) > max_chars:
                    sentences = para.replace('. ', '.\n').split('\n')
                    current_chunk = ""
                    for sent in sentences:
                        if len(current_chunk) + len(sent) + 1 <= max_chars:
                            current_chunk += sent + ' '
                        else:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                            current_chunk = sent + ' '
                else:
                    current_chunk = para + '\n\n'
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks if chunks else [text[:max_chars]]

    def _call_tokenfactory(self, system_prompt: str, user_prompt: str,
                           temperature: float = 0.3, max_tokens: int = 8000) -> Optional[str]:
        """Call TokenFactory API with retry logic"""
        for attempt in range(TOKENFACTORY_MAX_RETRIES):
            try:
                # Use longer timeout for TokenFactory
                http_client = httpx.Client(
                    verify=False, 
                    timeout=httpx.Timeout(TOKENFACTORY_TIMEOUT, connect=10.0)
                )
                client = OpenAI(
                    api_key=self.tokenfactory_key,
                    base_url="https://tokenfactory.esprit.tn/api",
                    http_client=http_client
                )
                
                response = client.chat.completions.create(
                    model="hosted_vllm/Llama-3.1-70B-Instruct",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=0.9,
                    frequency_penalty=0.0,
                    presence_penalty=0.0
                )
                
                result = response.choices[0].message.content
                
                # Check if response contains blocked page error (TokenFactory firewall)
                if result and ('Web Page Blocked' in result or 'page_title' in result or 'attack_ID' in result):
                    logger.warning(f"TokenFactory returned blocked page response, falling back to Gemini")
                    self.last_error = "TokenFactory blocked - firewall issue"
                    return None
                
                return result
                
            except Exception as e:
                error_str = str(e).lower()
                self.last_error = str(e)
                
                # Check for specific error types
                is_timeout = 'timeout' in error_str or 'timed out' in error_str
                is_connection = 'connection' in error_str or 'connect' in error_str
                is_blocked = 'web page blocked' in error_str or 'attack_id' in error_str or 'blocked' in error_str
                
                if is_blocked:
                    logger.warning(f"TokenFactory blocked by firewall, falling back to Gemini")
                    return None  # Don't retry for firewall blocks
                
                if is_timeout or is_connection:
                    if attempt < TOKENFACTORY_MAX_RETRIES - 1:
                        wait_time = (attempt + 1) * 5  # Exponential backoff
                        print(f"   ⏳ TokenFactory timeout/connection error, retrying in {wait_time}s (attempt {attempt + 2}/{TOKENFACTORY_MAX_RETRIES})...")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"TokenFactory API error after {TOKENFACTORY_MAX_RETRIES} attempts: {e}")
                else:
                    logger.error(f"TokenFactory API error: {e}")
                
                return None
        
        return None
    
    def _call_gemini(self, system_prompt: str, user_prompt: str,
                     temperature: float = 0.3, max_tokens: int = 8000) -> Optional[str]:
        """Call Gemini API as fallback with rate limit handling"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                import google.generativeai as genai
                
                genai.configure(api_key=self.gemini_key)
                
                model = genai.GenerativeModel(
                    model_name="gemini-2.0-flash",
                    system_instruction=system_prompt
                )
                
                response = model.generate_content(
                    user_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=temperature,
                        max_output_tokens=max_tokens
                    )
                )
                
                # Try to get actual token usage from response
                if hasattr(response, 'usage_metadata'):
                    usage = response.usage_metadata
                    if hasattr(usage, 'prompt_token_count'):
                        actual_input = usage.prompt_token_count
                        actual_output = usage.candidates_token_count if hasattr(usage, 'candidates_token_count') else 0
                        print(f"   📊 Gemini actual tokens - Input: {actual_input:,}, Output: {actual_output:,}")
                        # Update actual token counts
                        self.gemini_tokens_this_minute += actual_input + actual_output
                
                return response.text
                
            except Exception as e:
                self.last_error = str(e)
                error_str = str(e).lower()
                
                # Check for rate limit errors
                is_rate_limit = 'quota' in error_str or 'rate' in error_str or '429' in error_str or 'resource_exhausted' in error_str
                
                if is_rate_limit:
                    if attempt < max_retries - 1:
                        wait_time = 60 + (attempt * 10)  # Wait 60s, 70s, 80s
                        print(f"   ⚠️ Rate limit hit! Waiting {wait_time}s before retry (attempt {attempt + 2}/{max_retries})...")
                        logger.warning(f"Gemini rate limit hit, waiting {wait_time}s")
                        time.sleep(wait_time)
                        # Reset counters after waiting
                        self.gemini_calls_this_minute = 0
                        self.gemini_tokens_this_minute = 0
                        self.last_minute_reset = datetime.now()
                        continue
                    else:
                        print(f"   ❌ Rate limit persists after {max_retries} attempts")
                        logger.error(f"Gemini rate limit persists: {e}")
                else:
                    logger.error(f"Gemini API error: {e}")
                
                return None
        
        return None


# Singleton instance for easy import
llm_manager = LLMManager()


def get_llm_client():
    """Factory function to get an LLM client wrapper"""
    return llm_manager
