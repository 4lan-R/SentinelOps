"""
AI Incident Analyzer Service

Uses LLM APIs to analyze incidents and provide intelligent insights.
"""

import logging
import os
from typing import Any, Dict, List, Optional
from google import genai
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class AnalysisResult(BaseModel):
    """Structured output from incident analysis"""
    possible_causes: List[str]
    recommended_actions: List[str]
    confidence_score: float  # 0.0 to 1.0
    severity_assessment: str  # low, medium, high, critical


class AIIncidentAnalyzer:
    """AI-powered incident analysis using LLM"""

    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "gemini").lower()

        if self.provider == "gemini":
            self.model_name = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
            self.client = genai.Client()
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def analyze_incident(self, logs: str, metrics: Dict[str, Any]) -> AnalysisResult:
        """
        Analyze incident using logs and metrics data.

        Args:
            logs: Raw log data as string
            metrics: Dictionary of current metrics

        Returns:
            AnalysisResult with possible causes, actions, confidence, and severity
        """
        # Create structured prompt for analysis
        prompt = self._build_analysis_prompt(logs, metrics)

        try:
            response_text = self._call_model(prompt)
            return self._parse_analysis_response(response_text)
        except Exception:
            logger.exception("AI incident analysis failed")
            raise

    def _call_model(self, prompt: str) -> str:
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return self._extract_response_text(response)
        except Exception as exc:
            logger.exception("LLM request failed")
            raise RuntimeError("LLM request failed") from exc

    def _extract_response_text(self, response: Any) -> str:
        if hasattr(response, "output_text") and response.output_text:
            return response.output_text

        if hasattr(response, "output"):
            output = response.output
            if isinstance(output, str):
                return output
            if isinstance(output, list):
                pieces: List[str] = []
                for item in output:
                    if isinstance(item, str):
                        pieces.append(item)
                    elif isinstance(item, dict):
                        content = item.get("content")
                        if isinstance(content, str):
                            pieces.append(content)
                        elif isinstance(content, list):
                            pieces.extend(str(part) for part in content)
                return " ".join(pieces)

        if hasattr(response, "choices"):
            for choice in getattr(response, "choices", []):
                if hasattr(choice, "message") and getattr(choice.message, "content", None):
                    return choice.message.content
                if hasattr(choice, "text"):
                    return choice.text
                if isinstance(choice, dict):
                    message = choice.get("message")
                    if isinstance(message, dict) and message.get("content"):
                        return message["content"]
                    if choice.get("text"):
                        return choice["text"]

        return str(response)

    def _build_analysis_prompt(self, logs: str, metrics: Dict[str, Any]) -> str:
        """Build a structured prompt for incident analysis"""

        # Format metrics for the prompt
        metrics_str = "\n".join([f"- {key}: {value}" for key, value in metrics.items()])

        # Extract key patterns from logs (simplified)
        log_patterns = self._extract_log_patterns(logs)

        prompt = f"""
INCIDENT ANALYSIS REQUEST

METRICS:
{metrics_str}

LOG PATTERNS:
{log_patterns}

LOGS:
{logs[:2000]}  # Truncate for token limits

Please analyze this incident and provide:
1. Possible root causes (list 2-4 most likely causes)
2. Recommended immediate actions (list 3-5 actionable steps)
3. Confidence score (0.0-1.0) in your analysis
4. Severity assessment (low/medium/high/critical)

Focus on common infrastructure issues like:
- Resource exhaustion (CPU, memory, disk)
- Network connectivity problems
- Database connection issues
- Cache/Redis problems
- API rate limiting or failures
- Configuration errors
- Dependency failures
"""

        return prompt

    def _extract_log_patterns(self, logs: str) -> str:
        """Extract common error patterns from logs"""
        patterns = []

        # Common error patterns
        error_indicators = [
            "timeout", "connection refused", "connection reset", "500", "502", "503", "504",
            "out of memory", "cpu overload", "disk full", "permission denied",
            "redis connection", "database connection", "api failure"
        ]

        logs_lower = logs.lower()
        for indicator in error_indicators:
            if indicator in logs_lower:
                patterns.append(f"- Contains '{indicator}' errors")

        if not patterns:
            patterns.append("- No specific error patterns detected")

        return "\n".join(patterns)

    def _parse_analysis_response(self, response_text: str) -> AnalysisResult:
        """Parse LLM response into structured AnalysisResult"""

        # Simple parsing - in production, use more robust parsing
        lines = response_text.strip().split('\n')

        possible_causes = []
        recommended_actions = []
        confidence_score = 0.7  # Default
        severity_assessment = "medium"  # Default

        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect sections
            if "possible" in line.lower() and "cause" in line.lower():
                current_section = "causes"
                continue
            elif "recommend" in line.lower() and "action" in line.lower():
                current_section = "actions"
                continue
            elif "confidence" in line.lower():
                # Extract confidence score
                import re
                match = re.search(r'(\d+\.?\d*)', line)
                if match:
                    confidence_score = min(float(match.group(1)), 1.0)
                continue
            elif "severity" in line.lower():
                # Extract severity
                if "critical" in line.lower():
                    severity_assessment = "critical"
                elif "high" in line.lower():
                    severity_assessment = "high"
                elif "low" in line.lower():
                    severity_assessment = "low"
                else:
                    severity_assessment = "medium"
                continue

            # Add to current section
            if current_section == "causes" and line.startswith(('-', '•', '*')):
                possible_causes.append(line.lstrip('-•* ').strip())
            elif current_section == "actions" and line.startswith(('-', '•', '*')):
                recommended_actions.append(line.lstrip('-•* ').strip())

        # Ensure we have at least some content
        if not possible_causes:
            possible_causes = ["Unable to determine specific cause from available data"]
        if not recommended_actions:
            recommended_actions = ["Monitor the system closely", "Check system resources", "Review recent changes"]

        return AnalysisResult(
            possible_causes=possible_causes,
            recommended_actions=recommended_actions,
            confidence_score=confidence_score,
            severity_assessment=severity_assessment
        )

    def _fallback_analysis(self, logs: str, metrics: Dict[str, Any]) -> AnalysisResult:
        """Fallback analysis when LLM is unavailable"""

        possible_causes = []
        recommended_actions = []

        # Simple rule-based analysis
        logs_lower = logs.lower()

        if "redis" in logs_lower and ("timeout" in logs_lower or "connection" in logs_lower):
            possible_causes.append("Redis connection timeout or overload")
            recommended_actions.extend([
                "Check Redis server status and resource usage",
                "Verify Redis connection pool configuration",
                "Consider increasing Redis timeout settings"
            ])

        if "500" in logs_lower or "error" in logs_lower:
            possible_causes.append("Application server errors")
            recommended_actions.extend([
                "Check application logs for stack traces",
                "Verify database connectivity",
                "Check for recent deployments or configuration changes"
            ])

        # Check metrics
        if metrics.get("cpu_usage", 0) > 90:
            possible_causes.append("High CPU utilization")
            recommended_actions.append("Scale up CPU resources or optimize CPU-intensive processes")

        if metrics.get("memory_usage", 0) > 85:
            possible_causes.append("Memory pressure or leak")
            recommended_actions.append("Check for memory leaks and consider increasing memory allocation")

        if not possible_causes:
            possible_causes = ["Unknown issue - requires manual investigation"]
            recommended_actions = ["Gather more detailed logs", "Check system monitoring dashboards"]

        return AnalysisResult(
            possible_causes=possible_causes,
            recommended_actions=recommended_actions,
            confidence_score=0.5,
            severity_assessment="medium"
        )