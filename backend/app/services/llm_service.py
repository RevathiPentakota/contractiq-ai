"""LLM service – reusable interface to LiteLLM Proxy.

All LLM HTTP communication is encapsulated here.  Agents must never
call LiteLLM (or any LLM provider) directly; they delegate to this
service so that model configuration, retries, and error handling live
in one place.

LiteLLM Proxy exposes an OpenAI-compatible REST API, so we call it
with httpx using the standard ``/chat/completions`` endpoint.
"""

from __future__ import annotations

import json
from typing import Any

import httpx
from loguru import logger

from app.core.config import get_settings

# ── Prompt constants ───────────────────────────────────────────────────────────

_SUMMARY_SYSTEM_PROMPT = (
    "You are an expert legal contract analyst. "
    "Generate a concise executive summary highlighting the purpose of the "
    "agreement, parties involved, important dates, obligations, and key "
    "commercial terms. "
    "The summary should be 200–300 words, written in plain business English "
    "suitable for a non-legal audience. "
    "Do not include legal opinions or advice."
)

_SUMMARY_USER_TEMPLATE = (
    "Please summarise the following contract text:\n\n"
    "---\n"
    "{contract_text}\n"
    "---"
)

_RISK_SYSTEM_PROMPT = """
You are a senior legal contract risk analyst.

Review the contract and identify ALL legal, financial, commercial,
operational, compliance, payment, liability, termination,
intellectual property, confidentiality and data privacy risks.

A risk includes (but is not limited to):
- Unlimited liability
- Missing limitation of liability
- Weak confidentiality
- Short termination notice
- Missing SLA penalties
- Ambiguous payment terms
- Automatic renewal
- Broad IP assignment
- Regulatory compliance issues
- Weak data protection
- One-sided obligations
- Indemnification issues

Return ONLY valid JSON.
Do not return markdown.
Do not explain your reasoning.

If there are no risks, return an empty JSON array.

Each risk must include:
- category
- severity
- title
- description
- clause_reference
- recommendation

Example:

[
  {
    "category": "Legal",
    "severity": "High",
    "title": "Unlimited Liability",
    "description": "The agreement contains an unlimited liability clause.",
    "clause_reference": "Section 7",
    "recommendation": "Limit liability to fees paid under the agreement."
  }
]
"""
_RISK_USER_TEMPLATE = (
    "Please analyse the following contract for risks and return the results as JSON:\n\n"
    "---\n"
    "{contract_text}\n"
    "---"
)

_CLAUSE_SYSTEM_PROMPT = (
    "You are an expert legal contract analyst. "
    "Extract the important clauses from the contract. "
    "Return ONLY valid JSON. Do not return markdown. Do not explain your reasoning. "
    "If there are no clauses return an empty JSON array. "
    "Each clause must include: title, category, clause_reference, description, importance."
)

_CLAUSE_USER_TEMPLATE = (
    "Please extract the important clauses from the following contract and return the results as JSON:\n\n"
    "---\n"
    "{contract_text}\n"
    "---"
)


