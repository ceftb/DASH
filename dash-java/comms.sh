. ./env.sh

java -cp $SWILIB/jpl.jar:$BIN -Djava.library.path=$SWILIB/$SWIOS edu.isi.detergent.CommServer $*

