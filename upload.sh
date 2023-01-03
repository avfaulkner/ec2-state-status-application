#! /bin/bash
aws s3 cp templates/dashboard.html  s3://portal-af/templates/
aws s3 cp aws_functions.py  s3://portal-af
aws s3 cp app.py  s3://portal-af