class LLMService:
    """HTTP client for the LiteLLM Proxy (OpenAI-compatible API).

    The service is stateless — create one instance per request or share
    a singleton, as preferred.  All configuration is read from
    ``Settings`` at call time so environment changes are respected.

    Raises:
        httpx.HTTPStatusError: On non-2xx responses from the proxy.
        httpx.TimeoutException: When the request exceeds ``llm_timeout_seconds``.
        httpx.RequestError: On network-level failures.
    """

    def generate_summary(self, contract_text: str) -> str:
        """Generate a concise executive summary of a contract.

        Sends the contract text to the LiteLLM Proxy using a pre-defined
        legal analyst system prompt.

        Args:
            contract_text: Full extracted plain text of the contract.
                           Should be non-empty; empty text raises ``ValueError``.

        Returns:
            Plain-text executive summary (200–300 words).

        Raises:
            ValueError: If ``contract_text`` is empty.
            httpx.HTTPStatusError: On HTTP 4xx/5xx from the proxy.
            httpx.TimeoutException: If the proxy exceeds the timeout.
            Exception: On any other unexpected error.
        """
        if not contract_text or not contract_text.strip():
            raise ValueError("contract_text must not be empty.")

        settings = get_settings()

        logger.info(
            "[LLMService] Requesting summary | model={model} | "
            "text_length={length} chars",
            model=settings.llm_model,
            length=len(contract_text),
        )

        payload = {
            "model": settings.llm_model,
            "messages": [
                {"role": "system", "content": _SUMMARY_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": _SUMMARY_USER_TEMPLATE.format(
                        contract_text=contract_text
                    ),
                },
            ],
            "temperature": settings.temperature,
            "max_tokens": settings.max_tokens,
        }

        try:
            with httpx.Client(timeout=settings.llm_timeout_seconds) as client:
                response = client.post(
                    url=f"{settings.llm_base_url.rstrip('/')}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.llm_api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()

        except httpx.HTTPStatusError as err:
            logger.error(
                "[LLMService] HTTP error {status}: {body}",
                status=err.response.status_code,
                body=err.response.text,
            )
            raise
        except httpx.TimeoutException:
            logger.error(
                "[LLMService] Request timed out after {timeout}s",
                timeout=settings.llm_timeout_seconds,
            )
            raise
        except httpx.RequestError as err:
            logger.error(
                "[LLMService] Network error: {error}",
                error=str(err),
            )
            raise

        data = response.json()

        # Extract content from the standard OpenAI-compatible response shape.
        try:
            summary = data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError) as err:
            raise ValueError(
                f"Unexpected LLM response structure: {data}"
            ) from err

        logger.info(
            "[LLMService] Summary received | {words} words",
            words=len(summary.split()),
        )

        return summary

    def generate_risks(self, contract_text: str) -> list[dict[str, Any]]:
        """Analyse a contract and identify legal, financial, and operational risks.

        Sends the contract text to the LiteLLM Proxy using a senior risk
        analyst system prompt. Expects a JSON array in return.

        Args:
            contract_text: Full extracted plain text of the contract.
                           Should be non-empty; empty text raises ``ValueError``.

        Returns:
            List of risk dictionaries, each containing:
            - category: str (e.g. "Financial", "Legal", "Compliance")
            - severity: str ("High", "Medium", "Low")
            - title: str (e.g. "Unlimited Liability")
            - description: str (detailed explanation)
            - clause_reference: str (e.g. "Section 8.2")
            - recommendation: str (suggested remediation)

            Returns an empty list if the LLM identifies no risks.

        Raises:
            ValueError: If ``contract_text`` is empty or LLM response is not valid JSON.
            httpx.HTTPStatusError: On HTTP 4xx/5xx from the proxy.
            httpx.TimeoutException: If the proxy exceeds the timeout.
            Exception: On any other unexpected error.
        """
        if not contract_text or not contract_text.strip():
            raise ValueError("contract_text must not be empty.")

        settings = get_settings()

        logger.info(
            "[LLMService] Requesting risk analysis | model={model} | "
            "text_length={length} chars",
            model=settings.llm_model,
            length=len(contract_text),
        )

        payload = {
            "model": settings.llm_model,
            "messages": [
                {"role": "system", "content": _RISK_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": _RISK_USER_TEMPLATE.format(
                        contract_text=contract_text
                    ),
                },
            ],
            "temperature": settings.temperature,
            "max_tokens": settings.max_tokens,
        }

        try:
            with httpx.Client(timeout=settings.llm_timeout_seconds) as client:
                response = client.post(
                    url=f"{settings.llm_base_url.rstrip('/')}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.llm_api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()

        except httpx.HTTPStatusError as err:
            logger.error(
                "[LLMService] HTTP error {status}: {body}",
                status=err.response.status_code,
                body=err.response.text,
            )
            raise
        except httpx.TimeoutException:
            logger.error(
                "[LLMService] Request timed out after {timeout}s",
                timeout=settings.llm_timeout_seconds,
            )
            raise
        except httpx.RequestError as err:
            logger.error(
                "[LLMService] Network error: {error}",
                error=str(err),
            )
            raise

        data = response.json()

        # Extract content from the standard OpenAI-compatible response shape.
        try:
            raw_response = data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError) as err:
            raise ValueError(
                f"Unexpected LLM response structure: {data}"
            ) from err

        # Parse the JSON response; LLM should return an array of risks.
        try:
            raw_response = raw_response.replace("```json", "")
            raw_response = raw_response.replace("```", "")
            raw_response = raw_response.strip()
            risks = json.loads(raw_response)
        except json.JSONDecodeError as err:
            logger.error(
                "[LLMService] Failed to parse LLM JSON response: {error}",
                error=str(err),
            )
            raise ValueError(
                f"LLM did not return valid JSON: {raw_response[:200]}"
            ) from err

        if not isinstance(risks, list):
            logger.error(
                "[LLMService] LLM returned non-list JSON: {type}",
                type=type(risks).__name__,
            )
            raise ValueError(
                f"Expected JSON array of risks, got {type(risks).__name__}"
            )

        logger.info(
            "[LLMService] Risk analysis complete | {count} risks identified",
            count=len(risks),
        )

        return risks

    def generate_recommendations(
            self,
            summary: str,
            risks: list[dict],
            clauses: list[dict],
        ) -> list[dict[str, Any]]:
            """Generate contract improvement recommendations."""

            settings = get_settings()

            logger.info(
                "[LLMService] Requesting recommendations | model={model}",
                model=settings.llm_model,
            )

            prompt = f"""
        Executive Summary:
        {summary}

        Risks:
        {json.dumps(risks, indent=2)}

        Clauses:
        {json.dumps(clauses, indent=2)}

        Based on the above contract analysis, generate actionable recommendations.

        Return ONLY valid JSON.

        Each recommendation must contain:

        - priority
        - title
        - description
        - reason

        Example:

        [
        {{
            "priority":"High",
            "title":"Limit Liability",
            "description":"Limit liability to fees paid under the agreement.",
            "reason":"Unlimited liability exposes the supplier to excessive financial risk."
        }}
        ]
        """

            payload = {
                "model": settings.llm_model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert legal contract advisor.",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                "temperature": settings.temperature,
                "max_tokens": settings.max_tokens,
            }

            try:
                with httpx.Client(timeout=settings.llm_timeout_seconds) as client:
                    response = client.post(
                        url=f"{settings.llm_base_url.rstrip('/')}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {settings.llm_api_key}",
                            "Content-Type": "application/json",
                        },
                        json=payload,
                    )

                    response.raise_for_status()

            except Exception:
                raise

            data = response.json()

            try:
                raw_response = data["choices"][0]["message"]["content"].strip()
            except (KeyError, IndexError) as err:
                raise ValueError(
                    f"Unexpected LLM response structure: {data}"
                ) from err

            raw_response = raw_response.replace("```json", "")
            raw_response = raw_response.replace("```", "")
            raw_response = raw_response.strip()

            try:
                recommendations = json.loads(raw_response)
            except json.JSONDecodeError as err:
                raise ValueError(
                    f"LLM did not return valid JSON: {raw_response[:200]}"
                ) from err

            logger.info(
                "[LLMService] Recommendation generation complete | {count} recommendations",
                count=len(recommendations),
            )

            return recommendations

    def generate_clauses(self, contract_text: str) -> list[dict[str, Any]]:
        """Extract important clauses from a contract.

        Sends the contract text to the LiteLLM Proxy using a legal analyst
        system prompt. Expects a JSON array in return.

        Args:
            contract_text: Full extracted plain text of the contract.
                           Should be non-empty; empty text raises ``ValueError``.

        Returns:
            List of clause dictionaries, each containing:
            - title: str (e.g. "Indemnification")
            - category: str (e.g. "Liability", "Payment", "Termination")
            - clause_reference: str (e.g. "Section 5.1" or "Clause 3")
            - description: str (detailed explanation or verbatim text)
            - importance: str ("High", "Medium", "Low")

            Returns an empty list if the LLM identifies no clauses.

        Raises:
            ValueError: If ``contract_text`` is empty or LLM response is not valid JSON.
            httpx.HTTPStatusError: On HTTP 4xx/5xx from the proxy.
            httpx.TimeoutException: If the proxy exceeds the timeout.
            Exception: On any other unexpected error.
        """
        if not contract_text or not contract_text.strip():
            raise ValueError("contract_text must not be empty.")

        settings = get_settings()

        logger.info(
            "[LLMService] Requesting clause extraction | model={model} | "
            "text_length={length} chars",
            model=settings.llm_model,
            length=len(contract_text),
        )

        payload = {
            "model": settings.llm_model,
            "messages": [
                {"role": "system", "content": _CLAUSE_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": _CLAUSE_USER_TEMPLATE.format(
                        contract_text=contract_text
                    ),
                },
            ],
            "temperature": settings.temperature,
            "max_tokens": settings.max_tokens,
        }

        try:
            with httpx.Client(timeout=settings.llm_timeout_seconds) as client:
                response = client.post(
                    url=f"{settings.llm_base_url.rstrip('/')}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.llm_api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()

        except httpx.HTTPStatusError as err:
            logger.error(
                "[LLMService] HTTP error {status}: {body}",
                status=err.response.status_code,
                body=err.response.text,
            )
            raise
        except httpx.TimeoutException:
            logger.error(
                "[LLMService] Request timed out after {timeout}s",
                timeout=settings.llm_timeout_seconds,
            )
            raise
        except httpx.RequestError as err:
            logger.error(
                "[LLMService] Network error: {error}",
                error=str(err),
            )
            raise

        data = response.json()

        # Extract content from the standard OpenAI-compatible response shape.
        try:
            raw_response = data["choices"][0]["message"]["content"].strip()

            logger.debug(
                "[LLMService] Raw Clause Response:\n{}",
                raw_response,
            )

            # Remove markdown code fences if present
            raw_response = (
                raw_response
                    .replace("```json", "")
                    .replace("```", "")
                    .strip()
            )

            logger.debug(
                "[LLMService] Cleaned Clause Response:\n{}",
                raw_response,
            )   
        except (KeyError, IndexError) as err:
            raise ValueError(
                f"Unexpected LLM response structure: {data}"
            ) from err

        # Parse the JSON response; LLM should return an array of clauses.
        try:
            clauses = json.loads(raw_response)
        except json.JSONDecodeError as err:
            logger.error(
                "[LLMService] Failed to parse LLM JSON response: {error}",
                error=str(err),
            )
            raise ValueError(
                f"LLM did not return valid JSON: {raw_response[:200]}"
            ) from err

        if not isinstance(clauses, list):
            logger.error(
                "[LLMService] LLM returned non-list JSON: {type}",
                type=type(clauses).__name__,
            )
            raise ValueError(
                f"Expected JSON array of clauses, got {type(clauses).__name__}"
            )

        logger.info(
            "[LLMService] Clause extraction complete | {count} clauses extracted",
            count=len(clauses),
        )

        return clauses
