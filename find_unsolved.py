import time
import os
from bs4 import BeautifulSoup
import requests

# Taking the handles of the users and storing them in a list
users_number = int(input('Please enter the number of users: '))
users = []
print('Please enter the users handles (one handle per each line): ')
for i in range(0, users_number):
    user = input()
    users.append(user)
print('')

# Taking the range for the problems difficulty
print('Please enter the range for the problems difficulty,\nEnter 0 in the min and max difficulty if you do not want to filter problems by difficulty')
min_difficulty = int(input('Minimum difficulty: '))
max_difficulty = int(input('Maximum difficulty: '))
if min_difficulty == 0 and max_difficulty == 0:
    max_difficulty = 5000
print('')

# Taking the problem topic
print('Please enter the topic of the problems you need.')
print('Enter (no) without brackets if you do not want to filter the problems with topic')
topic = input('Enter the topic name (exactly as it is written on codeforces): ')
if topic == 'no':
    topic = ''
print('')

# Storing the solved or tried problems from at least one user
solvedOrTried = set()
for user in users:
    print(f'Collecting solved problems of the user ({user})')
    pagination = requests.get(f'https://codeforces.com/submissions/{user}/page/1').text
    soup = BeautifulSoup(pagination, 'lxml')
    manyPages = soup.find_all('span', class_='page-index')
    number_of_pages = 0
    if len(manyPages) == 0:
        number_of_pages = 1
    else:
        number_of_pages = int(manyPages[-1].text)
    number_of_pages += 1
    # iterate over the pages of submissions of the user
    for page in range(1, number_of_pages):
        print(f'Collecting solved Problems for user {user}...{int((page * 100) / number_of_pages)}%')
        html = requests.get(f'https://codeforces.com/submissions/{user}/page/{page}').text
        soup = BeautifulSoup(html, 'lxml')
        submissions = soup.find_all('td')

        #iterate over user's submissions in the current page
        for idx, submission in enumerate(submissions):
            if idx % 8 == 3:
                problem_letter = ''
                problem_number = ''
                problem = str(submission.a['href'])
                while problem[-1] is not '/':
                    problem_letter += problem[-1]
                    problem = problem[:-1]
                problem_letter = problem_letter[::-1]
                for c in problem:
                    if c >= '0' and c <= '9':
                        problem_number += c
                solvedOrTried.add(problem_number + problem_letter)
    print(f'Done collecting ({user}) solved problems')
    print('')
# done adding problems of all users

# edit the topic name to be replaced in link
if len(topic) > 0:
    topic += ','
topic = topic.replace(' ', '%20')

# calculating the number of pages of the filtered problems
pagination = requests.get(f'https://codeforces.com/problemset/page/1/?tags={topic}{min_difficulty}-{max_difficulty}').text
soup = BeautifulSoup(pagination, 'lxml')
manyPages = soup.find_all('span', class_='page-index')
number_of_pages = 0
if len(manyPages) == 0:
    number_of_pages = 1
else:
    number_of_pages = int(manyPages[-1].text)
number_of_pages += 1

# finding the problems which is not solved by anyone
print('Collecting problems...')
saved_problems_cnt = 0
with open(f'Unsolved Problems.txt', 'w') as f:
    for page in range(1, number_of_pages):
        print(f'Collecting Problems... {int((page * 100) / number_of_pages)}%')
        filtered_problemset = f'https://codeforces.com/problemset/page/{page}?tags={topic}{min_difficulty}-{max_difficulty}'
        html = requests.get(filtered_problemset).text
        soup = BeautifulSoup(html, 'lxml')
        problemList = soup.find_all('td')
        for idx, curProblem in enumerate(problemList):
            if idx % 5 == 0:
                problem_name = curProblem.text.strip()
                if problem_name not in solvedOrTried:
                    saved_problems_cnt += 1
                    problem_link = curProblem.a['href']
                    problem_link = f'https://codeforces.com' + problem_link
                    f.write(problem_name)
                    f.write('\n')
                    f.write(problem_link)
                    f.write('\n')
                    f.write('\n')
print(f'Done, please find the {saved_problems_cnt} problems in the saved file.')
print('')
