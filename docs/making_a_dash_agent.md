# Making a DASH Agent
In this tutorial we will go over the structure of DASH agents so that you can create both your own agent or even extend or replace functionalities in the underlying DASH model itself.

## The structure of DASH
If you do not have a basic understanding of the DASH model, see some of the other documentation available. Here we will be focusing on how that model is expressed in Python. 

The default DASH model is a composite class that is made of several mixins and other classes. These are the components of DASH. DASH has several main components listed below:

1. `Client`: this component defines how DASH agents interact. The default client class used in DASH defines socket protocols that allow the agent to connect and disconnect to servers and send and receive actions from those servers.
2. `System1`: this component defines the framework for the "intuition" of the agent. The default system1 framework defines nodes and spreading activations on those nodes (for more information see DASH model documentation). The user will define at a high-level what those activation conditions are. `System1` provides a set of general methods like `system1_update` or `system1_propose_actions` that let system1 interact with the DASH agent. System1 modules should provide a way for a user to set rules for the system. Those rules will define the system's behavior for a given application.
3. `System2`: this component defines the framework for the "reasoning" portion of the agent. The default system2 allows the user to define high-level goals that the agent will try to satisfy.
4. `Action`: this component defines the agent update rules and the interaction between `System1` and `System2`. For example, the `agentLoop` method will repeatedly query system1 and system2 for actions until the maximum number of iterations is reached. The `choose_action`, `arbitrate_system1_system2`, and `bypass_system2` methods decide whether system1 or system2 actions are chosen. This class also defines a method for adding new primitive actions to the agent (`primitiveActions`).
5. `HumanTraits`: this component defines a set of properties that human agents tend to have. It also defines some methods for randomly generating agents with different personality profiles. This could be swapped out for a module that defines properties related to the type of agent it is supposed to be.

The base DASH agent inherits from one of each of these components to create a class with all of this functionality combined. The composite DASH agent class is defined like so:
 
 `DASHAgent(DASHAction, Client, System2Agent, System1Agent, HumanTraits)`
 
 Similarly, the other default class provided currently in Dash2 is the SocogDASHAgent, which replaces the system1 and action classes to support belief systems (see socog documentation for more details):
 
 `SocogDASHAgent(SocogDASHAction, Client, System2Agent, SocogSystem1Agent, HumanTraits)`
 
 Unless your application requires an overhaul of the DASH model, you will not need to modify these core classes. Instead, we suggest that you implement your agent as a mixin that overrides only those methods that you need. However, if it does become necessary, you can swap out mixins and classes to create a new type of base agent:
 
 ```python
class CompanyDASHAgent(DASHAction, Client, CompanySystem2Agent, System1Agent, CompanyTraits):
``` 
 
 ## Making a DASH Mixin 
 While `DASHAgent` and `SocogDASHAgent` provide the basis for a Dash model, you must develop a mixin that introduces the rules and primitive actions for your specific use case. Lets build our first Dash mixin.
 
 Suppose we want to model a human's interaction with the online forum Reddit. We would like to develop a Dash agent that can write and read posts on this forum, as well as reason about what it reads. First I will import the socog module and create an outline for my mixin:
 
```python
from Dash2.socog.socog_dash import SocogDASHAgent
from Dash2.core.dash import DASHAgent

# A mixin that defines the rules and attributes for a Redditor
class RedditMixin(object):
    def __init__(self):
        # ...redditor attributes
        
    # ...redditor primitive actions
```

Once I have defined my mixin, I can create an agent class that will inherit it and the core dash class, giving the final composite class the full functionality of Dash plus the specific actions I need for Reddit:

```python
# An agent with the default DASH capabilities
class RedditUser(RedditMixin, DASHAgent):
    pass

# An agent with a belief system
class SocogRedditUser(RedditMixin, SocogDASHAgent):
    pass
```

Using a mixin gives us the flexibility of adopting different core models without having to re-write our code for our Redditor. The mixin itself doesn't need to be instantiable, it can use methods that belong to the base `DASHAgent`. Only the final composite class (`RedditUser`) would be instantiated and used.

In cases where the mixin needs to use methods specific to one of the core agent classes, then you can create derived classes from the mixin and use those in the corresponding composite class. Doing this helps reduce code duplication and helps maintains flexibility in adopting different core models: 

```python
class SocogRedditMixin(RedditMixin):
    # ... add some special primitives

class RedditUser(RedditMixin, DASHAgent):
    pass

class SocogRedditUser(SocogRedditMixin, SocogDASHAgent):
    pass
```

For the remainder of this example I am going to use the `SocogDASHAgent` as a base, because I want to model the agent's belief network, which may change as they read posts on the forums. The full code for this agent can be found in `tutorial/reddit_user.py`. The mixin defined there specifies a series of system2 goals, system1 rules, and defines a set of primitive actions: 

```python
# We define our mixin
class RedditMixin(object):
    ...
    def __init__(self, **kwargs):
        ...
        self.id = self.register()[1]
        self.readAgent("...agent goals...")
        self.read_system1_rules("...sys1 rules...")
        self.primitiveActions([
            ('read_comment', self.read_comment),
            ('write_comment', self.write_comment),
            ('last_comment', self.last_comment),
            ('leave_thread', self.leave_thread)])
    
    # a method for each primitive action     
    def read_comment(self, (goal, belief)):
        ...
        
    ...
```

In this example, we use a method called `register` that belongs to the `SocogDASHAgent`. Using this method requires that the `Client` be initialized. Whenever an agent uses methods from the core model that require initialization, we can make sure to initialize the core model first in our composite class like so:

```python
# We define our composite class, the actual agent we will use
class RedditUser(RedditMixin, SocogDASHAgent):
    def __init__(self, **kwargs):
        SocogDASHAgent.__init__(self)
        # We initialize the mixin last
        RedditMixin.__init__(self, **kwargs)
```

If no such dependency exists, then it is fine to just write an empty class with `pass`. Lastly, we can create and run our agent:

```python
if __name__ == '__main__':
    # Instantiate our agent
    my_redditor = RedditUser()
    my_redditor.agentLoop(10)
```

Because the mixin is inherited first, it comes first in Python's method resolution order (MRO). Thus, we can use the mixin to override methods in either the `DASHAgent` or `SocogDASHAgent`. This can be useful if we want to change only one functionality of either base model, without rewriting or deriving from them. For instance, the `DASHAction` component defines a method `agentLoop` which I could override specifically for Reddit agents. Doing so would look like this:

```python
class RedditMixin(object):
    ...
    
    def agentLoop(self, max_iterations):
        ... new functionality here...
```

You can see and try out the Reddit agent by running both `tutorial/reddit_user.py` and `tutorial/reddit_hub.py`.