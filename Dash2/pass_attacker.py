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
    forget([chooseAttack(x), findWebsite(x)])

transient attack

""")
        self.uncompromised_sites = ['bank1', 'bank2', 'mail1', 'mail2', 'amazon', 'youtube']

        self.primitiveActions([('findUncompromisedSite', self.find_unc_site), ('directAttack', self.direct_attack),
                               ('chooseAttack', self.choose_attack), ('findCompromisedSite', self.find_compromised_site),
                               ('reusePassword', self.reuse_password)])
        #self.register()     # Register with the running password agent hub

        self.compromised_sites = []  # If a site is compromised, I guess we assume the attacker knows all user/pwd combos there
        self.failed = []

    # Decide which style of attack to try next. Binds the main variable to either _direct or _indirect
    def choose_attack(self, call):
        term = call[1]
        if term == "_direct":
            if not self.compromised_sites or random.random() < 0.5:
                return [{}]
            else:
                return []
        elif term == "_indirect":
            if self.compromised_sites and random.random() > 0.5:
                return [{}]
            else:
                return []
        elif isVar(term):
            if not self.compromised_sites:
                return [{term: '_direct'}] # Must choose direct if no sites are compromised yet
            elif random.random() < 0.5:   #
                return [{term: '_direct'}]
            else:
                return [{term: '_indirect'}]
        else:  # some constant that is not an attack style
            return []

    # Bind the site variable to a random possible site to attack.
    # Ultimately, get the names from the hub and keep track of those that have already been compromised
    # or where the agent has failed, and attack the rest.
    # For now, use an internal list of sites
    def find_unc_site(self, call):
        return bind_random_element(call, self.uncompromised_sites)

    def find_compromised_site(self, call):
        return bind_random_element(call, self.compromised_sites)

    def direct_attack(self, call):
        # For now, assume it succeeds and move the site into the success list
        site = call[1]
        self.uncompromised_sites.remove(site)
        self.compromised_sites.append(site)
        return [{}]   # Success with empty bindings

    def reuse_password(self, call):    # call is (reusePassword, comp, site)
        # Assume it succeeds
        site = call[2]
        self.uncompromised_sites.remove(site)
        self.compromised_sites.append(site)
        return [{}]


def bind_random_element(call, lis):
    site_var = call[1]
    if not lis:
        return []
    else:
        return [{site_var: lis[random.randint(0, len(lis)-1)]}]

if __name__ == "__main__":
    PasswordAgentAttacker().agentLoop()
