"""
pxutil
~~~~~

Peter Jiping Xie's personal utils.

:copyright: © 2019 by Peter Jiping Xie.
:license: MIT.
"""
# import func/classes from .pxutil here so users can them directly,
# i.e., pxutil.bash() instead of pxutl.pxutil.bash().
from .pxutil import (
    bash,
    bashx,
    trim_docstring,
    grep,
    purge,
    time2seconds,
    replace_in_file,
    normal_path,
    exit_on_exception,
    register_signal_ctrl_c,
    post,
    request,
    set_work_path,
    prepend_sys_path,
    import_any,
    ChatAPI,
    list_module_contents,
    setup_logger,
    read_env_file,
)
from .pxutil_cy import run_loop, fib
