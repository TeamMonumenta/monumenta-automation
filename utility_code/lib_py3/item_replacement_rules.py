import json
import os
import sys
import yaml

from lib_py3.common import eprint
from lib_py3.common import get_item_name_from_nbt
from lib_py3.common import update_plain_tag

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types import nbt
from quarry.types.text_format import TextFormats, TextStyles


NIL = "00000000-0000-0000-0000-000000000000"


def jsonify_text_hack(text):
    if text == "":
        return json.dumps({"text":""}, ensure_ascii=False, separators=(',', ':'))
    if text.startswith("§"):
        extra = [{"bold":False, "italic":False, "underlined":False, "strikethrough":False, "obfuscated":False, "color":"light_purple", "text":""}]
        while text:
            while text.startswith("§"):
                try:
                    format_ = TextFormats.get_format_by_section_code(text[:2])
                    if format_ == TextFormats.reset.value:
                        format_ = TextFormats.white.value
                    if any(style.value == format_ for style in TextStyles):
                        extra[-1][format_.technical_name] = True
                    else:
                        extra[-1]["color"] = format_.technical_name
                    text = text[2:]
                except KeyError:
                    extra[-1]["text"] += text[:2]
                    text = text[2:]
                    break
            while text and not text.startswith("§"):
                extra[-1]["text"] += text[:1]
                text = text[1:]
            if text:
                extra.append({"text":""})
        return json.dumps({"extra":extra, "text":""}, ensure_ascii=False, separators=(',', ':'))

    return json.dumps({"extra":[{"text":text}], "text":""}, ensure_ascii=False, separators=(',', ':'))

def to_number(numeral):
    if numeral == 'I':
        return 1
    if numeral == 'II':
        return 2
    if numeral == 'III':
        return 3
    if numeral == 'IV':
        return 4
    return 0


def mark_dirty(item):
    if not item.nbt.has_path('tag.Monumenta'):
        return
    item.nbt.at_path('tag.Monumenta').value['Dirty'] = nbt.TagByte(1)


class GlobalRule():
    """Base pre/post processing rule for item replacements, used to preserve and edit data."""
    # Edit this for all new objects:
    name = "Undefined global rule"

    def __init__(self):
        """Local data storage"""
        pass

    def preprocess(self, template, item):
        """Read the unedited item.

        Return True to abort replacement and changes.
        Make no edits here.
        """
        pass

    def postprocess(self, item):
        """Edit the item with last stored value"""
        pass

    @classmethod
    def recursive_public_subclasses(cls):
        """Return a list of initialized subclasses, not listing subclasses starting with '_'.

        Should multiple subclasses need to be derived from another subclass,
        a base subclass whose name starts with '_' should be created so
        its children are returned, but not the base subclass itself.

        Note that this returns classes in the order they are defined in this file, so they can
        be re-ordered if needed
        """
        result = []

        for subclass in cls.__subclasses__():
            name = subclass.__name__

            # Ignore subclasses that exist only as a parent to other subclasses
            if not name.startswith("_"):
                result.append(subclass())

            result += subclass.recursive_public_subclasses()

        return result

    def __str__(self):
        return f'{self.name}: {vars(self)}'

    def __repr__(self):
        return f'{type(self).__name__}()'

################################################################################
# Global rules begin

### Items on Monumenta mobs have no lore text so they don't get updated

class AbortNoLore(GlobalRule):
    name = "Abort if there's no lore text"

    def preprocess(self, template, item):
        # Items with lore are always replaced
        if item.nbt.has_path('tag.display.Lore'):
            return

        # Always update vanity items, even with no lore
        if item.is_vanity():
            return

        # Items without lore in spawners never get replaced
        #if item.is_in_spawner():
        #    return True

        # ~~Anything at this point is probably fine.~~ It was not fine after all - mobs in the world, mobs in spawn eggs
        return True

### Vanilla data to preserve

