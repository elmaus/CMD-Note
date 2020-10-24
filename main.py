import itertools
import pickle
from fuzzywuzzy import fuzz



div = '======================================'


intro = [
    ''
    '"--search" space "query title" to search code...',
    '"--list space "category" to list all code from a category...',
    '"--add" space "category" to add new code directory...',
    '"--setting to set the app'
    '"--exit" to exit the program...',
    ''
]

data = {}

def load_data():
    global data
    with open('data.pickle', 'rb') as pickle_file:
        data = pickle.load(pickle_file)

def save(category, title, content):
    global data

    try:
        data[category][title] = content
    except:
        data[category] = {}
        data[category][title] = content

    with open('data.pickle', 'wb') as pkl:
        pickle.dump(data, pkl)

    return '{} for {} category has been saved'.format(title, category)


def get_line_text_content():
    current_line = 1

    # python generator to generate sequence of input function for the user
    for l in itertools.count():
        if l < 99:
            ind = current_line if current_line > 9 else '0{}'.format(current_line)
            current_line += 1
            inp = input('[{}]: '.format(ind))

            if '--back' in inp:

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
                        print("Error! line number {} doesn't exist".format(back_to))
                        yield 'pass'
                except:
                    print('Error! {} invalid input for a number')
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
                result.append((title, data[category][title]))

    if len(result) > 0:

        print('Result for {}\n'.format(text))
        for i, r in enumerate(result):
            print('{}. {}'.format(i + 1, r[0]))
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
                    return '{}\n{}\n\n{}\n{}'.format(div, result[index - 1][0], result[index - 1][1], div)
                else:
                    print("{} is not in the choices".format(pick))
            except:
                print("{} is not a number".format(pick))
    else:
        return 'No {} in the data...'.format(text)

def add(text):

    content = []
    try:
        category = text.split(' ')[1]
        if category == '':
            return 'Error! You must include a category separated by space...'
    except:
        return 'Error! You must include a category separated by space...'

    print('Type --save to save your content\n')

    title = ''
    has_title = False
    while not has_title:
        title = input('TITLE: ')
        if title == '':
            print('Error! TITLE needs an input...')
        else:
            has_title = True


    print('CONTENT:')

    for i in get_line_text_content():
        if i != '--save' and i != 'pass':
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
                return 'add aborted!'
        elif i == '--exit':
            return 'aborted!'
        else:
            text = ''.join(content)
            print('\n==========================================\n')
            print(text + '\n')
            answered = False
            while not answered:
                question_to_save = input('Save the content? y/n: ')
                if question_to_save == 'y':
                    answered = True
                    return save(category, title, ' '.join(content))
                elif question_to_save == 'n':
                    answered = True
                    return 'Add aborted!'

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
                index = int(pick) - 1
                if index > 0 and index < len(list_of_titles):
                    done = True
                    return "{}\n\n{}\n{}".format(div, data[category][list_of_titles[index]], div)
                else:
                    print('[Error] index is not in a list of titles...')
            except:
                print('[Error] {} is not a number'.format(pick))
    else:
        return 'No content for this category'


def get_directories():
    dir = ''
    for key in data:
        dir += '{}\n'.format(key)

    return dir


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
                    confirm = input('Are you sure you want to delete {}? y/n: '.format(title))
                    if confirm == 'y':
                        del data[category][title]
                        with open('data.pickle', 'wb') as pkl:
                            pickle.dump(data, pkl)
                        done = True
                        return '{} has been deleted...'.format(title)
                    elif confirm == 'n':
                        done = True
                        return 'Deleting {} is aborted...'.format(title)
    return 'No content for {}'.format(title)


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
        elif command == '--exit':
            print('bye!')
            return
        else:
            print('command error!\n')
            for itr in intro:
                if intro.index(itr) > 0:
                    print(itr)
            print()

            yield "{} command doesn't exist...".format(command)


def main():
    for itr in intro:
        print(itr)

    for response in get_user_command():
        print(response)
        if response == 'bye':
            break


if __name__ == '__main__':
    load_data()
    print('\n===============  Welcome to CMD Note  ===============\n\n')
    main()
