__author__ = 'Jun'

import os
import sys
import re
import csv


def file_tail(f, num_lines=20):
    """
    Empty lines are not considered
    :param f: file
    :param num_lines: nummber of lines
    :return: None if nummber of lines less than num_lines, otherwise lines
    """

    # for line in f:
    #     if not re.match(r'^\s*$', line):
    #         all_lines.append(line)

    all_lines = filter(lambda x: not re.match(r'^\s*$', x), f)

    if len(all_lines) < num_lines:
        return None

    return all_lines[-num_lines:]


def get_test_params(filename):
    file_params = filename.split("-")

    if len(file_params) != 7:
        return None

    test_params = 16 * [0]
    test_params_dict = {"dl1": 5 * [0], "il1": 5 * [0], "dl2": 5 * [0], "il2": 5 * [0]}

    for one_flag in file_params[0:4]:
        name = one_flag[6:9]
        shadow_name = one_flag[9:12]

        if shadow_name == "ul1":
            test_params_dict["dll"] = test_params_dict["il1"]
            test_params_dict["il1"][0] = "u"
            continue

        if shadow_name == "ul2":
            test_params_dict["dl2"] = test_params_dict["il2"]
            test_params_dict["il2"][0] = "u"
            continue

        params = one_flag[12:].split(r'\:')

        for index, value in enumerate(params):
            test_params_dict[name][index + 1] = value

    return file_params


def run_all_processes():
    if len(sys.argv) < 3:
        print "python post_process.py outputs_dir csv_file"
        sys.exit(0)

    outputs_dir = sys.argv[1]
    csv_file = open(sys.argv[2], 'wb')
    csv_writer = csv.writer(csv_file)

    for filename in os.listdir(outputs_dir):
        file_relative_path = os.path.join(outputs_dir, filename)
        test_params = get_test_params(filename)

        if test_params is None:
            continue

        f = open(file_relative_path, 'rb')
        lines = file_tail(f, 58)

        if lines is None:
            continue

        test_metrics = [line.split(r'[\s\t]+')[1] for line in lines]
        csv_writer.writerow(test_params + test_metrics)


if __name__ == '__main__':
    run_all_processes()