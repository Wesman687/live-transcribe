# lt_app/turn_detector.py
import time
import onnxruntime as ort
from transformers import AutoTokenizer
from pathlib import Path

# Constants
MODEL_PATH = Path("models/turn-detector/onnx/model_q8.onnx")
TOKENIZER_ID = "livekit/turn-detector"
MAX_HISTORY_TOKENS = 512

# Load once
tokenizer = AutoTokenizer.from_pretrained("models/turn-detector", local_files_only=True)
session = ort.InferenceSession("models/turn-detector/onnx/model.onnx", providers=["CPUExecutionProvider"])


def get_turn_probability(chat_ctx: list[dict]) -> float:
    start = time.perf_counter()

    formatted = tokenizer.apply_chat_template(
        chat_ctx,
        add_special_tokens=False,
        add_generation_prompt=False,
        tokenize=False,
    )

    if "<|im_end|>" in formatted:
        formatted = formatted.rsplit("<|im_end|>", 1)[0]

    inputs = tokenizer(
        formatted,
        return_tensors="np",
        max_length=MAX_HISTORY_TOKENS,
        truncation=True,
    )

    outputs = session.run(
        None,
        {
            "input_ids": inputs["input_ids"].astype("int64"),
        },
    )

    # ✅ Directly use the scalar value
    prob = float(outputs[0][0])


    return prob