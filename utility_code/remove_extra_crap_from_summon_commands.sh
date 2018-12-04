#for x in HurtByTimestamp FallFlying PortalCooldown AbsorptionAmount FallDistance DeathTime WorldUUIDMost Spigot.ticksLived Dimension OnGround Air Bukkit.updateLevel Leashed Spigot.ticksLived CanPickUpLoot WorldUUIDLeast HurtTime LeftHanded Fire
#do
#	find . -name '*.mcfunction' | xargs perl -p -i -e "s|$x:[^,\]}]*,?||g"
#done

for x in Motion Rotation ArmorDropChances Pos HandDropChances
do
	find . -name '*.mcfunction' | xargs perl -p -i -e "s|$x:\[[^\]]*\],?||g"
done

#Motion:[0.0d,-0.0784000015258789d,0.0d]
#Rotation:[214.71304f,0.0f]
#ArmorDropChances:[-200.1f,-200.1f,-200.1f,-200.1f]
#Pos:[-988.8143641146787d,99.0d,-1514.5454687685065d]
