import gvars
import sge_tools as sge

PHASES = (
    'pre_clean', 'clean', 'post_clean',
    'pre_vlog', 'vlog', 'post_vlog',
    'pre_simulate', 'simulate', 'post_simulate',
    'final_cleanup'
    )

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
def set_schedule():
    "Ensure that all gadgets have a correct phase. Assign each to the Schedule in the place they should go."

    global Schedule

    for gadget in Gadgets:
        if gadget.schedule_phase == None:
            gvars.Log.critical("The gadget %s (%s) has no phase scheduled." % (gadget.name, str(type(gadget))))
        if gadget.schedule_phase not in PHASES:
            gvars.Log.critical("The gadget %s (%s) has an illegal schedule_phase of %s." % (gadget.name, str(type(gadget)), gadget.schedule_phase))
        Schedule[gadget.schedule_phase].append(gadget)
        gvars.Log.debug("Added gadget %s to %s" % (gadget.name, gadget.schedule_phase))

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
