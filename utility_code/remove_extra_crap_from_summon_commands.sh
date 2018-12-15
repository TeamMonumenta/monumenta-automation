for x in HurtByTimestamp FallFlying PortalCooldown AbsorptionAmount FallDistance DeathTime WorldUUIDMost UUIDMost UUIDLeast Spigot.ticksLived Dimension OnGround Air Bukkit.updateLevel Leashed Spigot.ticksLived CanPickUpLoot WorldUUIDLeast HurtTime LeftHanded Fire
do
	find . -name '*.mcfunction' | xargs perl -p -i -e "s|$x:[^,\]}]*,?||g"
done

for x in Motion Rotation ArmorDropChances Pos HandDropChances
do
	find . -name '*.mcfunction' | xargs perl -p -i -e "s|$x:\[[^\]]*\],?||g"
done
