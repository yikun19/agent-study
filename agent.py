import re
from llm_client import LlmClient
from prompt import AGENT_SYSTEM_PROMPT
from tools import available_tools

API_KEY = "sk-bc98f26735994a7fb4f88c5b9cacf1f0"
BASE_URL = "https://api.deepseek.com"
MODEL_ID = "deepseek-flash"
TAVILY_API_KEY = "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"

llm = LlmClient(
  model=MODEL_ID,
  api_key=API_KEY,
  base_url=BASE_URL
)

user_prompt = "你好，请帮我查询一下今天成都的天气，然后根据天气推荐一个合适的旅游景点。"
prompt_history = [f"用户请求: {user_prompt}"]

print(f"用户输入: {user_prompt}\n" + "="*40)

for i in range(5):
  print(f"--- 循环 {i + 1} ---\n")
  full_prompt = "\n".join(prompt_history)
  llm_output = llm.generate(full_prompt, system_prompt=AGENT_SYSTEM_PROMPT)
  match = re.search(r'(Thought:.*?Action:.*?)(?=\n\s*(?:Thought:|Action:|Observation:)|\Z)', llm_output, re.DOTALL)
  if match:
    truncated = match.group(1).strip()
    if truncated != llm_output.strip():
      llm_output = truncated
      print("已截断多余的 Thought-Action 对")
  print(f'模型输出：\n{llm_output}\n')
  prompt_history.append(llm_output)

  action_match = re.search(r'Action: (.*)', llm_output, re.DOTALL)

  if not action_match:
    observation = "错误: 未能解析到 Action 字段。请确保你的回复严格遵循 'Thought: ... Action: ...' 的格式。"
    observation_str = f"Observation: {observation}"
    print(f"{observation_str}\n" + "="*40)
    prompt_history.append(observation_str)
    continue
  action_str = action_match.group(1).strip()

  if action_str.startswith("Finish"):
    final_answer = re.match(r"Finish\[(.*)\]", action_str).group(1)
    print(f"任务完成，最终答案: {final_answer}")
    break

  tool_name = re.search(r"(\w+)\(", action_str).group(1)
  args_str = re.search(r"\((.*)\)", action_str).group(1)
  kwargs = dict(re.findall(r'(\w+)="([^"]*)"', args_str))

  if tool_name in available_tools:
    observation = available_tools[tool_name](**kwargs)

  else:
    observation = f"错误:未定义的工具 '{tool_name}'"

  observation_str = f"Observation: {observation}"
  print(f"{observation_str}\n" + "="*40)
  prompt_history.append(observation_str)


