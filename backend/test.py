from transformers import VisionEncoderDecoderModel

print("start")
model = VisionEncoderDecoderModel.from_pretrained(
    "microsoft/trocr-base-handwritten"
)
print("done")