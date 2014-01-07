import gvars
import sge_tools as sge

MAIN_PHASES = ('clean', 'build', 'vlog', 'simulate', 'final_cleanup')

PHASES = []
for phase in MAIN_PHASES:
    PHASES.extend(['pre_%s' % phase, phase, 'post_%s' % phase])

# All of the gadgets that will be run
Gadgets = []

# The schedule that will be run. Populated by set_schedule
Schedule = {it:[] for it in PHASES}

# NOTE: Log = gvars.Log breaks if any tb.py add gadgets to the schedule, because they are imported before the Log is set up

########################################################################################
def add_gadget(gadget):
    "Add a gadget to the list of gadgets."

    # Todo: Just send in a type?

    global Gadgets
    gvars.Log.debug("Adding gadget: %s" % gadget.name)
    Gadgets.append(gadget)

########################################################################################
def set_schedule(phases_to_run):
    "Ensure that all gadgets have a correct phase. Assign each to the Schedule in the place they should go."

    global Schedule

    for gadget in Gadgets:
        if gadget.schedule_phase == None:
            gvars.Log.critical("The gadget %s (%s) has no phase scheduled." % (gadget.name, str(type(gadget))))
        if gadget.schedule_phase not in PHASES:
            gvars.Log.critical("The gadget %s (%s) has an illegal schedule_phase of %s." % (gadget.name, str(type(gadget)), gadget.schedule_phase))
        Schedule[gadget.schedule_phase].append(gadget)
        gvars.Log.debug("Added gadget %s to %s" % (gadget.name, gadget.schedule_phase))

    # clear out any added if the gadgets won't be run:
    for my_phase in MAIN_PHASES:
        if my_phase not in phases_to_run:
            clear_phase(['pre_%s' % my_phase, my_phase, 'post_%s' % my_phase])

########################################################################################
def run_schedule():
    for phase in PHASES:
        gvars.Log.debug("Entering phase.%s" % phase)
        if len(Schedule[phase]):
            # check each job's dependencies
            jobs = [it for it in Schedule[phase] if it.check_dependencies() == True]
            # set all of the command-lines for each of the jobs
            for job in jobs:
                # check each job's dependencies
                job.prepare()

            # if each job didn't fill out its command, or its doNotLaunch is set, 
            # then boot it (it will not run)
            jobs = [it for it in jobs if it.cmd and not it.doNotLaunch]
            if jobs:
                gvars.Log.debug("Running phase.%s (%d jobs to run)." % (phase, len(jobs)))
                sge.waitForSomeJobs(jobs, pollingMode=False)
                    
########################################################################################
def clear_phase(phase):
    """
    Remove all gadgets from the given phase(s).
    phase : (list of str, or str) Either a list of phases, or a phase as a string
    """

    def clear_it(my_phase):
        try:
            Schedule[my_phase] = []
        except KeyError:
            gvars.Log.critical("Unknown phase '%s'" % my_phase)

    if type(phase) == list:
        for a_phase in phase:
            clear_it(a_phase)
    elif type(phase) == str:
        clear_it(phase)

