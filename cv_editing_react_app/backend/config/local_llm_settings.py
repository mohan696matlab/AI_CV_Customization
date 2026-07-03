from ollama import Client

MODEL_NAME = "qwen3.5:9b"
HOST_ADDRESS = "http://localhost:11434"  # or "http://localhost:11434" "http://192.168.20.23:11434"

client = Client(host=HOST_ADDRESS)