#
# Setup
#
PID=$1
BID=$2

work_dir="/root/workspace"

export _JAVA_OPTIONS="-Xmx6144M -XX:MaxHeapSize=4096M"
export MAVEN_OPTS="-Xmx1024M"
export ANT_OPTS="-Xmx6144M -XX:MaxHeapSize=4096M"

export GZOLTAR_AGENT_JAR="$work_dir/gzoltar/com.gzoltar.agent.rt/target/com.gzoltar.agent.rt-1.7.4-SNAPSHOT-all.jar"
export GZOLTAR_CLI_JAR="$work_dir/gzoltar/com.gzoltar.cli/target/com.gzoltar.cli-1.7.4-SNAPSHOT-jar-with-dependencies.jar"

#
# Get GZoltar
#
if [ ! -f $GZOLTAR_AGENT_JAR ]; then
  cd "$work_dir"
  git clone https://github.com/GZoltar/gzoltar.git
  cd "$work_dir/gzoltar"
  mvn clean package
fi

#
# Checkout Closure-27, compile it, and get its metadata
#

# Checkout
# Changed to fixed directory -> check test covered by 'fixed' version
tmp_dir="/tmp/$PID-${BID}g";
rm -rf $tmp_dir;
defects4j checkout -p "$PID" -v "${BID}f" -w $tmp_dir

# Compile
cd $tmp_dir
defects4j compile

# Collect metadata
test_classpath=$(defects4j export -p cp.test)
src_classes_dir=$(defects4j export -p dir.bin.classes)
src_classes_dir="$tmp_dir/$src_classes_dir"
test_classes_dir=$(defects4j export -p dir.bin.tests)
test_classes_dir="$tmp_dir/$test_classes_dir"
echo "$PID-${BID}g's classpath: $test_classpath" >&2
echo "$PID-${BID}g's bin dir: $src_classes_dir" >&2
echo "$PID-${BID}g's test bin dir: $test_classes_dir" >&2

#
# Collect unit tests to run GZoltar with
#

unit_tests_file="$tmp_dir/unit_tests.txt"
relevant_tests="*"
# Note, you might want to consider the set of relevant tests provided by D4J, i.e., $D4J_HOME/framework/projects/$PID/relevant_tests/$BID

#echo $relevant_tests

java -cp "$test_classpath:$test_classes_dir:$D4J_HOME/framework/projects/lib/junit-4.11.jar:$GZOLTAR_CLI_JAR" \
  com.gzoltar.cli.Main listTestMethods "$test_classes_dir" \
    --outputFile "$unit_tests_file" \
    --includes "$relevant_tests"
#[ -f $unit_tests_file ] && rm $unit_tests_file;
#defects4j export -p tests.trigger | sed "s/::/#/g" | uniq | sort | while read line; do echo "JUNIT,${line}" >> $unit_tests_file; done


head "$unit_tests_file"

#
# Collect classes to perform fault localization on
# Note: the `sed` commands below might not work on BSD-based distributions such as MacOS.
#


loaded_classes_file="$D4J_HOME/framework/projects/$PID/loaded_classes/$BID.src"
normal_classes=$(cat "$loaded_classes_file" | sed 's/$/:/' | sed ':a;N;$!ba;s/\n//g')
inner_classes=$(cat "$loaded_classes_file" | sed 's/$/$*:/' | sed ':a;N;$!ba;s/\n//g')
classes_to_debug="$normal_classes$inner_classes"
echo "Likely faulty classes: $classes_to_debug" >&2

#
# Run GZoltar
#

cd $tmp_dir

start=$(date +%s%N)
ser_file="$tmp_dir/gzoltar.ser"
java -XX:MaxPermSize=4096M -javaagent:$GZOLTAR_AGENT_JAR=destfile=$ser_file,buildlocation=$src_classes_dir,includes=$classes_to_debug,excludes="",inclnolocationclasses=false,output="FILE" \
  -cp "$src_classes_dir:$D4J_HOME/framework/projects/lib/junit-4.11.jar:$test_classpath:$GZOLTAR_CLI_JAR" \
  com.gzoltar.cli.Main runTestMethods \
    --testMethods "$unit_tests_file" \
    --collectCoverage
end=$(date +%s%N)



#
# Generate fault localization report
#

cd "$tmp_dir"

java -cp "$src_classes_dir:$D4J_HOME/framework/projects/lib/junit-4.11.jar:$test_classpath:$GZOLTAR_CLI_JAR" \
    com.gzoltar.cli.Main faultLocalizationReport \
      --buildLocation "$src_classes_dir" \
      --granularity "line" \
      --inclPublicMethods \
      --inclStaticConstructors \
      --inclDeprecatedMethods \
      --dataFile "$ser_file" \
      --outputDirectory "$tmp_dir" \
      --family "sfl" \
      --formula "ochiai" \
      --metric "entropy" \
      --formatter "txt"
