import torch

cuda_available = torch.cuda.is_available()

print(f"Torch version: {torch.__version__}\nCuda is available: {cuda_available}")
assert cuda_available


"""# Import dependencies"""

import os
import uvicorn
import logging
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, pipeline
import torch

from fastapi import FastAPI, Response, status
from pydantic import BaseModel

os.environ["HUGGING_FACE_HUB_TOKEN"] = "" # TODO: paste here your token

app = FastAPI()

#Model Quantization and BitsAndBytes - https://medium.com/@rakeshrajpurohit/model-quantization-with-hugging-face-transformers-and-bitsandbytes-integration-b4c9983e8996

#Quantization in 4-bit
nf4_config = BitsAndBytesConfig(
   load_in_4bit=True,
   bnb_4bit_quant_type="nf4",
   bnb_4bit_use_double_quant=True,
   bnb_4bit_compute_dtype=torch.bfloat16
)

MODEL =  "meta-llama/Meta-Llama-3-8B-Instruct"

model_bin = AutoModelForCausalLM.from_pretrained(
    MODEL,
    device_map='auto',
    #load_in_8bit=True, #Quantization in 8-bit
    quantization_config=nf4_config, #Quantization in 4-bit
    use_cache=False
)

messages = [
    {"role": "system", "content": """Ты чатбот портала поставщиков москвы и работаешь с 44-ФЗ. 
    Твоя задача: помочь пользователю с составлением допсоглашения. 
    Будь внимателен, правильно сравнивай числа, следуй закону и не придумывай новые данные
    """}
]

tokenizer = AutoTokenizer.from_pretrained(MODEL)

pipe = pipeline(
    "text-generation",
    model=model_bin,
    tokenizer=tokenizer,
    device_map="auto",
)

terminators = [
    pipe.tokenizer.eos_token_id,
    pipe.tokenizer.convert_tokens_to_ids("<|eot_id|>")
]

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

REPLACE = (('[', ''), (']', ''), (' ', '_'), (',', ''), ("'", ''))

def ask_llm(prompt, model=MODEL):
  outputs = pipe(
    messages + [{"role": "user", "content": prompt}],
    max_new_tokens=256,
    eos_token_id=terminators,
    do_sample=True,
    temperature=0.6,
    top_p=0.9,
  )
  result = outputs[0]["generated_text"][-1]

  return result['content']

# Define schema for the request body
class PromptRequest(BaseModel):
    prompt: str

@app.get("/request")
async def root(prompt: str, response: Response):
    logger.info(prompt)
    try:
        predicted_nl = ask_llm(prompt=prompt, model=MODEL)
        response.status_code = status.HTTP_200_OK
        return {"result": predicted_nl}
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": str(e)}

@app.post("/request")
async def root(payload: PromptRequest, response: Response):
    prompt = payload.prompt
    logger.info(prompt)
    try:
        predicted_nl = ask_llm(prompt=prompt, model=MODEL)
        response.status_code = status.HTTP_200_OK
        return {"result": predicted_nl}
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081)