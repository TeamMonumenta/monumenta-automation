#!/usr/bin/env python3

import os
import sys
import time
import zlib
import math

from collections.abc import MutableMapping

from minecraft.chunk_format.chunk import Chunk
from minecraft.util.debug_util import NbtPathDebug

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../quarry"))
from quarry.types import nbt
from quarry.types.buffer import Buffer, BufferUnderrun

class Region(MutableMapping):
    """A region file."""

    def __init__(self, path, rx, rz):
        """Load a region file from the path provided, and allow saving."""
        self.path = path
        self.rx = rx
        self.rz = rz
        self._region = nbt.RegionFile(self.path)

    def has_chunk(self, cx, cz):
        """Return True if this region contains chunk cx, cz (global coordinates)."""
        entry = self._get_entry(cx, cz) & 0xffffffff
        return self._entry_valid(entry)

    def load_chunk(self, cx, cz):
        """Return the Chunk for a given cx, cz coordinate.

        Raises KeyError if chunk is not present.
        """
        if not self.has_chunk(cx, cz):
            raise KeyError(f'Chunk {cx},{cz} not found.')

        entry = self._get_entry(cx, cz)
        chunk_offset, chunk_length = entry >> 8, entry & 0xff

        # Read compressed chunk NBT data
        self._region.fd.seek(4096 * chunk_offset)
        buff = Buffer()
        buff.add(self._region.fd.read(4096 * chunk_length))
        compressed_size, compression_format = buff.unpack('IB')
        # Fix off-by-one error when reading chunk data
        compressed_size = min(compressed_size, len(buff))

        chunk_tag = buff.read(compressed_size)
        chunk_tag = zlib.decompress(chunk_tag)
        chunk_tag = nbt.TagRoot.from_bytes(chunk_tag)
        chunk_tag = chunk_tag.body

        chunk = Chunk(chunk_tag)
        return chunk

    def save_chunk(self, chunk, cx=None, cz=None):
        """Save the Chunk at cx, cz.

        If cx, cz is not in this region, raises KeyError.
        """
        if cx is None:
            cx = chunk.cx
        if cz is None:
            cz = chunk.cz

        if cx != chunk.cx or cz != chunk.cz:
            raise NotImplementedError('Saving chunks at new coordinates not yet supported.')

        local_cx = cx - 32 * self.rx
        local_cz = cz - 32 * self.rz

        if (
            0 > local_cx or local_cx > 31 or
            0 > local_cz or local_cz > 31
        ):
            raise KeyError(f'Region file ({self.rx}, {self.rz}) does not contain chunk coordinate ({cx}, {cz}).')

        chunk = nbt.TagRoot.from_body(chunk.nbt)

        # Compress chunk
        chunk = zlib.compress(chunk.to_bytes())
        chunk = Buffer.pack('IB', len(chunk), 2) + chunk
        chunk_length = 1 + (len(chunk) - 1) // 4096

        # Load extents
        extents = [(0, 2)] # Ignore the extent and timestamp tables.
        self._region.fd.seek(0)
        buff = Buffer(self._region.fd.read(4096))
        for entry_index in range(1024):
            z, x = divmod(entry_index, 32)
            entry = buff.unpack('I') & 0xffffffff
            offset, length = entry >> 8, entry & 0xff
            if self._entry_valid(entry) and not (x == cx and z == cz):
                extents.append((offset, length))
        # Sort extents by starting offset
        extents.sort()
        # Terminator extent - track where the new end of the region file would be if the file needs expanding.
        extents.append((extents[-1][0] + extents[-1][1] + chunk_length, 0))

        # Compute new extent
        for idx in range(len(extents) - 1):
            prev_extent = extents[idx]
            prev_extent_start = prev_extent[0]
            prev_extent_len = prev_extent[1]

            next_extent = extents[idx+1]
            next_extent_start = next_extent[0]

            extent_gap_start = prev_extent_start + prev_extent_len
            extent_gap_end = next_extent_start
            extent_gap_len = extent_gap_end - extent_gap_start

            if extent_gap_len >= chunk_length:
                chunk_offset = extent_gap_start
                extents.insert(idx+1, (chunk_offset, chunk_length))
                break

        # Write extent header
        self._region.fd.seek(4 * (32 * local_cz + local_cx))
        self._region.fd.write(Buffer.pack('I', (chunk_offset << 8) | (chunk_length & 0xff)))

        # Write timestamp header
        self._region.fd.seek(4096 + 4 * (32 * local_cz + local_cx))
        self._region.fd.write(Buffer.pack('I', int(time.time())))

        # Write chunk
        self._region.fd.seek(4096 * chunk_offset)
        self._region.fd.write(chunk)

        # Truncate file
        self._region.fd.seek(4096 * extents[-1][0])
        self._region.fd.truncate()

    def delete_chunk(self, cx, cz):
        """Save the Chunk at cx, cz.

        If cx, cz is not in this region, raises KeyError.
        """
        local_cx = cx - 32 * self.rx
        local_cz = cz - 32 * self.rz

        if (
            0 > local_cx or local_cx > 31 or
            0 > local_cz or local_cz > 31
        ):
            raise KeyError(f'Region file ({self.rx}, {self.rz}) does not contain chunk coordinate ({cx}, {cz}).')

        # Load extents
        extents = [(0, 2)] # Ignore the extent and timestamp tables.
        self._region.fd.seek(0)
        buff = Buffer(self._region.fd.read(4096))
        for entry_index in range(1024):
            z, x = divmod(entry_index, 32)
            entry = buff.unpack('I') & 0xffffffff
            offset, length = entry >> 8, entry & 0xff
            if self._entry_valid(entry) and not (x == cx and z == cz):
                extents.append((offset, length))
        # Sort extents by starting offset
        extents.sort()
        # Terminator extent - track end of region file
        extents.append((extents[-1][0] + extents[-1][1], 0))

        # Write extent header
        self._region.fd.seek(4 * (32 * local_cz + local_cx))
        self._region.fd.write(Buffer.pack('I', 0))

        # Write timestamp header
        self._region.fd.seek(4096 + 4 * (32 * local_cz + local_cx))
        self._region.fd.write(Buffer.pack('I', 0))

        # Truncate file
        self._region.fd.seek(4096 * extents[-1][0])
        self._region.fd.truncate()

    def iter_chunk_coordinates(self):
        """Iterate over chunk coordinates `tuple(cx, cz)` in this region file."""
        yield from iter(self)

    def iter_chunks(self, min_x=-math.inf, min_y=-math.inf, min_z=-math.inf, max_x=math.inf, max_y=math.inf, max_z=math.inf, autosave: bool=False):
        for cx, cz in self.iter_chunk_coordinates():
            if (
                16*cx + 16 <= min_x or
                16*cx      >  max_x or
                16*cz + 16 <= min_z or
                16*cz      >  max_z
            ):
                continue

            chunk = self.load_chunk(cx, cz)

            yield chunk

            if autosave:
                region.save_chunk(chunk)

    def _get_entry(self, cx, cz):
        local_cx = cx - 32 * self.rx
        local_cz = cz - 32 * self.rz

        if (
            0 > local_cx or local_cx > 31 or
            0 > local_cz or local_cz > 31
        ):
            return False

        # Read extent header
        self._region.fd.seek(4 * (32 * local_cz + local_cx))
        try:
            return Buffer(self._region.fd.read(4)).unpack('I') & 0xffffffff
        except BufferUnderrun:
            return False

    def _entry_valid(self, entry):
        entry = entry & 0xffffffff
        offset, length = entry >> 8, entry & 0xff
        return offset > 0 and length > 0

    def __len__(self):
        count = 0
        self._region.fd.seek(0)
        buff = Buffer(self._region.fd.read(4096))
        for entry_index in range(1024):
            entry = buff.unpack('I') & 0xffffffff
            if self._entry_valid(entry):
                count += 1
        return count

    def __length_hint__(self):
        # Typical case is 1024 chunks/region, hint may be over/under actual value.
        return 1024

    def __getitem__(self, chunk_coord_pair):
        """Get a chunk using a dict-style key access, ex: `return region[(5, 4)]`."""
        cx, cz = chunk_coord_pair
        return self.load_chunk(cx, cz)

    def __setitem__(self, chunk_coord_pair, chunk):
        """Set a chunk using a dict-style key access, ex: `region[(5, 4)] = chunk`."""
        cx, cz = chunk_coord_pair
        return self.save_chunk(chunk, cx, cz)

    def __delitem__(self, chunk_coord_pair):
        """Delete a chunk using a dict-style key access, ex: `del region[(5, 4)]`."""
        cx, cz = chunk_coord_pair
        return self.delete_chunk(chunk, cx, cz)

    def __iter__(self):
        """Iterate over chunk coordinates `tuple(cx, cz)` in this region file."""
        cx_offset = 32 * self.rx
        cz_offset = 32 * self.rz

        # Load extents
        for local_cz in range(32):
            cz = cz_offset + local_cz
            for local_cx in range(32):
                cx = cx_offset + local_cx
                if self.has_chunk(cx, cz):
                    yield (cx, cz)

    def __contains__(self, chunk_coord_pair):
        """Return true if chunk_coord_pair = (cx, cz) in this region file."""
        cx, cz = chunk_coord_pair
        return self.has_chunk(cx, cz)

    def __repr__(self):
        return f'Region({self.path!r}, {self.rx!r}, {self.rz!r})'
