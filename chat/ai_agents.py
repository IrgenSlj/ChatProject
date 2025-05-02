from transformers import pipeline, AutoModelForCausalLM, AutoModelForSeq2SeqLM, AutoTokenizer
import torch
from django.conf import settings

AGENT_CONFIGS = {
    "june": {
        "name": "June",
        "model_name": "facebook/opt-350m",  # Smaller, faster model
        "pipeline_type": "text-generation",
        "description": "Friendly conversational AI assistant",
        "min_length": 20,
        "max_length": 100,
        "temperature": 0.7,
        "top_p": 0.9,
        "model_type": "causal"
    },
    "ludwig": {
        "name": "Ludwig",
        "model_name": "google/flan-t5-small",  # Smaller version for faster responses
        "pipeline_type": "text2text-generation",
        "description": "Technical and analytical problem solver",
        "min_length": 30,
        "max_length": 150,
        "temperature": 0.3,
        "top_p": 0.95,
        "model_type": "seq2seq"
    },
    "gustav": {
        "name": "Gustav",
        "model_name": "Salesforce/codegen-350M-mono",  # Specialized code model
        "pipeline_type": "text-generation",
        "description": "Code generation and explanation specialist",
        "min_length": 50,
        "max_length": 200,
        "temperature": 0.2,
        "top_p": 0.95,
        "model_type": "causal"
    },
    "salvador": {
        "name": "Salvador",
        "model_name": "EleutherAI/gpt-neo-125M",  # Smaller creative model
        "pipeline_type": "text-generation",
        "description": "Creative and artistic content generator",
        "min_length": 30,
        "max_length": 150,
        "temperature": 0.9,
        "top_p": 0.95,
        "model_type": "causal"
    }
}

AGENT_PIPES = {}

def initialize_pipeline(agent_name):
    """Initialize a pipeline for an agent with proper model loading and device placement"""
    config = AGENT_CONFIGS[agent_name]
    try:
        # Determine device
        device = 0 if (torch.cuda.is_available() and settings.DEBUG) else -1
        
        # Load appropriate model class
        if config['model_type'] == 'seq2seq':
            model = AutoModelForSeq2SeqLM.from_pretrained(config['model_name'])
        else:
            model = AutoModelForCausalLM.from_pretrained(config['model_name'])
            
        tokenizer = AutoTokenizer.from_pretrained(config['model_name'])
        
        # Move model to GPU if available
        if device == 0:
            model = model.to('cuda')
            
        # Create pipeline with model-specific parameters
        pipe = pipeline(
            config['pipeline_type'],
            model=model,
            tokenizer=tokenizer,
            device=device,
            min_length=config['min_length'],
            max_length=config['max_length'],
            temperature=config['temperature'],
            top_p=config['top_p']
        )
        
        return pipe
    except Exception as e:
        print(f"Error initializing pipeline for {agent_name}: {e}")
        return None

def get_agent_pipe(agent_name):
    """Get or initialize an agent's pipeline"""
    if agent_name not in AGENT_PIPES:
        AGENT_PIPES[agent_name] = initialize_pipeline(agent_name)
    return AGENT_PIPES[agent_name]

def get_agent_response(agent_name, user_message, context=None):
    """Generate a response from an agent"""
    config = AGENT_CONFIGS.get(agent_name)
    if not config:
        return "Sorry, this agent is not available."
        
    pipe = get_agent_pipe(agent_name)
    if not pipe:
        return "Sorry, this agent's model failed to initialize."
        
    # Construct prompt based on agent type
    if config['model_type'] == 'seq2seq':
        prompt = f"{config['description']}\n"
        if context:
            prompt += f"Context: {context}\n"
        prompt += f"Query: {user_message}"
    else:
        prompt = f"You are {config['name']}, {config['description']}\n"
        if context:
            prompt += f"\nPrevious conversation:\n{context}"
        prompt += f"\nUser: {user_message}\n{config['name']}:"
    
    try:
        # Generate response
        result = pipe(prompt, 
                     max_new_tokens=config['max_length'],
                     min_length=config['min_length'],
                     temperature=config['temperature'],
                     top_p=config['top_p'])
        
        # Extract response text based on pipeline type
        if isinstance(result, list):
            if 'generated_text' in result[0]:
                response = result[0]['generated_text']
            else:
                response = str(result[0])
        else:
            response = result.get('generated_text', str(result))
            
        # Clean up response for seq2seq models
        if config['model_type'] == 'seq2seq':
            return response
        else:
            # Remove the prompt from the response for causal models
            return response[len(prompt):].strip()
            
    except Exception as e:
        print(f"Error generating response for {agent_name}: {e}")
        return f"Sorry, I encountered an error while generating a response."