class PreserveArmorColor(GlobalRule):
    name = 'Preserve armor color'

    def __init__(self):
        super().__init__()
        self.color = None

    def preprocess(self, template, item):
        self.color = None
        if item.nbt.has_path('tag.display.color'):
            self.color = item.tag.at_path('display.color').value

    def postprocess(self, item):
        if item.id not in (
                'minecraft:leather_helmet',
                'minecraft:leather_chestplate',
                'minecraft:leather_leggings',
                'minecraft:leather_boots',
                'minecraft:leather_horse_armor',
        ):
            # Don't preserve armor color if it's no longer leather
            return

        if self.color is None:
            if item.nbt.has_path('tag.display.color'):
                item.tag.at_path('display').value.pop('color')
            return

        # Make sure tag exists first
        if not item.has_tag():
            item.tag = nbt.TagCompound({})
        if not item.tag.has_path('display'):
            item.tag.value['display'] = nbt.TagCompound({})
        if not item.tag.has_path('display.color'):
            item.tag.at_path('display').value['color'] = nbt.TagInt(0)

        # Apply color
        item.tag.at_path('display.color').value = self.color

class PreserveDamage(GlobalRule):
    name = 'Preserve damage'

    def __init__(self):
        super().__init__()
        self.damage = None

    def preprocess(self, template, item):
        self.damage = None
        if item.nbt.has_path('tag.Damage'):
            self.damage = item.tag.at_path('Damage').value

    def postprocess(self, item):
        if not item.is_damageable():
            return

        if self.damage is None:
            if item.nbt.has_path('tag.Damage'):
                item.tag.value.pop('Damage')
            return

        # Make sure tag exists first
        if not item.has_tag():
            item.tag = nbt.TagCompound({})
        if not item.tag.has_path('Damage'):
            item.tag.value['Damage'] = nbt.TagInt(0)

        # Apply damage
        item.tag.at_path('Damage').value = self.damage

class PreserveCrossbowItem(GlobalRule):
    name = 'Preserve crossbow item'

    def __init__(self):
        super().__init__()
        self.Charged = None
        self.ChargedProjectiles = None

    def preprocess(self, template, item):
        self.Charged = None
        self.ChargedProjectiles = None
        if item.nbt.has_path('tag.Charged'):
            self.Charged = item.tag.at_path('Charged').deep_copy()
        if item.nbt.has_path('tag.ChargedProjectiles'):
            self.ChargedProjectiles = item.tag.at_path('ChargedProjectiles').deep_copy()

    def postprocess(self, item):
        if item.id != 'minecraft:crossbow':
            # Don't preserve crossbow item if it's no longer a crossbow
            return

        if self.Charged is None:
            if item.nbt.has_path('tag.Charged'):
                item.tag.value.pop('Charged')
        if self.ChargedProjectiles is None:
            if item.nbt.has_path('tag.ChargedProjectiles'):
                item.tag.value.pop('ChargedProjectiles')
        if self.Charged is None and self.ChargedProjectiles is None:
            return

        # Make sure tag exists first
        if not item.has_tag():
            item.tag = nbt.TagCompound({})
        if self.Charged is not None:
            item.tag.value['Charged'] = self.Charged
        if self.ChargedProjectiles is not None:
            item.tag.value['ChargedProjectiles'] = self.ChargedProjectiles

## Monumenta data to preserve
class PreserveMonumentaPlayerModifications(GlobalRule):
    name = 'Preserve player-modified tags from Monumenta'

    def __init__(self):
        super().__init__()
        self.tag = None

    def preprocess(self, template, item):
        self.tag = None
        if item.nbt.has_path('tag.Monumenta.PlayerModified'):
            self.tag = item.tag.at_path('Monumenta.PlayerModified')

    def postprocess(self, item):
        if self.tag is not None:
            if not item.nbt.has_path('tag'):
                item.nbt.value['tag'] = nbt.TagCompound({})
            if not item.tag.has_path('Monumenta'):
                item.tag.value['Monumenta'] = nbt.TagCompound({})
            item.tag.at_path('Monumenta').value['PlayerModified'] = self.tag

        if item.nbt.has_path('tag.Monumenta.PlayerModified.Infusions') and len(item.nbt.at_path('tag.Monumenta.PlayerModified.Infusions').value) == 0:
            item.tag.at_path('Monumenta.PlayerModified').value.pop('Infusions')

        if item.nbt.has_path('tag.Monumenta.PlayerModified') and len(item.nbt.at_path('tag.Monumenta.PlayerModified').value) == 0:
            item.tag.at_path('Monumenta').value.pop('PlayerModified')

        if item.nbt.has_path('tag.Monumenta') and len(item.nbt.at_path('tag.Monumenta').value) == 0:
            item.tag.value.pop('Monumenta')

        if item.nbt.has_path('tag.Monumenta.PlayerModified') and len(item.nbt.at_path('tag.Monumenta.PlayerModified').value) > 0:
            mark_dirty(item)

