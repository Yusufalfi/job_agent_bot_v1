import truststore
truststore.inject_into_ssl()

import os
from dotenv import load_dotenv
from groq import Groq, APIConnectionError, APIStatusError

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("ERROR: GROQ_API_KEY tidak ditemukan di .env")
    raise SystemExit(1)

try:
    client = Groq(api_key=api_key, max_retries=0)

    print("Mencoba koneksi ke Groq...")

    # response = client.chat.completions.create(
    #     model="openai/gpt-oss-20b",
    #     messages=[
    #         {"role": "user", "content": "Balas hanya: KONEKSI BERHASIL"}
    #     ],
    #     max_completion_tokens=50,
    # )

    
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": "ap itu ssl"
            }
        ],
        max_completion_tokens=1024,
        reasoning_effort="low",
        include_reasoning=False,
    )

    print("FINISH REASON:", response.choices[0].finish_reason)
    print("CONTENT:", repr(response.choices[0].message.content))
    print("USAGE:", response.usage)


except APIConnectionError as e:
    print("KONEKSI GAGAL")
    print("Detail:", repr(e.__cause__))

except APIStatusError as e:
    print("API MENOLAK REQUEST")
    print("HTTP Status:", e.status_code)
    print("Detail:", e.response.text)

except Exception as e:
    print("ERROR:", repr(e))
