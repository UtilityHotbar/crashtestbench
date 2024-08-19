import random
import os
import copy
import pickle

logic_prompt = 'You are a clever logician who can solve any logic problem. This is description of a problem setup involving animals:\n\nSETUP:\n%SETUP%\n\nHere is the problem:\n\n%PROBLEM%\n\nRemember to think step by step!'

animals = ['cat', 'dog', 'rat', 'bat', 'whale', 'chipmunk', 'sloth', 'turtle', 'fish', 'sheep', 'cow', 'monkey']

def GenerateSimpleLogicSequence(width=3, depth=1):
    if depth > width:
        raise RuntimeError('Depth > width')
    logic_seq = []
    shuffled_animals = copy.copy(animals)
    random.shuffle(shuffled_animals)
    for i in range(width):
        next_animal = shuffled_animals.pop()
        logic_seq.append(next_animal)
    setup = ''
    for j in range(width):
        if j == width-1:
            break
        else:
            k = j+1
        setup += f'The {logic_seq[j]} eats the {logic_seq[k]}. '
    
    problem = 'What did '
    curr_depth = -1-depth
    selected_animal = logic_seq[curr_depth]
    orig_prey_animal = logic_seq[curr_depth+1]

    while -curr_depth <= width:
        hunter_animal = logic_seq[curr_depth]
        prey_animal = logic_seq[curr_depth+1]

        problem += 'the thing that ate '
        curr_depth -= 1


    problem += 'the ' + orig_prey_animal + ' eat?'

    print(setup, problem, prey_animal)
    return setup, problem, logic_seq, prey_animal

if __name__ == '__main__':
    for d in range(2, 11):
        final = ''

        print('DEPTH',d)
        data = []
        for _ in range(20):
            s, p, l, pr = GenerateSimpleLogicSequence(width=d)
            final += f'{_}\n{s}\n{p}\n{",".join(l)}\n{pr}\n'
            data.append([s,p,l,pr])
        print(logic_prompt.replace('%SETUP%',s).replace('%PROBLEM%', p))
        print(pr)
        with open(f'questions/{d}.txt', 'w') as f:
            f.write(final)
        with open(f'question_pickles/{d}.pickle', 'wb') as g:
            pickle.dump(data, g)
