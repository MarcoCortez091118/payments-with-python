from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from langchain.prompts import ChatPromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.output_parsers import StrOutputParser

from app.agent.tools import AgentTools
from app.clients.errors import CircuitBreakerOpen
from app.core.config import get_settings
from app.core.logging import get_logger
from app.services.conversation_service import ConversationState
from app.utils.amount import parse_amount
from app.utils.phone import normalize_phone_number

try:  # pragma: no cover - optional dependency when API key available
    from langchain_openai import ChatOpenAI  # type: ignore
except Exception:  # pragma: no cover
    ChatOpenAI = None  # type: ignore


CONFIRMATION_KEYWORDS = {"si", "sí", "claro", "confirmo", "por supuesto"}
NEGATIVE_KEYWORDS = {"no", "cancelar", "detener"}


class EchoChatModel(BaseChatModel):
    """Deterministic chat model used for tests when no LLM is configured."""

    def _generate(self, messages: list[HumanMessage | SystemMessage | AIMessage], stop: list[str] | None = None, **kwargs: Any) -> ChatResult:  # noqa: ARG002
        content = ""
        if messages:
            last = messages[-1].content
            if isinstance(last, str) and "Target response:" in last:
                content = last.split("Target response:", maxsplit=1)[1].strip()
            else:
                content = str(last)
        generation = ChatGeneration(message=AIMessage(content=content))
        return ChatResult(generations=[generation])

    async def _agenerate(self, messages: list[HumanMessage | SystemMessage | AIMessage], stop: list[str] | None = None, **kwargs: Any) -> ChatResult:  # noqa: ARG002
        return self._generate(messages, stop=stop, **kwargs)


@dataclass
class AgentResponse:
    text: str
    state: ConversationState
    status: str
    metadata: dict[str, Any]


