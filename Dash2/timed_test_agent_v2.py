from dash import DASHAgent
import random
import math

class TimedTestAgent(DASHAgent):

    time = 0
    eat_state = 0
    is_first_day = True

    def __init__(self):
        DASHAgent.__init__(self)

        #  self.traceGoals = True
        self.register()

        self.readAgent("""

goalWeight doWork 1

goalRequirements doWork
    wakeUp(placeholder)
    run(placeholder)
    eat(meal)
    forget([eat(x)])
    sleep(placeholder)
    forget([wakeUp(x), run(x), sleep(x)])

goalRequirements doWork
    wakeUp(placeholder)
    run(placeholder)
    sleep(placeholder)
    forget([wakeUp(x), run(x), eat(x), sleep(x)])

transient doWork
    """)

        self.primitiveActions([
                ('wakeUp', self.wake_up),
                ('run', self.run),
                ('eat', self.eat),
                ('sleep', self.sleep)
                ])

    def wake_up(self, (goal, ph)):
        if self.is_first_day:
            wake_up_time = "asap"
        else:
            wake_up_time = 24 * math.floor((self.time+2)/24) + 6
            self.is_first_day = False
            self.time = wake_up_time
        print "woke up..."
        self.sendAction(goal, [], wake_up_time)
        return [{}]

    def run(self, (goal, ph)):
        run_time = 24 * math.floor(self.time/24) + 7
        print "running..."
        self.sendAction(goal, [], run_time)
        self.time = run_time
        self.eat_state = 0
        return [{}]

    def eat(self, (goal, meal_var)):
        if self.eat_state == 0:
            curr_meal = "breakfast"
            self.eat_state = 1
            eat_time = 24 * math.floor(self.time/24) + random.randint(8,9)
        elif self.eat_state == 1:
            curr_meal = "lunch"
            self.eat_state = 2
            eat_time = 24 * math.floor(self.time/24) + random.randint(11,14)
        elif self.eat_state == 2:
            curr_meal = "dinner"
            self.eat_state = 3
            eat_time = 24 * math.floor(self.time/24) + random.randint(18, 20)
        else:
            print "eat primitive action: no more meals - failing..."
            return None

        print "eating...", goal, meal_var
        self.sendAction(goal + "(" + curr_meal + ")", [], eat_time)
        self.time = eat_time
        return [{meal_var: curr_meal}]

    def sleep(self, (goal, ph)):
        sleep_time = 24 * math.floor(self.time/24) + 22
        print "sleeping..."
        self.sendAction(goal, [], sleep_time)
        self.time = sleep_time
        return [{}]

if __name__ == '__main__':
    TimedTestAgent().agentLoop(20)
