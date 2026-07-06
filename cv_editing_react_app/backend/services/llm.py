from langchain_ollama import ChatOllama
import time
from services.database.db_schema import LLM_Eval
from services.database.db import add_llm_eval


MODEL_NAME = "qwen3.5:9b"
HOST_ADDRESS = "http://localhost:11434"  # or "http://localhost:11434" "http://ip of your server:11434"

class LLM_With_Tracking:
    def __init__(self, model_name=MODEL_NAME, temperature=0, reasoning=False, task_name=None, base_url=HOST_ADDRESS):
        self.llm = ChatOllama(
                                model=model_name,
                                temperature=temperature,
                                reasoning=reasoning,
                                keep_alive='20m',
                                base_url=base_url,
                                # other params...
                            )
        self.task_name = task_name or "unknown"

    def invoke_with_tracking(self, messages, pydantic_model=None):
        start_time = time.time()
        raw_output = None
        structured_output = None
        error_message = None
        num_input_tokens = 0
        num_output_tokens = 0
        num_total_tokens = 0

        try:
            response = self.llm.invoke(messages)
            raw_output = response.content
            elapsed = time.time() - start_time

            usage = getattr(response, "usage_metadata", {}) or {}
            num_input_tokens = usage.get("input_tokens", 0)
            num_output_tokens = usage.get("output_tokens", 0)
            num_total_tokens = num_input_tokens + num_output_tokens

            if pydantic_model is not None and getattr(response, "content", None) is not None:
                structured_output = pydantic_model.model_validate_json(response.content)

        except Exception as e:
            error_message = str(e)
            elapsed = time.time() - start_time

        result = {
            "structured_output": structured_output,
            "raw_output": raw_output,
            "task_name": self.task_name,
            "time_taken": round(elapsed, 3),
            "input_tokens": num_input_tokens,
            "output_tokens": num_output_tokens,
            "total_tokens": num_total_tokens,
            "error": error_message,
        }

        eval_entry = LLM_Eval(
            task_name=result["task_name"],
            raw_output=result["raw_output"],
            time_taken=result["time_taken"],
            input_tokens=result["input_tokens"],
            output_tokens=result["output_tokens"],
            total_tokens=result["total_tokens"],
            error=result["error"]
        )

        add_llm_eval(eval_entry)

        return result

if __name__ == "__main__":
    from pydantic import BaseModel, Field

    class Movie(BaseModel):
        """A movie with details."""
        title: str = Field(description="The title of the movie")
        year: int = Field(description="The year the movie was released")
        director: str = Field(description="The director of the movie")
        rating: float = Field(description="The movie's rating out of 10")

    prompt = f'''Provide details about the movie Inception

        Return ONLY a JSON object.
        Do NOT return the schema.
        The JSON object must conform to this JSON Schema:
        {Movie.model_json_schema()}
        '''
    
    llm_tracker = LLM_With_Tracking(model_name=MODEL_NAME, task_name="cv_editing")

    messages = [
        ("system","You are a helpful assistant."),
        ("human", prompt),
    ]


    output = llm_tracker.invoke_with_tracking(messages,pydantic_model=Movie)

    print(output)