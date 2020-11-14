import itertools
import pickle
import time
from fuzzywuzzy import fuzz
import math



div = '======================================================================='


intro = [
    ''
    '"--dir" to list out all categories...',
    '"--list space "category" to list out all notes from the category...',
    '"--add" space "category" to add new code directory...',
    '"--search" space "query title" to search code...',
    '"--calc" for calculator mode...',
    '"--exit" to exit the program...',
    ''
]
version = '1.0.0'
new_content_reminders = 'Reminders:\n--save to save your content.\n--exit to exit.\nContent take only 100 lines\n'

data = {}

def load_data():
    global data
    with open('data.pickle', 'rb') as pickle_file:
        data = pickle.load(pickle_file)

def calculate(text):
    error = "ERROR! Must be a string..."
    commands = ['eval', 'sin', 'cos', 'tan', 'asin', 'acos', 'atan',
    'factorial', 'degrees', 'radians']
    print('For the list of commands, type commands...')

    for i in itertools.count():

        inp = input(">>> ")
        part1 = inp.split(' ')[0]
        part2 = " ".join(inp.split(' ')[1:])

        
        try:
            if part1 == 'commands':
                for com in commands:
                    print(com)
            elif part1 == 'eval':
                yield eval(part2)
            elif part1 == 'sin':
                yield math.sin(int(part2))
            elif part1 == 'cos':
                yield math.cos(int(part2))
            elif part1 == 'tan':
                yield math.tan(int(part2))
            elif part1 == 'asin':
                yield math.asin(int(part2))
            elif part1 == 'acos':
                yield math.acos(int(part2))
            elif part1 == 'atan':
                yield math.atan(int(part2))
            elif part1 == 'factorial':
                yield math.factorial(int(part2))
            elif part1 == 'radians':
                yield math.randians(int(part2))
            elif part1 == 'degrees':
                yield math.degrees(int(part2))
            elif part1 == '--exit':
                return '--exit'
            else:
                yield 'ERROR!: There is no command for {}'.format(part1)

        except Exception as e:
                yield e

        
def calculator(text):
    for i in calculate(text):
        if i == '--exit':
            return 'Calculator mode exited...'
        else:
            print(i)

def save(category, title, content):
    global data

    try:
        data[category][title] = content
    except:
        data[category] = {}
        data[category][title] = content

    with open('data.pickle', 'wb') as pkl:
        pickle.dump(data, pkl)

    return '"{}" for "{}" category has been saved'.format(title, category)


def get_line_text_content():
    current_line = 1

    # python generator to generate sequence of input function for the user
    for l in itertools.count():
        if l < 99:
            ind = current_line if current_line > 9 else '0{}'.format(current_line)
            current_line += 1
            inp = input('[{}]: '.format(ind))

            if '--exit' in inp:
                yield '--exit'
            elif '--back' in inp:

                """
                    --back is a command that allows to overwrite previous lines with the corresponding number
                    ex:
                    --back 2 # all you have written in line greater than 2 will be overwritten
                """

                back_to = inp.split(' ')[-1]
                try:
                    if int(back_to) < current_line and current_line > 1:
                        current_line = int(back_to)
                        yield '--back {}'.format(back_to)
                    else:
                        current_line -= 1
                        print('Error! line number "{}" do not exist'.format(back_to))
                        yield 'pass'
                except:
                    print('Error! "{}" is invalid input for a number'.format(back_to))
                    current_line -= 1
                    yield 'pass'
            else:
                yield inp
        else:
            yield 'exceed'


def search(command):
    text = ' '.join(command.split(' ')[1:])
    result = []
    for category in data:
        for title in data[category]:
            if fuzz.token_set_ratio(text, title) > 50:
                result.append((title, data[category][title], category))

    if len(result) > 0:

        print('Result for "{}"...\n'.format(text))
        for i, r in enumerate(result):
            print('{}. {} ({})'.format(i + 1, r[0], r[2]))
        print('\n')

        done = False

        while not done:
            # asking the user to enter the number corresponding with the title wanted to be open
            pick = input('Enter the key number: ')

            try:
                index = int(pick)
                if index > 0 and index <= len(result):
                    done = True
                    # returning the content with title and dividing line
                    return '{}\nTitle: {}\n\n{}\n{}'.format(div, result[index - 1][0], result[index - 1][1], div)
                else:
                    print('"{}" is not in the choices...'.format(pick))
            except:
                print('"{}" is not a number...'.format(pick))
    else:
        return 'No "{}" in the data...'.format(text)

