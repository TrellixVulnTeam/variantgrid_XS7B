#!/bin/bash

service gunicorn start
service celeryd_analysis_workers start
service celeryd_annotation_workers start
service celeryd_db_workers start
service celeryd_web_workers start
service celeryd_variant_id_single_worker start
service celeryd_scheduling_single_worker start
service celeryd_seqauto_single_worker start
service celeryd_beat start
