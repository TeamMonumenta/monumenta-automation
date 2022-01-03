import os
import sys
import concurrent.futures

from minecraft.chunk_format.block_entity import BlockEntity
from minecraft.chunk_format.entity import Entity
from minecraft.util.iter_util import RecursiveMinecraftIterator, TypeMultipathMap, process_in_parallel
from minecraft.util.debug_util import NbtPathDebug

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../quarry"))
from quarry.types import nbt

def _create_structure_lambda(full_path):
    return Structure(full_path)

def _finalize_structure_lambda(structure, autosave):
    if autosave:
        structure.save()

class Structure(RecursiveMinecraftIterator, NbtPathDebug):
    """A structure, loaded from an nbt file."""
    __CLASS_UNINITIALIZED = True
    __MULTIPATHS = TypeMultipathMap()

    def __init__(self, path: str, path_debug=None):
        if type(self).__CLASS_UNINITIALIZED:
            self._init_multipaths(type(self).__MULTIPATHS)
            type(self).__CLASS_UNINITIALIZED = False
        self._multipaths = type(self).__MULTIPATHS

        self.path = path
        name = os.path.basename(path)
        self._structure_name = os.path.splitext(name)[0]

        self._nbtfile = nbt.NBTFile.load(path)

        self.nbt_path_init(self._nbtfile.root_tag, None, self, self._nbtfile.root_tag.at_path('"".DataVersion').value)

    def _init_multipaths(self, multipaths):
        super()._init_multipaths(multipaths)
        multipaths[BlockEntity] |= frozenset({
            '"".blocks[].nbt',
        })
        multipaths[Entity] |= frozenset({
            '"".entities[]',
        })

    def get_debug_str(self):
        return f"structure {self.path}"

    @property
    def name(self):
        return self._structure_name

    @property
    def root_tag(self):
        return self.nbt

    @property
    def pos(self):
        """Structures have no inherent position"""
        return None

    def __str__(self):
        return f'Structure({self._structure_name})'

    def __repr__(self):
        return f'Structure(self.root_tag.to_mojangson())'

    def save(self):
        self._nbtfile.save(self.path)

    @classmethod
    def iter_structures_parallel(cls, path, func, err_func, num_processes=4, autosave=False, additional_args=(), initializer=None, initargs=()):
        """Iterates structures in parallel using multiple processes.

        func will be called with each Structure object that this folder
        contains plus any arguments supplied in additional_args

        This function is a generator - values returned by func(...) will be
        yielded back to the caller as those results become available.

        For example, if there are three structures, func will be called three
        times.  If each one returns a dict, the values yielded from this
        function will be: [{}, {}, {}]

        err_func will be called with (exception, args) if an exception is
        triggered and should return an empty result of the same type as func()

        Processes are pooled such that only at most num_processes will run
        simultaneously. If num_processes is set to 0 will automatically use as
        many CPUs as are available. If num_processes is 1, will iterate
        directly and not launch any new processes, which is easier to debug.

        initializer can be set to a function that initializes any variables
        once for each process worker, which for large static arguments is much
        faster than putting them in additional_args which would copy them for
        each iteration. initializer will be called with the arguments supplied
        in init_args.
        """
        if not os.path.isdir(path):
            raise ValueError("Expected path to be a folder")

        parallel_args = []
        for root, subdirs, files in os.walk(path):
            for fname in files:
                if fname.endswith(".nbt"):
                    parallel_args.append((_create_structure_lambda, (os.path.join(root, fname),), _finalize_structure_lambda, (autosave,), func, err_func, additional_args))

        yield from process_in_parallel(parallel_args, num_processes=num_processes, initializer=initializer, initargs=initargs)
