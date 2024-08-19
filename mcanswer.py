import os
from openai import OpenAI
import tiktoken
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

MODEL_NAME = 'gpt-4-turbo'

MASKED_ANSWER_PROMPT = '%QUESTION%'

EXTRACT_ANSWER_PROMPT = 'You are a clever assistant looking over a partial answer transcript from a qna session. The last segment of an answer provided to a multiple choice is in the <answer> tags:\n\n<answer>\n%RESPONSE%\n</answer>\n\nWhat is their final answer? The valid answers are: \n%TRUE_ANSWERS%\n\n Respond with their final answer only.'

def num_tokens_from_string(string: str, encoding_name: str ="cl100k_base") -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def get_mc_answer_simple(question: str, answers: list, iterations=None, tries_per_iteration=5, client=client, return_cand=False):
    answer_prefs = {}
    answers = [_.lower() for _ in answers]
    for answer in answers:
        answer_prefs[answer] = 0
    if not iterations:
        iterations = len(answers)+1
    final_prompt = MASKED_ANSWER_PROMPT.replace('%QUESTION%', question)
    extract_prompt = EXTRACT_ANSWER_PROMPT.replace('%TRUE_ANSWERS%', ', '.join(answers))
    for iteration in range(iterations):
        attempts_remaining = tries_per_iteration
        candidate = None
        while True:
            completion = client.chat.completions.create(model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": final_prompt},
                    ],
                temperature=1.0,
                max_tokens=num_tokens_from_string(final_prompt)+1000)
            candidate = completion.choices[0].message.content
            extract_prompt = extract_prompt.replace('%RESPONSE%', ' '.join(candidate.split(' ')[-50:]))
            next_completion = client.chat.completions.create(model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": extract_prompt}
                    ],
                temperature=1.0,
                max_tokens=num_tokens_from_string(extract_prompt)+1000)
            final_answer = next_completion.choices[0].message.content.lower().strip()
            if final_answer in answers:
                break
            else:
                attempts_remaining -= 1
            if attempts_remaining == 0:
                raise RuntimeError(f'Randomised prompting failed to elicit valid multiple choice response. \n\nThe last returned response was: ${final_answer}')
        answer_prefs[final_answer] += 1
    if return_cand:
        return candidate, max(answer_prefs, key=answer_prefs.get)
    return max(answer_prefs, key=answer_prefs.get)  # get the favoured answer by the LLM