def add(text):

    content = []
    try:
        category = text.split(' ')[1]
        if category == '':
            return 'Error! You must include a category separated by space...'
    except:
        return 'Error! You must include a category separated by space...'

    print(new_content_reminders)

    title = ''
    has_title = False
    while not has_title:
        title = input('TITLE: ')
        if title == '':
            print('Error! TITLE needs an input...')
        elif title == '--exit':
            return "{}\n".format(div)
        else:
            has_title = True


    print('CONTENT:')

    for i in get_line_text_content():
        if i == '--exit':
            return '\n{}\n'.format(div)
        elif i != '--save' and i != 'pass':
            content.append('{}\n'.format(i))

            if i.split(' ')[0] == '--back': # going back to previous
                go_bck_to = int(i.split(' ')[1])
                if go_bck_to == 1:
                    print('Warning! Jumped back to line {} and the rest is deleted...'.format(go_bck_to))
                    content = []
                else:
                    print('Warning! Jumped back to line {} and the rest is deleted...'.format(go_bck_to))
                    content = list(content[:go_bck_to])

        elif i == 'pass':
            continue

        elif i == 'exceed':
            warning = input('Content reached the line limit. Save it anyway? y/n: ')
            if warning == 'y':
                save(category, title, ' '.join(content))
            elif warning == 'n':
                add(text)
            else:
                return 'add aborted!...'
        else:
            text = ''.join(content)
            print('\n{}\n'.format(div))
            print(text + '\n')
            answered = False
            while not answered:
                question_to_save = input('Save the content? y/n: ')
                if question_to_save == 'y':
                    answered = True
                    return save(category, title, ' '.join(content))
                elif question_to_save == 'n':
                    answered = True
                    return 'Add aborted!...'

def get_list(text):
    category = ' '.join(text.split(' ')[1:])
    list_of_titles = []

    for titles in data[category]:
        list_of_titles.append(titles)

    if len(list_of_titles) > 0:
        for i, titles in enumerate(list_of_titles):
            print('{}. {}'.format(i + 1, titles))
        print('\n')
        done = False

        while not done:
            pick = input('[Enter the index] What content do you want to open?: ')
            try:
                index = int(pick)
                if index > 0 and index <= len(list_of_titles):
                    done = True
                    return "{}\nTitle: {}\n\n{}\n{}".format(div, list_of_titles[index - 1], data[category][list_of_titles[index - 1]], div)
                else:
                    print('[Error] index is not in a list of titles...')
            except:
                if pick == '--exit':
                    return '{}\n'.format(div)
                else:
                    print('[Error] "{}" is not a number'.format(pick))
    else:
        return 'No content for this category...'


def get_directories():
    dir = []
    for key in data:
        dir.append(key)
    print("Total Categories: {}".format(len(dir)))
    return '{}\n\nType --list category to list out all the content'.format('\n'.join(dir))


def delete_content(text):
    global data
    title = ' '.join(text.split(' ')[1:])
    if title == "":
        print("Can't delete empty title...")
        return 'type --del title'

    for category in data:
        for t in data[category]:
            if t == title:
                print('{}\n{}\n{}'.format(div, data[category][title], div))
                done = False
                while not done:
                    confirm = input('Are you sure you want to delete "{}"? y/n: '.format(title))
                    if confirm == 'y':
                        del data[category][title]
                        with open('data.pickle', 'wb') as pkl:
                            pickle.dump(data, pkl)
                        done = True
                        return '"{}" has been deleted...'.format(title)
                    elif confirm == 'n':
                        done = True
                        return 'Deleting "{}" is aborted...'.format(title)
    return 'No content for "{}"'.format(title)


def get_user_command():
    for i in itertools.count():
        text = input('>>> ')
        command = text.split(' ')[0]

        if command == '--add':
            yield add(text)
        elif command == '--search':
            yield search(text)
        elif command == '--dir':
            yield get_directories()
        elif command == '--list':
            yield get_list(text)
        elif command == '--del':
            yield delete_content(text)
        elif command == '--calc':
            yield calculator(text)
        elif command == '--exit':
            print('bye!')
            return
        else:
            print('command error!\n')
            for itr in intro:
                if intro.index(itr) > 0:
                    print(itr)
            print()

            yield '"{}" command error...'.format(command)


def main():
    for itr in intro:
        print(itr)

    for response in get_user_command():
        print(response)
        if response == 'bye':
            time.sleep(1)
            break


if __name__ == '__main__':
    load_data()
    print('\n===============  Welcome to CMD Note version: {}  ===============\n\n'.format(version))
    input('Press enter to start...')
    print('\n\n')
    main()
