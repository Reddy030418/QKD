import { AIAgent, AIConversation, AIMessage } from '../types/chat';

class AIService {
  private openaiApiKey: string;
  private anthropicApiKey: string;

  constructor() {
    this.openaiApiKey = process.env.REACT_APP_OPENAI_API_KEY || '';
    this.anthropicApiKey = process.env.REACT_APP_ANTHROPIC_API_KEY || '';
  }

  async sendToOpenAI(
    messages: { role: string; content: string }[],
    model: string = 'gpt-3.5-turbo',
    maxTokens: number = 1000
  ): Promise<{
    response: string;
    tokens_used: number;
    model_response: any;
  }> {
    if (!this.openaiApiKey) {
      throw new Error('OpenAI API key not configured');
    }

    try {
      const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.openaiApiKey}`,
        },
        body: JSON.stringify({
          model,
          messages,
          max_tokens: maxTokens,
          temperature: 0.7,
        }),
      });

      if (!response.ok) {
        throw new Error(`OpenAI API error: ${response.statusText}`);
      }

      const data = await response.json();
      const choice = data.choices[0];

      return {
        response: choice.message.content,
        tokens_used: data.usage.total_tokens,
        model_response: data,
      };
    } catch (error) {
      console.error('OpenAI API error:', error);
      throw error;
    }
  }

  async sendToAnthropic(
    messages: { role: string; content: string }[],
    model: string = 'claude-3-sonnet-20240229',
    maxTokens: number = 1000
  ): Promise<{
    response: string;
    tokens_used: number;
    model_response: any;
  }> {
    if (!this.anthropicApiKey) {
      throw new Error('Anthropic API key not configured');
    }

    try {
      // Convert messages to Anthropic format
      const anthropicMessages = messages.map(msg => ({
        role: msg.role === 'assistant' ? 'assistant' : 'user',
        content: msg.content,
      }));

      const response = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': this.anthropicApiKey,
          'anthropic-version': '2023-06-01',
        },
        body: JSON.stringify({
          model,
          messages: anthropicMessages,
          max_tokens: maxTokens,
          temperature: 0.7,
        }),
      });

      if (!response.ok) {
        throw new Error(`Anthropic API error: ${response.statusText}`);
      }

      const data = await response.json();

      return {
        response: data.content[0].text,
        tokens_used: data.usage.input_tokens + data.usage.output_tokens,
        model_response: data,
      };
    } catch (error) {
      console.error('Anthropic API error:', error);
      throw error;
    }
  }

  async sendToAI(
    agent: AIAgent,
    messages: { role: string; content: string }[],
    model?: string,
    maxTokens: number = 1000
  ): Promise<{
    response: string;
    tokens_used: number;
    model_response: any;
  }> {
    // Use agent's configured model or default
    const aiModel = model || agent.model_type;

    // Determine which API to use based on model type
    if (aiModel.includes('gpt') || aiModel.includes('openai')) {
      return this.sendToOpenAI(messages, aiModel, maxTokens);
    } else if (aiModel.includes('claude') || aiModel.includes('anthropic')) {
      return this.sendToAnthropic(messages, aiModel, maxTokens);
    } else {
      throw new Error(`Unsupported AI model: ${aiModel}`);
    }
  }

  // Helper method to format conversation context for AI
  formatConversationContext(
    conversation: AIConversation,
    messages: AIMessage[]
  ): { role: string; content: string }[] {
    const context = [];

    // Add system prompt if available
    if (conversation.context?.system_prompt) {
      context.push({
        role: 'system',
        content: conversation.context.system_prompt,
      });
    }

    // Add recent messages (limit to last 10 for context)
    const recentMessages = messages.slice(-10);
    for (const message of recentMessages) {
      context.push({
        role: message.role,
        content: message.content,
      });
    }

    return context;
  }

  // Helper method to create a QKD-focused system prompt
  createQKDSystemPrompt(): string {
    return `You are an AI assistant specialized in Quantum Key Distribution (QKD) and quantum cryptography.

Your expertise includes:
- BB84 protocol and other QKD protocols
- Quantum mechanics principles
- Cryptographic key generation and distribution
- Quantum security concepts
- Error correction and privacy amplification
- Quantum channel characteristics

When helping users:
- Explain quantum concepts clearly and accurately
- Provide practical guidance for QKD implementation
- Help troubleshoot QKD simulation issues
- Suggest security improvements
- Explain the mathematical foundations when relevant

Always maintain scientific accuracy while being accessible to users with varying levels of quantum knowledge.`;
  }

  // Helper method to create a general assistant system prompt
  createGeneralSystemPrompt(): string {
    return `You are a helpful AI assistant with expertise in quantum computing, cryptography, and software development.

You can help with:
- Quantum Key Distribution (QKD) concepts and implementation
- Cryptographic protocols and security
- Programming and software development
- General technical questions
- Problem-solving and debugging

Provide clear, accurate, and helpful responses while maintaining a professional and friendly tone.`;
  }
}

export const aiService = new AIService();
