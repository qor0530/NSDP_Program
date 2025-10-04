import google.generativeai as genai
import json

# 1. API 키 설정
# 아래 따옴표 안에 발급받은 본인의 API 키를 붙여넣으세요.
API_KEY = "api_key"

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-flash-latest')

# 2. 문제 텍스트 붙여넣기
# 이제 이 안에 따옴표나 어떤 특수문자가 들어가도 괜찮습니다.
problem_text = """
연도 진행바 스페셜 저지
시간 제한	메모리 제한	제출	정답	맞힌 사람	정답 비율
2 초	128 MB	4477	2064	1812	48.166%
문제
문빙이는 새해를 좋아한다. 하지만, 이제 새해는 너무 많이 남았다. 그래도 문빙이는 새해를 기다릴 것이다.

어느 날 문빙이는 잠에서 깨면서 스스로에게 물었다. “잠깐, 새해가 얼마나 남은거지?”

이 문제에 답하기 위해서 문빙이는 간단한 어플리케이션을 만들기로 했다. 연도 진행바라는 것인데, 이번 해가 얼마나 지났는지를 보여주는 것이다.

오늘 날짜가 주어진다. 이번 해가 몇%지났는지 출력하는 프로그램을 작성하시오.

입력
첫째 줄에 Month DD, YYYY HH:MM과 같이 주어진다. Month는 현재 월이고, YYYY는 현재 연도이다. 숫자 네자리이다. DD, HH, MM은 모두 2자리 숫자이고, 현재 일, 시, 분이다.

Month는 January, February, March, April, May, June, July, August, September, October, November, December 중의 하나이고, 연도는 1800보다 크거나 같고, 2600보다 작거나 같다. 항상 올바른 날짜와 시간만 입력으로 주어진다.

출력
첫째 줄에 문제의 정답을 출력한다. 절대/상대 오차는 10-9까지 허용한다.

예제 입력 1 
May 10, 1981 00:31
예제 출력 1 
35.348363774733635
예제 입력 2 
January 01, 2008 00:00
예제 출력 2 
0.0
예제 입력 3 
December 31, 2007 23:59
예제 출력 3 
99.99980974124807
예제 입력 4 
July 02, 2007 12:00
예제 출력 4 
50.0
예제 입력 5 
July 02, 2008 00:00
예제 출력 5 
50.0
예제 입력 6 
January 31, 1900 00:47
예제 출력 6 
8.228120243531203
힌트
평년일 때, 각 달은 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31일이 있다. 윤년에는 2월이 29일이다. 윤년은 그 해가 400으로 나누어 떨어지는 해 이거나, 4로 나누어 떨어지면서, 100으로 나누어 떨어지지 않는 해 일때이다. 지역에 따른 서머타임은 고려하지 않는다.
"""

# 3. 프롬프트 템플릿 정의
# f-string 대신, 나중에 교체할 자리 표시자(__PROBLEM_TEXT__)를 사용합니다.
prompt_template = """
You are an intelligent assistant that analyzes programming problems and structures them into a specific JSON format.
Analyze the following problem text and extract all necessary information.

Based on the content, you MUST also suggest a "hint" (the relevant algorithm category in Korean) and a "stars" rating (an integer from 1 to 10 based on difficulty).

The final output MUST be ONLY a JSON object formatted exactly like this example, enclosed in ```json ... ```:

```json
{
  "id": 1000,
  "title": "A+B",
  "description": "두 정수 A와 B를 입력받은 다음, A+B를 출력하는 프로그램을 작성하시오.",
  "hint": "기본 입출력",
  "stars": 1,
  "time_limit": 1,
  "memory_limit": 128,
  "testcases": [
    {
      "input": "1 2",
      "output": "3"
    }
  ]
}
````

## Here is the problem text to analyze:

PROBLEM_TEXT

"""

# 4\. 템플릿에 문제 텍스트를 안전하게 삽입

final_prompt = prompt_template.replace("PROBLEM_TEXT", problem_text)

def generate_problem_json():
  print("Gemini API를 사용하여 문제 분석을 시작합니다...")
  try:
  # 최종적으로 완성된 프롬프트를 API에 전달
      response = model.generate_content(final_prompt)

      json_text = response.text.strip().replace("json", "").replace("```", "").strip()
      parsed_data = json.loads(json_text)
      pretty_json = json.dumps(parsed_data, indent=2, ensure_ascii=False)

      print("\n" + "="*50)
      print("✅ 분석 완료! 아래 내용을 problems.json에 추가하세요:")
      print("="*50)
      print(pretty_json)
      print("\n" + "="*50)

  except Exception as e:
      print(f"\nAPI 요청 중 오류가 발생했습니다: {e}")
      print("API 키가 올바르게 입력되었는지, 인터넷 연결이 정상적인지 확인해주세요.")


generate_problem_json()
