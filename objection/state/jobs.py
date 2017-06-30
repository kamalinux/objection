import atexit

import click


class JobManagerState(object):
    """  A class representing the current Job manager. """

    def __init__(self) -> None:
        """
            Init a new job state manager. This method will also
            register an atexit(), ensiring that cleanup operations
            are performed on jobs when this class is GC'd.
        """

        self.jobs = []

        atexit.register(self.cleanup)

    def add_job(self, job) -> None:
        """
            Adds a job to the job state manager.

            :param job:
            :return:
        """

        self.jobs.append(job)

    def remove_job(self, job) -> None:
        """
            Removes a job from the job state manager.

            :param job:
            :return:
        """

        self.jobs.remove(job)

    def cleanup(self) -> None:
        """
            Clean up all of the job in the job manager.

            This method is typicall called when at the end of an
            objection session.

            :return:
        """

        for job in self.jobs:
            click.secho('[job manager] Ending job: {0}'.format(job.id), dim=True)
            job.end()


job_manager_state = JobManagerState()
