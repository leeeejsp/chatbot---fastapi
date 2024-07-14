import google.generativeai as genai
import os
from config import GENAI_API_KEY

genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# response = model.generate_content("한국말로 해줘. 음식추천점 ")
# print(response.text)

chat = model.start_chat(history=[])

# 첫 번째 질문 내용 작성
# 첫 번째 질문 내용을 입력해주세요. : 초등학교 1학년이 배우는 수학은 어떤 내용?
q1 = input("첫 번째 질문 내용을 입력해주세요. : ")


# 첫 번째 질문 내용에 대한 답변 응답
response = chat.send_message(q1)
print("첫 번째 답변 : " + response.text)

# 두 번째 질문 내용 작성
# 방금 내가 질문한 내용은?
q2 = input("두 번째 질문 내용을 입력해주세요. : ")


# 두 번째 질문 내용에 대한 답변 응답
response = chat.send_message(q2)
print("두 번째 답변 : " + response.text)

print("채팅 내역 확인")
print(chat.history)