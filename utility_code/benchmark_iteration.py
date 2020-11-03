#!/usr/bin/env python3

import traceback

from lib_py3.timing import Timings

import lib_py3.world
import minecraft.world

show_stacktrace = True
shard_names = (
    'region_1',
    'region_2',
    'dungeon',
)

class TestHarness():
    def __init__(self, world_path, show_stacktrace):
        NotImplemented

    def test_iter_items(self):
        NotImplemented


class TestOld(TestHarness):
    def __init__(self, world_path, show_stacktrace):
        self.timer = Timings()
        self.show_stacktrace = show_stacktrace
        self.timer.nextStep(f'[{type(self).__name__}] World loading...')
        self.world = lib_py3.world.World(world_path)
        self.timer.nextStep(f'[{type(self).__name__}] World loaded.')

    def test_iter_regions(self):
        count = 0
        try:
            self.timer.nextStep(f'[{type(self).__name__}] Region iteration starting...')
            for region in self.world.iter_regions():
                count += 1
        except Exception:
            self.timer.nextStep(f'[{type(self).__name__}] Region iteration crashed. Found {count} regions before crash.')
            if self.show_stacktrace:
                traceback.print_exc()
            return
        self.timer.nextStep(f'[{type(self).__name__}] Region iteration done. Found {count} regions.')

    def test_iter_chunks(self):
        count = 0
        try:
            self.timer.nextStep(f'[{type(self).__name__}] Chunk iteration starting...')
            for chunk in self.world.iter_chunks():
                count += 1
        except Exception:
            self.timer.nextStep(f'[{type(self).__name__}] Chunk iteration crashed. Found {count} chunks before crash.')
            if self.show_stacktrace:
                traceback.print_exc()
            return
        self.timer.nextStep(f'[{type(self).__name__}] Chunk iteration done. Found {count} chunks.')

    def test_iter_entities_local(self):
        count = 0
        self.timer.nextStep(f'[{type(self).__name__}] Local entity iteration starting...')
        try:
            for chunk in self.world.iter_chunks():
                count += chunk[2].count_multipath('Level.TileEntities[]')
                count += chunk[2].count_multipath('Level.Entities[]')
        except Exception:
            self.timer.nextStep(f'[{type(self).__name__}] Local entity iteration crashed. Found {count} entities before crash.')
            if self.show_stacktrace:
                traceback.print_exc()
            return
        self.timer.nextStep(f'[{type(self).__name__}] Local entity iteration done. Found {count} entities.')

    def test_iter_entities(self):
        count = 0
        item_set = set()
        try:
            self.timer.nextStep(f'[{type(self).__name__}] Entity iteration starting...')
            for item in self.world.entity_iterator(no_players=True):
                count += 1
                item_set.add((id(item[0]), hash(item[0])))
        except Exception:
            self.timer.nextStep(f'[{type(self).__name__}] Entity iteration crashed. Found {count} (or was it {len(item_set)}?) entities before crash.')
            if self.show_stacktrace:
                traceback.print_exc()
            return
        self.timer.nextStep(f'[{type(self).__name__}] Entity iteration done. Found {count} (or was it {len(item_set)}?) entity.')

    def test_iter_items(self):
        count = 0
        item_set = set()
        try:
            self.timer.nextStep(f'[{type(self).__name__}] Item iteration starting...')
            for item in self.world.items(no_players=True):
                count += 1
                item_set.add((id(item[0]), hash(item[0])))
        except Exception:
            self.timer.nextStep(f'[{type(self).__name__}] Item iteration crashed. Found {count} (or was it {len(item_set)}?) items before crash.')
            if self.show_stacktrace:
                traceback.print_exc()
            return
        self.timer.nextStep(f'[{type(self).__name__}] Item iteration done. Found {count} (or was it {len(item_set)}?) items.')


