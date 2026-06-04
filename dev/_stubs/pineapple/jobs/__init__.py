"""Mock of pineapple.jobs — provides Job and a deterministic JobManager.

The real JobManager runs do_work() in a background thread. For predictable
off-device tests, this mock does NOT auto-run jobs: a job stays not-complete
until stop_job() is called (mirroring a long-running capture that runs until
stopped). Callbacks fire on stop.
"""
from typing import Callable, Dict, Generic, List, Optional, TypeVar
from uuid import uuid4

TResult = TypeVar('TResult')


class Job(Generic[TResult]):
    def __init__(self):
        self.is_complete: bool = False
        self.result: Optional[TResult] = None
        self.error: Optional[str] = None

    @property
    def was_successful(self) -> bool:
        return self.error is None and self.is_complete

    def do_work(self, logger):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()


class JobManager:
    def __init__(self, name: str, log_level: int = 0, module=None):
        self.name = name
        self.jobs: Dict[str, Job] = {}
        self._callbacks: Dict[str, List[Callable]] = {}
        if module is not None:
            module.register_action_handler('poll_job', self._poll_job)
            module.register_shutdown_handler(self._on_module_shutdown)

    def execute_job(self, job: Job, callbacks: List[Callable] = None) -> str:
        job_id = str(uuid4())
        job.is_complete = False
        self.jobs[job_id] = job
        self._callbacks[job_id] = callbacks or []
        return job_id

    def get_job(self, job_id: str, remove_if_complete: bool = True) -> Optional[Job]:
        job = self.jobs.get(job_id)
        if job and remove_if_complete and job.is_complete:
            self.remove_job(job_id)
        return job

    def remove_job(self, job_id: str):
        self.jobs.pop(job_id, None)
        self._callbacks.pop(job_id, None)

    def stop_job(self, job: Job = None, job_id: str = None):
        if not job and not job_id:
            raise Exception('A job or job_id is expected.')
        if not job:
            job = self.jobs.get(job_id)
        if isinstance(job, Job):
            try:
                job.stop()
            finally:
                job.is_complete = True
                for cb in self._callbacks.get(job_id, []):
                    cb(job)

    def _on_module_shutdown(self, signal):
        for jid in list(self.jobs):
            self.stop_job(job_id=jid)

    def _poll_job(self, request):
        job_id = request.__dict__.get('job_id')
        if not job_id:
            return 'job_id was not found in request.', False
        job = self.get_job(job_id, request.__dict__.get('remove_if_complete', True))
        if not job:
            return 'No job found by that id.', False
        return {'is_complete': job.is_complete, 'result': job.result, 'job_error': job.error}
