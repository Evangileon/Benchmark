__author__ = 'Jun'

from subprocess import Popen
from multiprocessing import Pool
import sys

NUM_PROCS = 10

USER_HOME = "/home/004/j/jx/jxy132330/"

PROJECT_PATH = USER_HOME + "project/cs6304/"

BENCHMARK_PATH = PROJECT_PATH + "benchmarks/"

SIMPLE_CACHE_PATH = PROJECT_PATH + "simplesim-3.0/"

OUTPUT_DIR = PROJECT_PATH + "outputs/"

SIM = SIMPLE_CACHE_PATH + "sim-cache"

TEST_SET = [
    "cc1.alpha",
    "anagram.alpha",
    "go.alpha",
]

BIG_O = {
    "cc1.alpha": "-O benchmarks/1stmt.i",
    "anagram.alpha": BENCHMARK_PATH + "words < benchmarks/anagram.in",
    "go.alpha": "50 9 benchmarks/2stone9.in"
}

CACHE_L1_AVAILABLE = 256  # 256K
CACHE_L2_AVAILABLE = 1024  # 1M

CACHE_L1_D = [128, 256]
CACHE_L2_D = [512, 1024]

CACHE_SEPARATE_BOUND = 0.1  # both upper bound and lower bound are 10% of available
CACHE_SEPARATE_SAMPLES = 128  # add 0.01 * available to next configuration

WAYS = [1, 2, 4]
BLOCK_SIZES = [32, 64]

REPLACE_POLICIES = ["l", "f", "r"]

# OUTPUT_DIR = "benchmark_confs"


class CacheConf(object):
    """
    Class for one cache configuration
    """

    def __init__(self, name, nsets, bsize, assoc, repl):
        self.name = name
        self.nsets = nsets
        self.bsize = bsize
        self.assoc = assoc
        self.repl = repl

    def to_conf_string(self):
        return "-cache:" + self.name + " " + ":".join([self.name, self.nsets, self.bsize, self.assoc, self.repl])


def generate_one_conf(l1_data, l1_inst, l2_data, l2_inst, l1_bsize, l2_bsize, l1_way, l2_way, l1_repl, l2_repl):
    l1_d_nsets = l1_data * 1024 / l1_bsize
    l2_d_nsets = l2_data * 1024 / l2_bsize
    l1_i_nsets = l1_inst * 1024 / l1_bsize
    l2_i_nsets = l2_inst * 1024 / l2_bsize

    if l1_data == 0:
        return None
    elif l1_inst == 0:
        # L1 unified
        l1_inst_flags = "-cache:il1 dl1"
        l1_data_flags = "-cache:dl1 ul1:" + ":".join(str(e) for e in [l1_d_nsets, l1_bsize, l1_way, l1_repl])
    else:
        # L1 separate
        l1_inst_flags = "-cache:il1 il1:" + ":".join(str(e) for e in [l1_i_nsets, l1_bsize, l1_way, l1_repl])
        l1_data_flags = "-cache:dl1 dl1:" + ":".join(str(e) for e in [l1_d_nsets, l1_bsize, l1_way, l1_repl])

    if l2_data == 0:
        return None
    elif l2_inst == 0:
        # L2 unified
        l2_inst_flags = "-cache:il2 dl2"
        l2_data_flags = "-cache:dl2 ul2:" + ":".join(str(e) for e in [l2_d_nsets, l2_bsize, l2_way, l2_repl])
    else:
        # L2 separate
        l2_inst_flags = "-cache:il2 il2:" + ":".join(str(e) for e in [l2_i_nsets, l2_bsize, l2_way, l2_repl])
        l2_data_flags = "-cache:dl2 dl2:" + ":".join(str(e) for e in [l2_d_nsets, l2_bsize, l2_way, l2_repl])

    if l1_inst == 0 and l2_inst == 0:
        # L1, L2 both are unified
        l2_inst_flags = "-cache:il2 none"
        command_line = " ".join(str(e) for e in [l1_inst_flags, l1_data_flags, l2_data_flags, l2_inst_flags])
    else:
        command_line = " ".join(str(e) for e in [l1_inst_flags, l1_data_flags, l2_inst_flags, l2_data_flags])

    command_line += " " + "-tlb:itlb none -tlb:dtlb none"

    return command_line


def run_all_confs():
    po = Pool(8)
    confs = []

    for l1_data in CACHE_L1_D:
        # for L1 cache, 0 means unified
        l1_inst = CACHE_L1_AVAILABLE - l1_data
        for l2_data in CACHE_L2_D:
            # for L2 cache, 0 means unified
            l2_inst = CACHE_L2_AVAILABLE - l2_data
            for l1_bsize in BLOCK_SIZES:
                for l2_bsize in BLOCK_SIZES:
                    for l1_way in WAYS:
                        for l2_way in WAYS:
                            for l1_repl in REPLACE_POLICIES:
                                for l2_repl in REPLACE_POLICIES:
                                    conf_params = generate_one_conf(l1_data, l1_inst,
                                                                    l2_data, l2_inst,
                                                                    l1_bsize, l2_bsize,
                                                                    l1_way, l2_way,
                                                                    l1_repl, l2_repl)
                                    if conf_params is not None:
                                        # po.(run_all_benchmarks_for_one_conf, [conf_params])
                                        # time.sleep(3)
                                        confs.append(conf_params)
    results = po.map(run_all_benchmarks_for_one_conf, confs)
    print results


def run_all_benchmarks_for_one_conf(conf_params):
    count = 1
    for test_case in TEST_SET:
        case = BENCHMARK_PATH + test_case
        output = OUTPUT_DIR + conf_params.replace(" ", "")[1:] + "-" + test_case + ".txt"
        count += 1
        args_to_call = [SIM, "-redir:sim", output] + conf_params.split(" ") + [case] + BIG_O[test_case].split(" ")
        print " ".join(args_to_call)
        p = Popen(args_to_call)
        p.wait()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        OUTPUT_DIR = sys.argv[1]

    run_all_confs()