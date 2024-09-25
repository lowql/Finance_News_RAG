import ollama
def list_model():
  models = ollama.list()
  models = models['models']
  available_models = []
  for model in models:
    available_models.append(model['name'])
    print('model name: ',model['name'])
    print('modified time: ',model['modified_at'])
    print(model['details'])
    print('model details: \n','parameter_size: ',model['details']['parameter_size'],'\n quantization_level: ',model['details']['quantization_level'])
    print()
  return available_models

def pull_model():
    # 預計要下載的模型
    models = ['yi:latest', 'llama3.1:latest']
    
    # 獲取已下載的模型列表
    downloaded_models = list_model()
    print(f"以下載模型: {downloaded_models}")
    
    # 遍歷預計要下載的模型
    for model in models:
        # 檢查模型是否已下載
        if model not in downloaded_models:
            try:
                print(f"正在下載模型: {model}")
                ollama.pull(model)
                print(f"模型 {model} 下載完成")
            except ollama.ResponseError as e:
                print(f'下載模型 {model} 時發生錯誤:', e.error)
        else:
            print(f"模型 {model} 已存在，跳過下載")

    print("所有模型下載完成")
    
  
  
if __name__ == "__main__":
  list_model()