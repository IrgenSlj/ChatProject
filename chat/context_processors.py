from .ai_agents import AGENT_CONFIGS

def agent_configs(request):
    return {
        'AGENT_CONFIGS': AGENT_CONFIGS
    }