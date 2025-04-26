from django.test import TestCase
from chat.ai_agents import get_agent_response

class LLMFlowTest(TestCase):
    def test_llm_input_output(self):
        agents = ['june', 'ludwig', 'gustav', 'salvador']
        prompt = "Hello, how can you help me?"
        context = "User: Hi\n"

        for agent in agents:
            response = get_agent_response(agent, prompt, context)
            print(f"Agent: {agent}, Response: {response}")
            self.assertIsInstance(response, str)
            self.assertTrue(len(response) > 0)