# Initial attacker agent for password agents
import random

from dash import DASHAgent
from system2 import isVar


class PasswordAgentAttacker(DASHAgent):

    def __init__(self):
        DASHAgent.__init__(self)
        self.readAgent("""

goalWeight attack 1

goalRequirements attack
    chooseAttack(_direct)
    findUncompromisedSite(site)
    directAttack(site)
    sleep(1)
    forget([chooseAttack(x), findUncompromisedSite(x), directAttack(x), sleep(x)])

goalRequirements attack
    chooseAttack(_indirect)
    findUncompromisedSite(site)
    findCompromisedSite(comp)
    reusePassword(comp, site)
    sleep(1)
    forget([chooseAttack(x), findUncompromisedSite(x), findCompromisedSite(x), reusePassword(x,y), sleep(x)])

# If chooseAttack fails in both clauses (since the calls are independent), just try again as long as there's
# something left to attack
goalRequirements attack
    findUncompromisedSite(site)
    forget([chooseAttack(x), findUncompromisedSite(x), directAttack(x), reusePassword(c, s), findCompromisedSite(x)])

transient attack

""")
        self.primitiveActions([('findUncompromisedSite', self.find_unc_site), ('directAttack', self.direct_attack),
                               ('chooseAttack', self.choose_attack), ('findCompromisedSite', self.find_compromised_site),
                               ('reusePassword', self.reuse_password)])
        self.register()     # Register with the running password agent hub

        # These are sets since the main operations are set difference and adding or removing elements
        self.uncompromised_sites = set() #['bank1', 'bank2', 'mail1', 'mail2', 'amazon', 'youtube']
        self.compromised_sites = set()  # If a site is compromised, I guess we assume the attacker knows all user/pwd combos there
        self.failed = []

        #self.traceAction = True
        #self.traceGoals = True

    # Decide which style of attack to try next. Binds the main variable to either _direct or _indirect
    def choose_attack(self, (goal, term)):
        if term == "_direct":
            if not self.compromised_sites or random.random() < 0.5:
                print 'making a direct attack'
                return [{}]
            else:
                return []
        elif term == "_indirect":
            if self.compromised_sites and random.random() > 0.5:
                print 'making an indirect attack'
                return [{}]
            else:
                return []
        elif isVar(term):
            if not self.compromised_sites:
                print 'choosing direct attack since there are no compromised sites'
                return [{term: '_direct'}] # Must choose direct if no sites are compromised yet
            elif random.random() < 0.5:   #
                print 'choosing direct attack randomly'
                return [{term: '_direct'}]
            else:
                print 'choosing indirect attack randomly'
                return [{term: '_indirect'}]
        else:  # some constant that is not an attack style
            return []

    # Bind the site variable to a random possible site to attack.
    # Ultimately, get the names from the hub and keep track of those that have already been compromised
    # or where the agent has failed, and attack the rest.
    # For now, use an internal list of sites
    def find_unc_site(self, (goal, site_var)):
        [status, data] = self.sendAction('listAllSites')
        # This call is made every time in case new sites have been added in the hub. Filter out the ones
        # that are already compromised (using set difference). Return a list of bindings, one for each possible site.
        print 'all sites: ', data
        self.uncompromised_sites = set(data) - self.compromised_sites
        return [{site_var: unc_site} for unc_site in self.uncompromised_sites]

    def find_compromised_site(self, (goal, site_var)):
        # Keep track internally of what was compromised (from the hub's point of view, someone logged in to a site,
        # but the agent knows this was a password reuse attack).
        #[status, data] = self.sendAction('findCompromisedSite')
        # Return a list of bindings, one for each possible compromised site.
        return [{site_var: compromised_site} for compromised_site in self.compromised_sites]

    def direct_attack(self, (goal, site)):   # call is (directAttack, site)
        status = self.sendAction('directAttack', [site])   # action just returns success or failure
        if status == 'success':
            self.uncompromised_sites.remove(site)
            self.compromised_sites.add(site)
            return [{}]   # Success with empty bindings
        else:
            return []

    def reuse_password(self, (goal, comp, site)):    # call is (reusePassword, comp, site)
        [status, list_of_pairs] = self.sendAction('getUserPWList', [comp])   # will fail if site wasn't compromised
        # Pick a pair at random and try to log in (low success rate)
        if status == 'success' and list_of_pairs:
            (user, password) = random.choice
            status = self.sendAction('signIn', [site, user, password])
            if status[0] == 'success':
                self.uncompromised_sites.remove(site)
                self.compromised_sites.add(site)
                print 'successfully reused', user, password, 'from', comp, 'on', site
                return [{}]
            else:
                print 'failed attempt to reuse', user, password, 'from', comp, 'on', site
                return []
        else:
            print 'site', comp, 'was not compromised after all'
            return []




if __name__ == "__main__":
    PasswordAgentAttacker().agentLoop()
