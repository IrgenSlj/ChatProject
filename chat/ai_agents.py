from transformers import pipeline

AGENT_PROFILES = {
    "june": {
        "display_name": "June",
        "description": "The assistant and friendship model.",
        "model": "microsoft/DialoGPT-medium",
        "task": "text-generation",
        "prompt_prefix": "You are June, a friendly assistant and companion. "
    },
    "ludwig": {
        "display_name": "Ludwig",
        "description": "The architect and designer.",
        "model": "google/flan-t5-large",
        "task": "text2text-generation",
        "prompt_prefix": "You are Ludwig, an expert architect and designer. "
    },
    "gustav": {
        "display_name": "Gustav",
        "description": "The coder and engineer.",
        "model": "codellama/CodeLlama-7b-Instruct-hf",
        "task": "text-generation",
        "prompt_prefix": "You are Gustav, a skilled coder and engineer. "
    },
    "salvador": {
        "display_name": "Salvador",
        "description": "The artist and interactive content generator.",
        "model": "google/flan-t5-large",
        "task": "text2text-generation",
        "prompt_prefix": "You are Salvador, an imaginative artist and content generator. "
    },
}

AGENT_PIPES = {}

def get_agent_pipe(agent_name):
    if agent_name not in AGENT_PIPES:
        profile = AGENT_PROFILES[agent_name]
        AGENT_PIPES[agent_name] = pipeline(profile["task"], model=profile["model"])
    return AGENT_PIPES[agent_name]

def get_agent_response(agent_name, user_message, context=None):
    profile = AGENT_PROFILES.get(agent_name)
    if not profile:
        return "Sorry, this agent is not available."
    pipe = get_agent_pipe(agent_name)
    prompt = profile["prompt_prefix"]
    if context:
        prompt += f"\nConversation so far:\n{context}\nUser: {user_message}"
    else:
        prompt += user_message
    result = pipe(prompt, max_new_tokens=128)
    if isinstance(result, list) and "generated_text" in result[0]:
        return result[0]["generated_text"]
    elif isinstance(result, list) and "generated_text" not in result[0]:
        return str(result[0])
    elif "generated_text" in result:
        return result["generated_text"]
    elif "answer" in result:
        return result["answer"]
    else:
        return str(result)