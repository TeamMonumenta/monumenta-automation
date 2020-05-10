#!/bin/bash
java -Djava.library.path=$JAVA_HOME/jre/bin -cp $JAVA_HOME/lib/tools.jar:/warmroast-1.0.0-SNAPSHOT.jar com.sk89q.warmroast.WarmRoast --thread "Server thread" --timeout 3600 --pid 1

