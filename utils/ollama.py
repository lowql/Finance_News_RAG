import ollama
model = 'yi'

try:
  ollama.pull(model)
except ollama.ResponseError as e:
  print('Error:', e.error)