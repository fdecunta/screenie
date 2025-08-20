# Create the config directory first
mkdir -p ~/.config/screenie

# Then create the config file with heredoc
cat > ~/.config/screenie/config.yaml << 'EOF'
default: "openai-gpt-4"

model_list:
  - model_name: "openai-gpt-4"
    litellm_params:
      model: "gpt-4"
      api_key: "sk-your-openai-key-here"

  - model_name: "anthropic-claude"
    litellm_params:
      model: "claude-3-sonnet"
      api_key: "your-anthropic-key-here"

  - model_name: "DigitalOcean-llama3.3"
    litellm_params:
      model: "gradient_ai/llama3.3-70b-instruct"
      api_key: "DigitalOcean-endpoint-inference-key"
EOF
