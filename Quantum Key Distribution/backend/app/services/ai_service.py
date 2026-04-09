from ..core.database import db
from ..models import AIAgent, AIConversation, AIMessage, User
from typing import List, Optional, Dict, Any
import logging
import json
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

class AIService:
    """Service for managing AI assistant functionality"""

    @staticmethod
    def create_agent(name: str, description: str, model_type: str,
                    api_endpoint: Optional[str], api_key: Optional[str],
                    system_prompt: Optional[str], created_by: int) -> AIAgent:
        """Create a new AI agent"""
        try:
            agent = AIAgent(
                name=name,
                description=description,
                model_type=model_type,
                api_endpoint=api_endpoint,
                api_key=api_key,
                system_prompt=system_prompt,
                created_by=created_by
            )
            db.session.add(agent)
            db.session.commit()

            logger.info(f"AI agent '{name}' created by user {created_by}")
            return agent
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating AI agent: {e}")
            raise

    @staticmethod
    def get_agent(agent_id: int) -> Optional[AIAgent]:
        """Get an AI agent by ID"""
        return AIAgent.query.get(agent_id)

    @staticmethod
    def get_user_agents(user_id: int) -> List[AIAgent]:
        """Get all AI agents created by a user"""
        return AIAgent.query.filter_by(created_by=user_id, is_active=1).all()

    @staticmethod
    def create_conversation(agent_id: int, user_id: int, title: Optional[str] = None,
                          context: Optional[Dict] = None) -> AIConversation:
        """Create a new AI conversation"""
        try:
            conversation = AIConversation(
                agent_id=agent_id,
                user_id=user_id,
                title=title,
                context=context
            )
            db.session.add(conversation)
            db.session.flush()  # Get conversation ID

            # Add system message if agent has system prompt
            agent = AIAgent.query.get(agent_id)
            if agent and agent.system_prompt:
                system_message = AIMessage(
                    conversation_id=conversation.id,
                    role='system',
                    content=agent.system_prompt
                )
                db.session.add(system_message)

            db.session.commit()

            logger.info(f"AI conversation created for user {user_id} with agent {agent_id}")
            return conversation
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating AI conversation: {e}")
            raise

    @staticmethod
    def add_message(conversation_id: int, role: str, content: str,
                   tokens_used: Optional[int] = None, model_response: Optional[Dict] = None) -> AIMessage:
        """Add a message to an AI conversation"""
        try:
            message = AIMessage(
                conversation_id=conversation_id,
                role=role,
                content=content,
                tokens_used=tokens_used,
                model_response=model_response
            )
            db.session.add(message)
            db.session.commit()

            logger.info(f"Message added to conversation {conversation_id}")
            return message
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding AI message: {e}")
            raise

    @staticmethod
    def get_conversation_messages(conversation_id: int) -> List[AIMessage]:
        """Get all messages in an AI conversation"""
        return AIMessage.query.filter_by(conversation_id=conversation_id)\
            .order_by(AIMessage.created_at.asc()).all()

    @staticmethod
    def get_user_conversations(user_id: int) -> List[AIConversation]:
        """Get all AI conversations for a user"""
        return AIConversation.query.filter_by(user_id=user_id)\
            .order_by(AIConversation.updated_at.desc()).all()

    @staticmethod
    async def send_to_ai_agent(agent_id: int, user_message: str,
                              conversation_context: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Send a message to an AI agent and get response"""
        try:
            agent = AIAgent.query.get(agent_id)
            if not agent:
                raise ValueError(f"AI agent {agent_id} not found")

            if not agent.is_active:
                raise ValueError(f"AI agent {agent_id} is not active")

            # Prepare messages for AI API
            messages = []

            # Add system prompt if available
            if agent.system_prompt:
                messages.append({"role": "system", "content": agent.system_prompt})

            # Add conversation context if provided
            if conversation_context:
                messages.extend(conversation_context)

            # Add user message
            messages.append({"role": "user", "content": user_message})

            # Prepare API request
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {agent.api_key}" if agent.api_key else ""
            }

            payload = {
                "model": agent.model_type,
                "messages": messages,
                "max_tokens": 1000,
                "temperature": 0.7
            }

            # Make API request
            response = requests.post(
                agent.api_endpoint or "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code != 200:
                raise Exception(f"AI API request failed: {response.status_code} - {response.text}")

            result = response.json()
            ai_response = result["choices"][0]["message"]["content"]
            tokens_used = result.get("usage", {}).get("total_tokens", 0)

            return {
                "response": ai_response,
                "tokens_used": tokens_used,
                "model_response": result
            }

        except Exception as e:
            logger.error(f"Error communicating with AI agent {agent_id}: {e}")
            raise

    @staticmethod
    def get_qkd_context(session_id: int) -> Dict[str, Any]:
        """Get QKD session context for AI assistant"""
        try:
            from ..models import QKDSession
            session = QKDSession.query.get(session_id)
            if not session:
                return {}

            return {
                "session_id": session.session_id,
                "parameters": {
                    "key_length": session.key_length,
                    "noise_level": session.noise_level,
                    "detector_efficiency": session.detector_efficiency,
                    "eavesdropper_present": session.eavesdropper_present
                },
                "results": {
                    "status": session.status,
                    "security_status": session.security_status,
                    "final_key_length": session.final_key_length,
                    "quantum_error_rate": session.quantum_error_rate
                },
                "timestamp": session.created_at.isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting QKD context: {e}")
            return {}

    @staticmethod
    def generate_qkd_explanation(session_id: int, agent_id: int) -> str:
        """Generate explanation of QKD session results using AI"""
        try:
            context = AIService.get_qkd_context(session_id)
            if not context:
                return "Unable to generate explanation - QKD session not found."

            prompt = f"""
            Please explain the following QKD (BB84 protocol) simulation results in simple terms:

            Session ID: {context['session_id']}
            Parameters:
            - Key Length: {context['parameters']['key_length']} bits
            - Noise Level: {context['parameters']['noise_level']}
            - Detector Efficiency: {context['parameters']['detector_efficiency']}
            - Eavesdropper Present: {context['parameters']['eavesdropper_present']}

            Results:
            - Status: {context['results']['status']}
            - Security Status: {context['results']['security_status']}
            - Final Key Length: {context['results']['final_key_length']} bits
            - Quantum Error Rate: {context['results']['quantum_error_rate']}

            Please provide a clear explanation of what these results mean for quantum key distribution security.
            """

            # This would normally call the AI API, but for now return a template response
            return f"""
            QKD Session Analysis ({context['session_id']}):

            **Configuration:**
            - Key Length: {context['parameters']['key_length']} bits
            - Noise Level: {context['parameters']['noise_level']}
            - Detector Efficiency: {context['parameters']['detector_efficiency']}
            - Eavesdropper Simulation: {'Enabled' if context['parameters']['eavesdropper_present'] else 'Disabled'}

            **Results:**
            - Protocol Status: {context['results']['status'].title()}
            - Security Assessment: {context['results']['security_status'].title()}
            - Final Key Length: {context['results']['final_key_length']} bits
            - Quantum Bit Error Rate: {context['results']['quantum_error_rate']:.4f}

            **Security Analysis:**
            {AIService._get_security_analysis(context)}
            """

        except Exception as e:
            logger.error(f"Error generating QKD explanation: {e}")
            return "Unable to generate QKD session explanation due to an error."

    @staticmethod
    def _get_security_analysis(context: Dict[str, Any]) -> str:
        """Generate security analysis based on QKD results"""
        error_rate = context['results']['quantum_error_rate']
        security_status = context['results']['security_status']

        if error_rate > 0.15:  # High error rate
            return "⚠️ HIGH SECURITY RISK: The quantum error rate is above acceptable thresholds, indicating potential eavesdropping or significant channel noise."
        elif error_rate > 0.05:  # Moderate error rate
            return "⚡ MODERATE SECURITY: Elevated error rate detected. Additional privacy amplification may be required."
        elif security_status == 'secure':
            return "✅ SECURE: The quantum channel appears secure with acceptable error rates."
        else:
            return "❓ UNCERTAIN: Security status requires further analysis of the quantum channel."

    @staticmethod
    def update_agent_activity(agent_id: int) -> None:
        """Update the last used timestamp for an AI agent"""
        try:
            agent = AIAgent.query.get(agent_id)
            if agent:
                agent.updated_at = datetime.utcnow()
                db.session.commit()
        except Exception as e:
            logger.error(f"Error updating agent activity: {e}")

    @staticmethod
    def delete_conversation(conversation_id: int, user_id: int) -> bool:
        """Delete an AI conversation (only by owner)"""
        try:
            conversation = AIConversation.query.filter_by(
                id=conversation_id,
                user_id=user_id
            ).first()

            if conversation:
                db.session.delete(conversation)
                db.session.commit()
                logger.info(f"AI conversation {conversation_id} deleted by user {user_id}")
                return True
            return False
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting AI conversation: {e}")
            raise
