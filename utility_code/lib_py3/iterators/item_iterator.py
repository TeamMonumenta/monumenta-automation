#
# Recursive iterator for items everywhere in the world
#

class ItemIterator(object):
    _single_item_locations = (
        "ArmorItem",
        "Item",
        "RecordItem",
        "SaddleItem",
        "Trident",
    )

    _list_item_locations = (
        "ArmorItems",
        "EnderItems",
        "HandItems",
        "Inventory",
        "Items",
        "Inventory",
    )

    @classmethod
    def scan_entity_for_items(cls, entity_nbt, item_found_func):
        for location in cls._single_item_locations:
            if entity_nbt.has_path(location):
                item_found_func(entity_nbt.at_path(location))

        for location in cls._list_item_locations:
            if entity_nbt.has_path(location):
                for item in entity_nbt.at_path(location).value:
                    item_found_func(item)

        if entity_nbt.has_path("Offers.Recipes"):
            for item in entity_nbt.at_path("Offers.Recipes").value:
                if item.has_path("buy"):
                    item_found_func(item.at_path("buy"))
                if item.has_path("buyB"):
                    item_found_func(item.at_path("buyB"))
                if item.has_path("sell"):
                    item_found_func(item.at_path("sell"))
