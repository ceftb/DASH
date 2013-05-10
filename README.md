WebDash
=======

### Download Maven:
```
http://maven.apache.org/download.cgi
```
### Set environment variable 
(this is a temporary solution until I figure out why the maven config doen't work with native libraries)

* in ~/.bash_profile add:

```
export DYLD_LIBRARY_PATH path_to_jpl
```
* Example:

```
export DYLD_LIBRARY_PATH /opt/local/lib/swipl-6.2.2/lib/i386-darwin11.3.0
```

* Set environment (at command line):

```
. ~/.bash_profile
```

### Compile
```
mvn compile
```

### Start Jetty Server
```
mvn jetty:run
```

### Start Wizard

* In Browser go to:
```
localhost:8080/wizard.html
```
