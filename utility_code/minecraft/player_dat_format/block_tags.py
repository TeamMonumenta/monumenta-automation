import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../quarry"))
from quarry.types import nbt

class CanPlaceOn():
    """Block IDs this item can be placed on in adventure mode."""
    def __init__(self, item_tag: nbt.TagCompound):
        """Load which blocks this item can be placed on from its tag.

        This is a reference to the original. Make sure to save parent tag when done.
        """
        if not isinstance(item_tag, nbt.TagCompound):
            raise TypeError("Expected item_tag to be an instance of nbt.TagCompound.")

        self.item_tag = item_tag

    @property
    def block_ids(self):
        """"Get the list of block IDs this item can be placed on."""
        block_ids = []
        for block_id_tags in item_tag.iter_multipath("AttributeModifiers[]"):
            block_ids = block_id_tags.value
        return block_ids

    @block_ids.setter
    def block_ids(self, value):
        """Set the list of blocks this item can be placed on."""
        if len(value) == 0:
            if self.item_tag.has_path("AttributeModifiers"):
                self.item_tag.value.pop("AttributeModifiers")
        else:
            block_id_tags = [nbt.TagString(block_id) for block_id in value]
            self.item_tag.value["AttributeModifiers"] = nbt.TagList(block_id_tags)


class BlockEntityTag():
    """The block entity tag to be placed/displayed by this item."""
    def __init__(self, item: Item):
        """Load the block tag in this item from its tag.

        This is a reference to the original. Make sure to save parent tag when done.
        """
        if not isinstance(item, Item):
            raise TypeError("Expected item to be an instance of Item.")

        self.item = item
        self.item_tag = item.tag

    @property
    def block_entity(self):
        """"Get the block entity tag of this item, or None."""
        if not self.item_tag.has_path("BlockEntityTag"):
            return None
        blockEntityTag = self.item_tag.at_path("BlockEntityTag")
        item_path_debug = self.item.path_debug.get_child_debug("BlockEntityTag", blockEntityTag, blockEntityTag)
        return BlockEntity(blockEntityTag, item_path_debug, self.item.root)

    @block_entity.setter
    def block_entity(self, value):
        """Set the block entity tag of this item."""
        if value is None:
            if self.item_tag.has_path("BlockEntityTag"):
                self.item_tag.value.pop("BlockEntityTag")
        elif isinstance(value, BlockEntity):
            self.item_tag.value["BlockEntityTag"] = value.nbt
        else:
            self.item_tag.value["BlockEntityTag"] = value


class BlockStateTag():
    """The block state tag to be placed with this item."""
    def __init__(self, item: Item):
        """Load the block state in this item from its tag.

        This is a reference to the original. Make sure to save parent tag when done.
        """
        if not isinstance(item, Item):
            raise TypeError("Expected item to be an instance of Item.")

        self.item = item
        self.item_tag = item.tag

    @property
    def block_state(self):
        """"Get the block state of this item, or None."""
        if not self.item_tag.has_path("BlockStateTag"):
            return None
        block_state = {}
        for key, value_tag in self.item_tag.at_path("BlockStateTag").value.items():
            block_state[key] = value_tag.value
        return block_state

    @block_state.setter
    def block_state(self, value):
        """Set the block state of this item."""
        if value is None:
            if self.item_tag.has_path("BlockStateTag"):
                self.item_tag.value.pop("BlockStateTag")
        else:
            block_state = {}
            for key, val in value.items():
                block_state[key] = nbt.TagString(val)
            self.item_tag.value["BlockStateTag"] = nbt.TagCompound(block_state)


from minecraft.chunk_format.block_entity import BlockEntity

