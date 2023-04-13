## OPENAI API(GPT)를 활용한 Telegram Bot 설치하기

1. 본 스크립트는 Linux(우분투 20.04LTS)를 기반으로 설치하도록 되어 있으나, 일부 코드 변경을 통해 Windows에서도 활용 가능하다.

2. git을 설치하고 아래와 같이 해당 repository를 local로 cloning한다.
```python
apt install git -y
cd {패키지를 받을 경로}
git clone https://github.com/joongon/tele_gptbot.git 
```

3. 필요한 Package를 설치한다.
```python
pip install -r requirements
```

4. python 코드에 필요한 접속 정보(telegram chat_id, TOKEN, OPENAPI API KEY)를 입력한다.
또한, Telegram 대화시 bot을 호출할 trigger 키워드도 임의로 입력한다.


