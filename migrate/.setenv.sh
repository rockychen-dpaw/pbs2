#!/bin/bash

sourcehost="127.0.0.1"
sourceport=5432
sourcedatabase="pbs_prod"
sourceschema="public"
sourceuser=""
sourcepassword=""

targethost="127.0.0.1"
targetport=5432
targetdatabase="pbs2"
targetschema="public"
targetuser=""
targetpassword=""


step1_excluded_tables=(django_  celery_ djcelery_ djkombu_ guardian_ restless_ reversion_ south_ tastypie_ spatial_ref_sys)
#step1_included_tables=(django_admin_log)
step1_include_schema_tables=(review_annualindicativeburnprogram)
