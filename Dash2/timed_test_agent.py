from dash import DASHAgent
import random
import math

class TimedTestAgent(DASHAgent):

    time = 0
    eat_state = 0

    def __init__(self):
        DASHAgent.__init__(self)

        self.register()

        self.readAgent("""

goalWeight doWork 1

goalRequirements doWork
    wake_up_wrapper(placeholder)
    run_wrapper(placeholder)
    eat_breakfast_wrapper(breakfast)
    eat_lunch_wrapper(lunch)
    eat_dinner_wrapper(dinner)
    sleep_wrapper(placeholder)
    forget([wake_up_wrapper(x), run_wrapper(x), eat_breakfast_wrapper(x), eat_lunch_wrapper(x), eat_dinner_wrapper(x), sleep_wrapper(x)])

transient doWork
    """)

        self.primitiveActions([
                ('wake_up_wrapper', self.wake_up),
                ('run_wrapper', self.run),
                ('eat_breakfast_wrapper', self.eat_breakfast),
                ('eat_lunch_wrapper', self.eat_lunch),
                ('eat_dinner_wrapper', self.eat_dinner),
                ('sleep_wrapper', self.sleep)
                ])

    def wake_up(self, ph):
        wake_up_time = 24 * math.floor((self.time+2)/24) + 6
        print "woke up..."
        self.sendAction("wake_up", [wake_up_time])
        self.time = wake_up_time
        return [{ph: "hello"}]

    def run(self, ph):
        run_time = 24 * math.floor(self.time/24) + 7
        print "running..."
        self.sendAction("run", [run_time])
        self.time = run_time
        return [{ph: "hello"}]

    def eat_breakfast(self, ph):
        eat_time = self.time + random.randint(1,3)
        print "eating breakfast..."
        self.sendAction("eat_breakfast", [eat_time])
        self.time = eat_time
        return [{ph: "hello"}]

    def eat_lunch(self, ph):
        eat_time = self.time + random.randint(2,4)
        print "eating lunch..."
        self.sendAction("eat_lunch", [eat_time])
        self.time = eat_time
        return [{ph: "hello"}]

    def eat_dinner(self, ph):
        eat_time = self.time + random.randint(3,6)
        print "eating dinner..."
        self.sendAction("eat_dinner", [eat_time])
        self.time = eat_time
        return [{ph: "hello"}]

    def sleep(self, ph):
        sleep_time = 24 * math.floor(self.time/24) + 22
        print "sleeping..."
        self.sendAction("sleep", [sleep_time])
        self.time = sleep_time
        return [{ph: "hello"}]

if __name__ == '__main__':
    TimedTestAgent().agentLoop(100)
