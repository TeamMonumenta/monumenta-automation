These are in Brigadier and just need to be tied to their ID somehow:
```
brigadier:bool
brigadier:double
brigadier:float
brigadier:integer
brigadier:string
```
The Brigadier library may need some of its library ported to Python to port the full parsing logic, but let's ignore that for now.


Done:
```
minecraft:item_stack
minecraft:nbt_path # Sort of; only if using the path right away, not pre-parsing it, ie for functions
minecraft:nbt_compound_tag
```

Everything past this point may need a ContextBuilder object in order to yield the correct results:

TODO:
```
minecraft:block_pos
minecraft:block_predicate
minecraft:block_state
minecraft:color
minecraft:column_pos
minecraft:component # text component/raw json text
minecraft:dimension
minecraft:entity
minecraft:entity_anchor
minecraft:entity_summon
minecraft:function
minecraft:game_profile
minecraft:int_range
minecraft:item_enchantment
minecraft:item_predicate
minecraft:item_slot
minecraft:message
minecraft:mob_effect
minecraft:nbt
minecraft:nbt_tag
minecraft:objective
minecraft:objective_criteria
minecraft:operation
minecraft:particle
minecraft:resource_location
minecraft:rotation
minecraft:score_holder
minecraft:scoreboard_slot
minecraft:swizzle
minecraft:team
minecraft:time
minecraft:vec2
minecraft:vec3
```