class ConversationAgent:
    def __init__(self, tools: AgentTools) -> None:
        self.tools = tools
        self.settings = get_settings()
        self.logger = get_logger(self.__class__.__name__)
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "Eres un asistente financiero que ayuda a usuarios a enviar dinero de forma cordial y segura."),
                (
                    "human",
                    "Contexto de la conversación:\n{context}\nMensaje del usuario: {user_message}\nObjetivo del asistente: {target_response}\nTarget response: {target_response}",
                ),
            ]
        )
        self.llm = self._configure_llm()
        self.chain = self.prompt | self.llm | StrOutputParser()

    def _configure_llm(self) -> BaseChatModel:
        if not self.settings.use_fake_llm and ChatOpenAI is not None and self.settings.openai_api_key:
            return ChatOpenAI(model="gpt-4.1-mini", temperature=0.2, api_key=self.settings.openai_api_key)
        return EchoChatModel()

    async def _render(self, context: str, user_message: str, target_response: str) -> str:
        return await self.chain.ainvoke(
            {
                "context": context,
                "user_message": user_message,
                "target_response": target_response,
            }
        )

    async def handle(self, state: ConversationState, message: str, conversation_id) -> AgentResponse:  # noqa: ANN001
        lower_message = message.lower()
        normalized_phone = normalize_phone_number(message)
        amount = parse_amount(message)

        if normalized_phone:
            state.phone_number = normalized_phone
        if amount:
            state.amount = amount

        if state.stage == "greeting":
            state.stage = "awaiting_phone"

        if state.stage == "awaiting_phone" and not state.phone_number:
            target = "Necesito el número de celular de 10 dígitos del destinatario."
            response_text = await self._render(self._context_summary(state), message, target)
            return AgentResponse(response_text, state, "awaiting_phone", {})

        if state.phone_number and state.stage in {"awaiting_phone", "awaiting_amount"}:
            state.stage = "awaiting_amount"
            if not state.amount:
                target = f"He recibido el número {state.phone_number}. Pregunta educadamente el monto a enviar."
                response_text = await self._render(self._context_summary(state), message, target)
                return AgentResponse(response_text, state, "awaiting_amount", {})

        if state.stage in {"awaiting_amount", "awaiting_confirmation"} and not state.amount:
            target = "Solicita un monto válido mayor a cero para continuar."
            response_text = await self._render(self._context_summary(state), message, target)
            return AgentResponse(response_text, state, "awaiting_amount", {})

        if state.amount and state.stage != "awaiting_confirmation":
            state.stage = "awaiting_confirmation"
            formatted_amount = f"{state.amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            target = f"Confirma con el usuario si desea enviar ${formatted_amount} COP al número {state.phone_number}."
            response_text = await self._render(self._context_summary(state), message, target)
            return AgentResponse(response_text, state, "awaiting_confirmation", {})

        if state.stage == "awaiting_confirmation":
            if any(keyword in lower_message for keyword in CONFIRMATION_KEYWORDS):
                try:
                    payload = {
                        "recipient_phone": state.phone_number,
                        "amount": state.amount,
                        "currency": state.currency,
                    }
                    validation = await self.tools.validate_transaction_tool(payload)
                except CircuitBreakerOpen:
                    target = "Informa al usuario que el servicio externo no está disponible temporalmente e invita a intentar más tarde."
                    response_text = await self._render(self._context_summary(state), message, target)
                    return AgentResponse(response_text, state, "error", {"error": "circuit_open"})
                except Exception as exc:  # noqa: BLE001
                    self.logger.error("Validation failed", error=str(exc))
                    target = "Indica que hubo un error al validar la transacción e intenta nuevamente más tarde."
                    response_text = await self._render(self._context_summary(state), message, target)
                    return AgentResponse(response_text, state, "error", {"error": "validation_failed"})

                if validation.get("status") != "approved":
                    target = "Indica que la transacción no pudo ser aprobada y solicita verificar los datos o intentar más tarde."
                    response_text = await self._render(self._context_summary(state), message, target)
                    return AgentResponse(response_text, state, "error", {"error": "not_approved"})

                try:
                    execution = await self.tools.execute_transaction_tool(state, conversation_id)
                except CircuitBreakerOpen:
                    target = "Comunica que el servicio no está disponible temporalmente y que reintente luego."
                    response_text = await self._render(self._context_summary(state), message, target)
                    return AgentResponse(response_text, state, "error", {"error": "circuit_open"})
                except Exception as exc:  # noqa: BLE001
                    self.logger.error("Execution failed", error=str(exc))
                    target = "Informa que la transacción falló y que se registró el intento."
                    response_text = await self._render(self._context_summary(state), message, target)
                    return AgentResponse(response_text, state, "error", {"error": "execution_failed"})

                transaction_id = execution.get("transaction_id", "desconocido")
                status = execution.get("status", "pending")
                target = f"Confirma al usuario que la transacción fue {status} y proporciona el ID {transaction_id}."
                state.stage = "completed"
                response_text = await self._render(self._context_summary(state), message, target)
                return AgentResponse(
                    response_text,
                    state,
                    "completed",
                    {"transaction_id": transaction_id, "status": status},
                )

            if any(keyword in lower_message for keyword in NEGATIVE_KEYWORDS):
                state.amount = None
                state.stage = "awaiting_amount"
                target = "Reconoce la cancelación y pregunta si desea indicar un nuevo monto."
                response_text = await self._render(self._context_summary(state), message, target)
                return AgentResponse(response_text, state, "awaiting_amount", {})

            target = "Solicita una confirmación clara con sí o no para proceder."
            response_text = await self._render(self._context_summary(state), message, target)
            return AgentResponse(response_text, state, "awaiting_confirmation", {})

        target = "Despedida corta y profesional indicando que la sesión finalizó."
        response_text = await self._render(self._context_summary(state), message, target)
        return AgentResponse(response_text, state, "completed", {})

    def _context_summary(self, state: ConversationState) -> str:
        return (
            f"Estado: {state.stage}. Teléfono: {state.phone_number or 'no proporcionado'}. "
            f"Monto: {state.amount or 'no proporcionado'} {state.currency}."
        )
