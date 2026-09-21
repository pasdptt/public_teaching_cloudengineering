"""docapp — the course application for Cloud Computing: Principles and Practice.

A small document/job-processing service. It starts fully local and synchronous and
acquires cloud behaviour one lab at a time:

    Lab 1  local disk, in-process state, synchronous processing
    Lab 3  object storage for documents, Firestore for job records
    Lab 4  containerised, deployed to managed execution
    Lab 5  a real queue between submission and processing

The seams that make that possible are the Protocol classes in ``storage``, ``jobstore``
and ``queue``. Each lab supplies a new implementation of one of them; no lab rewrites
the application.

Standard library only. That is a deliberate choice, not an oversight — see README.md.
"""

__version__ = "0.1.0"