class TestNew(TestHarness):
    def __init__(self, world_path, show_stacktrace):
        self.timer = Timings()
        self.show_stacktrace = show_stacktrace
        self.timer.nextStep(f'[{type(self).__name__}] World loading...')
        self.world = minecraft.world.World(world_path)
        self.timer.nextStep(f'[{type(self).__name__}] World loaded.')

    def test_iter_regions(self):
        count = 0
        try:
            self.timer.nextStep(f'[{type(self).__name__}] Region iteration starting...')
            for region in self.world.iter_regions():
                count += 1
        except Exception:
            self.timer.nextStep(f'[{type(self).__name__}] Region iteration crashed. Found {count} regions before crash.')
            if self.show_stacktrace:
                traceback.print_exc()
            return
        self.timer.nextStep(f'[{type(self).__name__}] Region iteration done. Found {count} regions.')

    def test_iter_chunks(self):
        count = 0
        try:
            self.timer.nextStep(f'[{type(self).__name__}] Chunk iteration starting...')
            for region in self.world.iter_regions():
                for chunk in region.values():
                    count += 1
        except Exception:
            self.timer.nextStep(f'[{type(self).__name__}] Chunk iteration crashed. Found {count} chunks before crash.')
            if self.show_stacktrace:
                traceback.print_exc()
            return
        self.timer.nextStep(f'[{type(self).__name__}] Chunk iteration done. Found {count} chunks.')

    def test_iter_entities_local(self):
        count = 0
        self.timer.nextStep(f'[{type(self).__name__}] Local entity iteration starting...')
        try:
            for region in self.world.iter_regions():
                for chunk in region.values():
                    for item in chunk.iter_block_entities():
                        count += 1
                    for item in chunk.iter_entities():
                        count += 1
        except Exception:
            self.timer.nextStep(f'[{type(self).__name__}] Local entity iteration crashed. Found {count} entities before crash.')
            if self.show_stacktrace:
                traceback.print_exc()
            return
        self.timer.nextStep(f'[{type(self).__name__}] Local entity iteration done. Found {count} entities.')

    def test_iter_entities(self):
        count = 0
        count_fancy = 0
        item_set = set()
        path_set = set()
        self.timer.nextStep(f'[{type(self).__name__}] Entity iteration starting...')
        try:
            for region in self.world.iter_regions():
                for chunk in region.values():
                    fancy_set = set()
                    for item in chunk.recursive_iter_block_entities():
                        count += 1
                        item_set.add((id(item.nbt), hash(item.nbt)))
                        path_set.add(item.path_debug.full_nbt_path)
                        fancy_set.add((id(item.nbt), hash(item.nbt)))
                    for item in chunk.recursive_iter_entities():
                        count += 1
                        item_set.add((id(item.nbt), hash(item.nbt)))
                        path_set.add(item.path_debug.full_nbt_path)
                        fancy_set.add((id(item.nbt), hash(item.nbt)))
                    count_fancy += len(fancy_set)
        except Exception:
            self.timer.nextStep(f'[{type(self).__name__}] Entity iteration crashed. Found {count} (Entity ID set has {len(item_set)}? Entity path set has {len(path_set)}? Fancy count is {count_fancy}?) entities before crash.')
            if self.show_stacktrace:
                traceback.print_exc()
            return
        self.timer.nextStep(f'[{type(self).__name__}] Entity iteration done. Found {count} (Entity ID set has {len(item_set)}? Entity path set has {len(path_set)}? Fancy count is {count_fancy}?) entities.')

    def test_iter_items(self):
        count = 0
        count_fancy = 0
        item_set = set()
        path_set = set()
        self.timer.nextStep(f'[{type(self).__name__}] Item iteration starting...')
        try:
            for region in self.world.iter_regions():
                for chunk in region.values():
                    fancy_set = set()
                    for item in chunk.recursive_iter_items():
                        count += 1
                        item_set.add((id(item.nbt), hash(item.nbt)))
                        path_set.add(item.path_debug.full_nbt_path)
                        fancy_set.add((id(item.nbt), hash(item.nbt)))
                    count_fancy += len(fancy_set)
        except Exception:
            self.timer.nextStep(f'[{type(self).__name__}] Item iteration crashed. Found {count} (Item ID set has {len(item_set)}? Item path set has {len(path_set)}? Fancy count is {count_fancy}?) items before crash.')
            if self.show_stacktrace:
                traceback.print_exc()
            return
        self.timer.nextStep(f'[{type(self).__name__}] Item iteration done. Found {count} (Item ID set has {len(item_set)}? Item path set has {len(path_set)}? Fancy count is {count_fancy}?) items.')


try:
    for shard_name in shard_names:
        world_path = f'/home/epic/project_epic/{shard_name}/Project_Epic-{shard_name}'
        print(shard_name)
        for test_harness_cls in TestHarness.__subclasses__():
            test_harness = test_harness_cls(world_path, show_stacktrace)
            #test_harness.test_iter_regions()
            #test_harness.test_iter_chunks()
            #test_harness.test_iter_entities_local()
            test_harness.test_iter_entities()
            test_harness.test_iter_items()
            print('')
except KeyboardInterrupt:
    print('\nAborted.')

