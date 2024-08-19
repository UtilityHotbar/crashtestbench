from openai import OpenAI
from mcanswer import get_mc_answer_simple
import os
import pickle
import threading
import logging
from multiprocessing.pool import ThreadPool

MAX_THREADS= 10

scores = {}

logic_prompt = 'You are a clever logician who can solve any logic problem. This is description of a problem setup involving animals:\n\nSETUP:\n%SETUP%\n\nHere is the problem:\n\n%PROBLEM%\n\nRemember to think step by step!'

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def answer_question(question,qid):
    qid = qid.replace('/', '-')
    logging.info('Starting question thread for qid '+qid)
    setup, problem, opts, answer = question
    print(setup, problem, opts, answer)
    opts.append('None of the Above')
    full_q = logic_prompt.replace('%SETUP%',setup).replace('%PROBLEM%', problem)
    full_a, a = get_mc_answer_simple(full_q, opts, return_cand=True) 
    with open(f'logs/{qid}.txt', 'w') as f:
        f.write(full_a+'\n\n'+a)
    print(full_a, a, answer)
    if a == answer:
        scores[depth] += 1

for thing in os.scandir('question_pickles'):
    if thing.is_file():
        with open(thing.path, 'rb') as f:
            data = pickle.load(f)
        depth = thing.path
        print(f'TESTING DEPTH {depth}')
        scores[depth] = 0

        i = 0
        master_threads = []
        for question in data:
            i += 1
            if i > MAX_THREADS:
                logging.warning('Reached max request thread count')
                break
            x = threading.Thread(target=answer_question, args=(question, depth+'-'+str(i)))
            master_threads.append(x)
        logging.info('Waiting for data...')
        for thread in master_threads:
            thread.start()

        for thread in master_threads:
            thread.join()

            
print(scores)
with open('results.pickle', 'wb') as f:
    pickle.dump(scores, f)
