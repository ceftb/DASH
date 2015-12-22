from dash import readAgent, known, primitiveActions, agentLoop

nmap = '/usr/local/bin/nmap'   # location of netmap program

readAgent("""

goalWeight readFile(!server1, !/etc/passwd) 1

goalRequirements readFile(target, file)
  SQLVulnerability(target, port, baseUrl, parameter)
  reachable(attackLoc, target)
  SQLInjectionReadFile(attackLoc, target, file, port, baseUrl, parameter)

goalRequirements SQLVulnerability(target, port, baseUrl, parameter)
  likelyVulnerability(target, port, baseUrl, parameter)
  service(target, port, protocol)
  http-style(protocol)

goalRequirements service(target, port, protocol)
  portScanner(target, port, protocol)

# this predicate means the information is known, and also records
# that a subgoal has been achieved
known likelyVulnerability(!server1, 80, !index.html, !name)

known reachable(anywhere, !server1)

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

# 'action' is a term, e.g. ('portScanner', '!server1', 80, 'protocol')
def portScanner(action):
    # Will expand to a call to nmap here
    print "called portScanner with", action
    # Faking the callout now. Let's say we need the machine bound and will 
    # match the other arguments. Return a bindings list for each potential match.
    # I happen to know the port is bound here
    return [{action[3]: '!http'}]

def sqlInjectionReadFile(args):
    print "Performing sql injection attack to read a file with args", args
    return [{}]   # This would signify success without adding new bindings

primitiveActions([('SQLInjectionReadFile', sqlInjectionReadFile), ('portScanner', portScanner)])

# Figure out the next action to take
agentLoop(maxIterations=2)

