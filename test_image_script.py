from google import genai
import inspect
client = genai.Client()
print(inspect.signature(client.models.generate_images))
