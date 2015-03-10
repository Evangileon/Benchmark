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
    all_lines = filter(lambda x: not re.match(r'^\s*$', x), f)

    if len(all_lines) < num_lines:
        return None

    return all_lines[-num_lines:]


def get_test_params(filename):
    """
    Get list of configuration of a given test case identified by file name
    :param filename: output file name
    :return: list of parameters
    """
    file_params = filename.split("-")

    if len(file_params) != 7:
        return None

    test_params = []
    test_params_dict = {"dl1": 5 * [""], "il1": 5 * [""], "dl2": 5 * [""], "il2": 5 * [""]}

    for one_flag in file_params[0:4]:
        name = one_flag[6:9]
        shadow_name = one_flag[9:12]

        if name != shadow_name and not shadow_name.startswith("ul"):
            # unified cache, pointer flag
            test_params_dict[name] = test_params_dict[shadow_name]
            test_params_dict[shadow_name] = "u"
            continue
        elif name != shadow_name and shadow_name.startswith("ul"):
            # unified cache, parameters about the unified cache
            test_params_dict[shadow_name] = "u"
        else:
            # separate cache
            test_params_dict[name][0] = "d"

        # fill in the parameters, if it is a unified cache, data cache pointer to instruction cache
        params = one_flag[13:].split(':')
        for index, value in enumerate(params):
            test_params_dict[name][index + 1] = value

    # follow this order
    test_params.extend(test_params_dict["il1"])
    test_params.extend(test_params_dict["dl1"])
    test_params.extend(test_params_dict["il2"])
    test_params.extend(test_params_dict["dl2"])

    benchmark_name = file_params[6][:-4]
    test_params.append(benchmark_name)

    return test_params


def run_all_processes():
    """
    Main method
    :return: nothing
    """
    if len(sys.argv) < 3:
        print "python post_process.py outputs_dir csv_file"
        sys.exit(0)

    outputs_dir = sys.argv[1]
    csv_file = open(sys.argv[2], 'wb')
    csv_writer = csv.writer(csv_file)
    unprocessed_list_file = open("unprocessed_files.txt", 'w')

    metric_titles = ['sim_num_insn', 'sim_num_refs', 'sim_elapsed_time', 'sim_inst_rate', 'il1.accesses', 'il1.hits',
                     'il1.misses', 'il1.replacements', 'il1.writebacks', 'il1.invalidations', 'il1.miss_rate',
                     'il1.repl_rate', 'il1.wb_rate', 'il1.inv_rate', 'il2.accesses', 'il2.hits', 'il2.misses',
                     'il2.replacements', 'il2.writebacks', 'il2.invalidations', 'il2.miss_rate', 'il2.repl_rate',
                     'il2.wb_rate', 'il2.inv_rate', 'dl1.accesses', 'dl1.hits', 'dl1.misses', 'dl1.replacements',
                     'dl1.writebacks', 'dl1.invalidations', 'dl1.miss_rate', 'dl1.repl_rate', 'dl1.wb_rate',
                     'dl1.inv_rate', 'dl2.accesses', 'dl2.hits', 'dl2.misses', 'dl2.replacements', 'dl2.writebacks',
                     'dl2.invalidations', 'dl2.miss_rate', 'dl2.repl_rate', 'dl2.wb_rate', 'dl2.inv_rate',
                     'ld_text_base', 'ld_text_size', 'ld_data_base', 'ld_data_size', 'ld_stack_base', 'ld_stack_size',
                     'ld_prog_entry', 'ld_environ_base', 'ld_target_big_endian', 'mem.page_count', 'mem.page_mem',
                     'mem.ptab_misses', 'mem.ptab_accesses', 'mem.ptab_miss_rate']
    conf_titles = ['L1 Inst Unified', 'L1 Inst nsets', 'L1 Inst bsize', 'L1 Inst ways', 'L1 Inst repl',
                   'L1 Data Unified', 'L1 Data nsets', 'L1 Data bsize', 'L1 Data ways', 'L1 Data repl',
                   'L2 Inst Unified', 'L2 Inst nsets', 'L2 Inst bsize', 'L2 Inst ways', 'L2 Inst repl',
                   'L2 Data Unified', 'L2 Data nsets', 'L2 Data bsize', 'L2 Data ways', 'L2 Data repl',
                   'Benchmark Name']

    csv_writer.writerow(conf_titles + metric_titles)

    count = 0

    for filename in os.listdir(outputs_dir):
        file_relative_path = os.path.join(outputs_dir, filename)
        test_params = get_test_params(filename)

        if test_params is None:
            continue

        f = open(file_relative_path, 'rb')
        lines = file_tail(f, 58)

        if lines is None:
            unprocessed_list_file.write(filename + "\n")
            continue

        test_metrics = [line.split()[1] for line in lines]
        csv_writer.writerow(test_params + test_metrics)
        print filename + " processed"
        count += 1

    csv_file.close()
    unprocessed_list_file.close()
    print "files processed in total " + str(count)


if __name__ == '__main__':
    run_all_processes()