class PreserveBlockEntityTag(GlobalRule):
    name = 'Preserve block entity tag'

    def __init__(self):
        super().__init__()
        self.block_entity_tag = None

    def preprocess(self, template, item):
        self.block_entity_tag = None
        if item.nbt.has_path('tag.BlockEntityTag'):
            self.block_entity_tag = item.tag.at_path('BlockEntityTag')

            if not isinstance(self.block_entity_tag, nbt.TagCompound):
                self.block_entity_tag = None
                eprint("Skipping invalid BlockEntityTag: " + item.nbt.to_mojangson(highlight=False))
                return

            # Some legacy items have this invalid tag.BlockEntityTag.id field
            if self.block_entity_tag.has_path('id'):
                self.block_entity_tag.value.pop('id')

    def postprocess(self, item):
        if item.nbt.has_path('tag.BlockEntityTag'):
            item.tag.value.pop('BlockEntityTag')

        if self.block_entity_tag is not None:
            if not item.has_tag():
                item.tag = nbt.TagCompound({})
            item.tag.value['BlockEntityTag'] = self.block_entity_tag

class PreserveTotemOfTransposing(GlobalRule):
    name = 'Preserve Totem of Transposing tags'

    def __init__(self):
        super().__init__()
        self.channel = None

    def preprocess(self, template, item):
        self.channel = None
        if item.nbt.has_path('tag.TransposingID') and isinstance(item.tag.at_path('TransposingID').value, int):
            self.channel = item.tag.at_path('TransposingID').value

    def postprocess(self, item):
        if self.channel is not None:
            if not item.nbt.has_path('tag.display.Lore[0]'):
                return
            for i, oldLoreTag in enumerate(item.tag.at_path('display.Lore').value):
                if 'Transposing Channel:' in oldLoreTag.value:
                    item.tag.value['TransposingID'] = nbt.TagInt(self.channel)
                    item.tag.at_path('display.Lore').value[i].value = '{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"gold","extra":[{"text":"Transposing Channel: "},{"text":"$TRANSPOSING_ID$"}],"text":""}'.replace('$TRANSPOSING_ID$', str(self.channel))
                    plain_tag_path = 'plain.display.Lore[$INDEX$]'.replace('$INDEX$', str(i))
                    if item.tag.has_path(plain_tag_path):
                        item.tag.at_path(plain_tag_path).value = 'Transposing Channel: $TRANSPOSING_ID$'.replace('$TRANSPOSING_ID$', str(self.channel))
            mark_dirty(item)

class PreservePotionInjector(GlobalRule):
    name = 'Preserve Potion Injector config'

    def __init__(self):
        super().__init__()
        self.injector_config = None

    def preprocess(self, template, item):
        self.injector_config = None
        if item.id.startswith('minecraft:') and item.id.endswith('_shulker_box'):
            if item.nbt.has_path('tag.display.Name') and get_item_name_from_nbt(item.tag, True) == 'Potion Injector':
                if item.nbt.has_path('tag.display.Lore[1]'):
                    self.injector_config = item.nbt.at_path('tag.display.Lore[1]')

    def postprocess(self, item):
        if self.injector_config is not None and item.nbt.has_path('tag.display.Lore[1]'):
            item.nbt.at_path('tag.display.Lore').value[1] = self.injector_config

class UpdatePlainTag(GlobalRule):
    name = 'Update plain tag'

    def postprocess(self, item):
        if item.nbt.has_path("tag"):
            update_plain_tag(item.nbt.at_path("tag"))

################################################################################
# Global rules end

global_rules = GlobalRule.recursive_public_subclasses()
