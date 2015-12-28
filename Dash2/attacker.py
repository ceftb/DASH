from dash import readAgent, known, primitiveActions, agentLoop, isConstant, knownTuple
import subprocess

readAgent("""

goalWeight readFile(!localhost, !/etc/passwd) 1

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
known likelyVulnerability(!server1, !80, !index.html, !name)
known likelyVulnerability(!localhost, !80, !index.html, !name)

known reachable(anywhere, !server1)
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
    if not isConstant(action[1]):
        print "Host needs to be bound on calling portScanner:", action[1]
        return False
    portVar = action[2]
    protocolVar = action[3]
    bindingsList = []
    readingPorts = False
    for line in subprocess.check_output(["nmap", action[1][1:]]).split('\n'): # runs nmap if it's in the path
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
            knownTuple((action[0], action[1], port, protocol))
            if not isConstant(portVar) and not isConstant(protocolVar):
                bindingsList.append({portVar: port, protocolVar: protocol})
            elif portVar == port and not isConstant(protocolVar):
                bindingsList.append({protocolVar: protocol})
            elif not isConstant(portVar) and protocolVar == protocol:
                bindingsList.append({portVar: port})
            elif portVar == port and protocolVar == protocol:
                bindingsList.append({})   # constants all match, record success
    return bindingsList

def sqlMap(action):
    print "Called sql map with action", action
    return [{}]

def sqlInjectionReadFile(args):
    print "Performing sql injection attack to read a file with args", args
    return [{}]   # This would signify success without adding new bindings

primitiveActions([('SQLInjectionReadFile', sqlInjectionReadFile), 
                  ('portScanner', portScanner),
                  ('checkSQLVulnerability', sqlMap)])

# Figure out the next action to take
agentLoop(maxIterations=3)

