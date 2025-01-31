FLAG_DEPENDENCY = "mm_flag_dependency"


def tag(cls, flags: dict):
    cls.mm_flags = dict()
    for flag in flags.items():
        cls.mm_flags[flag[0]] = flag[1]


def define_dependency(*args):
    def wrapper(cls):
        tag(cls, {FLAG_DEPENDENCY: {*args}})

    return wrapper
