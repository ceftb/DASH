WebDash
=======

* Tested on Firefox 20.0.1

### Download Maven:
```
http://maven.apache.org/download.cgi
```
### Set environment variable 

* in ~/.bash_profile add:

```
export DYLD_LIBRARY_PATH=path_to_jpl
```

* Example:

```
export DYLD_LIBRARY_PATH=/opt/local/lib/swipl-6.2.2/lib/i386-darwin11.3.0
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

### Import as Eclipse Project

* In Eclipse go to: File -> Import -> Maven -> Existing Maven Projects (if you do not find Maven as an option, go to "Install Maven for Eclipse")
* Browse to "webdash" project location and Import

### Install Maven for Eclipse

* Go to Help -> Eclipse Marketplace and look for m2e. 
* Click "Maven Integration for Eclipse", then on Install 
